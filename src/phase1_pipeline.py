"""Deterministic Phase 1 corpus engineering pipeline.

Reads the three raw CSVs, preserves source fields, and writes derived artifacts
under Data/derived_phase1. It never edits raw or existing processed files.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "Data" / "raw"
DEFAULT_OUTPUT = ROOT / "Data" / "derived_phase1"
DEFAULT_REVIEWED = ROOT / "Data" / "processed" / "annotation_work" / "manual_adjudication_workbook.csv"
DATASETS = {
    "youtube": "youtube_data set.csv",
    "reddit": "reddit_dataSet.csv",
    "twitter": "twitter_data set.csv",
}
REQUIRED = {"record_id", "post_text", "platform", "timestamp", "anonymized_user_id", "is_synthetic", "parent_record_id", "aug_method"}
LEGACY_COLUMNS = ["tier", "tier_lexicon", "tier_corrected", "tier_model", "tier_pred", "tier_source", "tier_confidence", "lex_conf", "lex_hits", "corr_conf", "model_conf", "model_accept", "prob_tier_0", "prob_tier_1", "prob_tier_2", "prob_tier_3", "split", "model_split"]
APPROVED_LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
APPROVED_CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}

def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]

def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    return re.sub(r"\s+", " ", value).strip().casefold()

def read_csv_strict(path: Path) -> tuple[str, list[str], list[dict[str, str]]]:
    errors = []
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                fields = reader.fieldnames or []
                rows = list(reader)
            if not REQUIRED <= set(fields):
                raise ValueError(f"missing required columns: {sorted(REQUIRED - set(fields))}")
            return encoding, fields, rows
        except (UnicodeDecodeError, csv.Error, ValueError) as exc:
            errors.append(f"{encoding}: {exc}")
    raise RuntimeError(f"Unable to load {path}: {'; '.join(errors)}")

def synthetic_status(row: dict[str, str]) -> str:
    method = (row.get("aug_method", "") or "").strip().casefold()
    flag = (row.get("is_synthetic", "") or "").strip().casefold()
    if flag in {"true", "1", "yes"} or row.get("parent_record_id", "").strip() or method not in {"", "original", "none", "false"}:
        return "synthetic_or_augmented"
    return "original_or_unspecified"

def valid_review_label(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    parts = value.split("|")
    if value == "none_other":
        return True
    return len(parts) == len(set(parts)) and "none_other" not in parts and set(parts) <= APPROVED_LABELS and parts == [x for x in ("distress_negative_affect", "mental_health_reference_or_support", "self_harm_related") if x in parts]

def load_reviewed(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Reviewed workbook not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, strict=True))
    required = {"record_id", "platform", "post_text", "final_adjudicated_label", "final_context_flags", "adjudication_status"}
    if not rows or not required <= set(rows[0]):
        raise RuntimeError("Reviewed workbook does not contain the required final-label columns")
    result = {}
    for row in rows:
        rid = row["record_id"].strip()
        if not rid or rid in result:
            raise RuntimeError(f"Duplicate or blank reviewed record_id: {rid!r}")
        if row["adjudication_status"].strip().casefold() != "completed" or not valid_review_label(row["final_adjudicated_label"]):
            raise RuntimeError(f"Reviewed row is not completed/policy-valid: {rid}")
        result[rid] = row
    return result

def run(raw_dir: Path = DEFAULT_RAW, output_dir: Path = DEFAULT_OUTPUT, reviewed_path: Path = DEFAULT_REVIEWED, near_threshold: float = 0.95) -> dict:
    output_dir.mkdir(parents=True, exist_ok=False) if not output_dir.exists() else None
    log_path = output_dir / "pipeline.log.jsonl"
    logger = logging.getLogger("phase1")
    logger.handlers.clear(); logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path, encoding="utf-8"); handler.setFormatter(logging.Formatter("%(message)s")); logger.addHandler(handler)
    reviewed = load_reviewed(reviewed_path)
    records = []; schema = {}; dataset_metrics = []
    for platform, filename in DATASETS.items():
        path = raw_dir / filename
        if not path.exists(): raise FileNotFoundError(path)
        encoding, fields, rows = read_csv_strict(path)
        schema[platform] = fields
        ids = Counter(); full_rows = Counter(); text_counts = Counter()
        for number, row in enumerate(rows, start=2):
            rid = row.get("record_id", "").strip(); ids[rid] += 1; full_rows[tuple(row.get(f, "") for f in fields)] += 1
            norm = normalize_text(row.get("post_text", "")); text_counts[norm] += 1
            records.append({"platform": platform, "source_file": filename, "source_row_number": number, "source_encoding": encoding, "fields": fields, "row": row, "norm": norm, "rid": rid})
        dataset_metrics.append({"platform": platform, "source_file": filename, "encoding": encoding, "rows": len(rows), "columns": len(fields), "missing_record_id": sum(not x for x in ids), "duplicate_record_id_extra": sum(n-1 for k,n in ids.items() if k and n > 1), "empty_text": sum(not normalize_text(r.get("post_text", "")) for r in rows), "exact_duplicate_rows_extra": sum(n-1 for n in full_rows.values() if n > 1), "normalized_duplicate_text_extra": sum(n-1 for n in text_counts.values() if n and n > 1), "synthetic_or_augmented": sum(synthetic_status(r) == "synthetic_or_augmented" for r in rows)})
    all_fields = list(dict.fromkeys(f for p in DATASETS for f in schema[p]))
    text_groups = defaultdict(list); id_counts = Counter(); parent_groups = defaultdict(list)
    for item in records:
        text_groups[sha(item["norm"])].append(item) if item["norm"] else None
        id_counts[item["rid"]] += 1
        parent = item["row"].get("parent_record_id", "").strip()
        if parent: parent_groups[parent].append(item)
    exact_groups = {h: group for h, group in text_groups.items() if len(group) > 1}
    near = []; buckets = defaultdict(list)
    for item in records:
        if item["norm"]: buckets[(item["norm"][:32], len(item["norm"]) // 25)].append(item)
    seen = set()
    for bucket in buckets.values():
        for i, left in enumerate(bucket):
            for right in bucket[i+1:]:
                if left["norm"] == right["norm"]: continue
                if abs(len(left["norm"]) - len(right["norm"])) / max(len(left["norm"]), len(right["norm"]), 1) > 0.15: continue
                score = SequenceMatcher(None, left["norm"], right["norm"]).ratio()
                pair = tuple(sorted((left["rid"], right["rid"])))
                if score >= near_threshold and pair not in seen:
                    seen.add(pair); near.append({"platform_a": left["platform"], "platform_b": right["platform"], "record_id_hash_a": sha(pair[0]), "record_id_hash_b": sha(pair[1]), "text_hash_a": sha(left["norm"]), "text_hash_b": sha(right["norm"]), "similarity": f"{score:.4f}", "reason": "conservative near-duplicate candidate; manual review required"})
    reviewed_joined = 0; join_errors = []
    output_fields = all_fields + ["source_file", "source_row_number", "source_encoding", "stable_record_key", "normalized_text_hash", "exact_text_group_hash", "synthetic_status", "reviewed_label", "reviewed_context_flags", "reviewed_join_status"]
    with (output_dir / "canonical_corpus.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=output_fields, extrasaction="ignore"); writer.writeheader()
        for item in records:
            row = dict(item["row"]); rid = item["rid"]; review = reviewed.get(rid)
            if review:
                if review["platform"].strip().casefold() != item["platform"] or review["post_text"] != item["row"].get("post_text", ""):
                    join_errors.append(rid)
                else: reviewed_joined += 1
            row.update({"source_file": item["source_file"], "source_row_number": item["source_row_number"], "source_encoding": item["source_encoding"], "stable_record_key": f"{item['platform']}:{rid}", "normalized_text_hash": sha(item["norm"]) if item["norm"] else "", "exact_text_group_hash": sha(item["norm"]) if item["norm"] and sha(item["norm"]) in exact_groups else "", "synthetic_status": synthetic_status(item["row"]), "reviewed_label": review["final_adjudicated_label"] if review and rid not in join_errors else "", "reviewed_context_flags": review["final_context_flags"] if review and rid not in join_errors else "", "reviewed_join_status": "matched_validated" if review and rid not in join_errors else "unreviewed"})
            writer.writerow(row)
    if join_errors: raise RuntimeError(f"Reviewed-label text/platform mismatch for {len(join_errors)} IDs; canonical file was written but reviewed fields were left blank for those IDs")
    with (output_dir / "duplicate_review_candidates.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(near[0]) if near else ["platform_a", "platform_b", "record_id_hash_a", "record_id_hash_b", "text_hash_a", "text_hash_b", "similarity", "reason"]); writer.writeheader(); writer.writerows(near)
    data_dictionary = []
    for field in output_fields:
        origin = "raw source" if field in all_fields else "pipeline-derived"
        role = "legacy metadata; not ground truth" if field in LEGACY_COLUMNS else ("reviewed human label; only 60 matched rows" if field == "reviewed_label" else "source/provenance or derived audit field")
        data_dictionary.append({"column": field, "origin": origin, "role": role, "provenance_status": "unknown legacy provenance" if field in LEGACY_COLUMNS else "documented"})
    with (output_dir / "data_dictionary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data_dictionary[0])); writer.writeheader(); writer.writerows(data_dictionary)
    quality = {"row_count": len(records), "platform_counts": Counter(x["platform"] for x in records), "dataset_metrics": dataset_metrics, "combined_duplicate_record_id_extra": sum(n-1 for k,n in id_counts.items() if k and n > 1), "exact_text_groups": len(exact_groups), "exact_text_records": sum(len(g) for g in exact_groups.values()), "near_duplicate_candidates": len(near), "parent_groups": len(parent_groups), "reviewed_rows_available": len(reviewed), "reviewed_rows_joined": reviewed_joined, "unreviewed_rows": len(records)-reviewed_joined, "reviewed_join_errors": len(join_errors), "legacy_columns": [c for c in LEGACY_COLUMNS if c in all_fields], "raw_files_unchanged": True}
    with (output_dir / "quality_summary.json").open("w", encoding="utf-8") as handle: json.dump(quality, handle, indent=2, default=dict)
    logger.info(json.dumps({"event": "pipeline_complete", "rows": len(records), "reviewed_joined": reviewed_joined, "near_candidates": len(near)}))
    handler.close()
    return quality

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--reviewed-workbook", type=Path, default=DEFAULT_REVIEWED)
    parser.add_argument("--near-threshold", type=float, default=0.95)
    args = parser.parse_args(argv)
    try:
        quality = run(args.raw_dir, args.output_dir, args.reviewed_workbook, args.near_threshold)
        print(json.dumps(quality, indent=2, default=dict)); return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr); return 1

if __name__ == "__main__": raise SystemExit(main())
