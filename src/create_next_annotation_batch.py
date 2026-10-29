"""Create a new blank, two-annotator batch without using legacy labels."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Data" / "raw"
OUT = ROOT / "Data" / "processed" / "annotation_batch_v1"
SEED = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
DATASETS = {"youtube": "youtube_data set.csv", "reddit": "reddit_dataSet.csv", "twitter": "twitter_data set.csv"}
RANDOM_SEED = 20261028
PER_PLATFORM = 20

TEMPLATE_FIELDS = ["record_id", "stable_record_key", "platform", "post_text", "duplicate_group_hash", "source_text_review_required", "annotator_id", "proposed_label", "context_flags", "confidence", "rationale", "annotation_status", "needs_review", "review_notes"]


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value or "")).strip().casefold()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:24]


def read_csv(path: Path, encoding: str) -> list[dict[str, str]]:
    with path.open(encoding=encoding, newline="") as handle:
        return list(csv.DictReader(handle))


def load_source(path: Path) -> list[dict[str, str]]:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return read_csv(path, encoding)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Unable to decode source file: {path}")


def existing_batch_ids(output: Path) -> set[str]:
    ids = {row["record_id"].strip() for row in read_csv(SEED, "utf-8-sig")}
    for manifest_path in (ROOT / "Data" / "processed").glob("annotation_batch*/batch_manifest.csv"):
        if manifest_path.parent.resolve() == output.resolve():
            continue
        ids.update(row.get("record_id", "").strip() for row in read_csv(manifest_path, "utf-8-sig") if row.get("record_id", "").strip())
    return ids


def synthetic(row: dict[str, str]) -> bool:
    return (row.get("is_synthetic", "").strip().casefold() in {"true", "1", "yes"} or bool(row.get("parent_record_id", "").strip()) or row.get("aug_method", "").strip().casefold() not in {"", "original", "none", "false"})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--per-platform", type=int, default=PER_PLATFORM)
    args = parser.parse_args(argv)
    output = args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing batch directory: {output}")
    if args.per_platform < 1:
        raise ValueError("--per-platform must be positive")
    prior_ids = existing_batch_ids(output)
    all_rows: list[dict[str, str]] = []
    source_counts = {}
    excluded_counts = {}
    for platform, filename in DATASETS.items():
        rows = load_source(RAW / filename)
        source_counts[platform] = len(rows)
        excluded = {"synthetic_or_augmented": 0, "prior_pilot_or_batch_record": 0, "missing_id_or_text": 0}
        eligible = []
        for index, row in enumerate(rows, start=2):
            rid = row.get("record_id", "").strip(); text = row.get("post_text", "")
            if synthetic(row): excluded["synthetic_or_augmented"] += 1; continue
            if rid in prior_ids: excluded["prior_pilot_or_batch_record"] += 1; continue
            if not rid or not normalize(text): excluded["missing_id_or_text"] += 1; continue
            eligible.append({"record_id": rid, "platform": platform, "post_text": text, "source_file": filename, "source_row_number": str(index), "source_text_review_required": "FALSE", "normalized_text_hash": digest(normalize(text))})
        if len(eligible) < args.per_platform:
            raise RuntimeError(f"Not enough eligible {platform} rows: {len(eligible)} available, {args.per_platform} required")
        random.Random(args.seed + sum(ord(char) for char in platform)).shuffle(eligible)
        all_rows.extend(eligible[:args.per_platform])
        excluded_counts[platform] = excluded
    selected_hash_counts = {}
    for row in all_rows:
        selected_hash_counts[row["normalized_text_hash"]] = selected_hash_counts.get(row["normalized_text_hash"], 0) + 1
    for row in all_rows:
        row["duplicate_group_hash"] = row["normalized_text_hash"] if selected_hash_counts[row["normalized_text_hash"]] > 1 else ""
    output.mkdir(parents=True)
    manifest_fields = ["record_id", "stable_record_key", "platform", "source_file", "source_row_number", "duplicate_group_hash", "source_text_review_required"]
    with (output / "batch_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields); writer.writeheader()
        writer.writerows({field: (f"{row['platform']}:{row['record_id']}" if field == "stable_record_key" else row.get(field, "")) for field in manifest_fields} for row in all_rows)
    for annotator in ("A1", "A2"):
        with (output / f"{annotator}_annotation.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=TEMPLATE_FIELDS); writer.writeheader()
            for row in all_rows:
                writer.writerow({"record_id": row["record_id"], "stable_record_key": f"{row['platform']}:{row['record_id']}", "platform": row["platform"], "post_text": row["post_text"], "duplicate_group_hash": row["duplicate_group_hash"], "source_text_review_required": row["source_text_review_required"], "annotator_id": annotator, "proposed_label": "", "context_flags": "", "confidence": "", "rationale": "", "annotation_status": "not_started", "needs_review": "", "review_notes": ""})
    mismatch_rows = [{"record_id": rid, "prior_pilot_platform": "", "A1_text_mismatch": "TRUE", "A2_text_mismatch": "TRUE", "decision": "", "review_notes": ""} for rid in sorted(prior_ids)]
    mismatch_ids = {"95728c25-80b6-41e9-ad4c-f8566d580284", "d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e"}
    with (output / "prior_text_mismatch_review.csv").open("w", encoding="utf-8", newline="") as handle:
        fields = ["record_id", "A1_text_mismatch", "A2_text_mismatch", "decision", "review_notes"]; writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows({"record_id": rid, "A1_text_mismatch": "TRUE", "A2_text_mismatch": "TRUE", "decision": "", "review_notes": ""} for rid in sorted(mismatch_ids))
    source_hash_path = ROOT / "Data" / "derived_phase1" / "quality_summary.json"
    source_hash = digest(source_hash_path.read_text(encoding="utf-8")) if source_hash_path.exists() else "unavailable"
    metadata = {"batch_version": output.name, "seed": args.seed, "per_platform": args.per_platform, "total_records": len(all_rows), "platform_counts": {platform: sum(row["platform"] == platform for row in all_rows) for platform in DATASETS}, "selection_method": "deterministic platform-stratified random sample using record eligibility only; legacy labels, keywords, predictions, probabilities, and confidence fields were not read", "excluded_existing_pilot_and_batch_ids": len(prior_ids), "excluded_counts": excluded_counts, "synthetic_policy": "explicitly synthetic/augmented records excluded from primary batch", "prior_mismatch_review_items": sorted(mismatch_ids), "source_quality_summary_sha256_prefix": source_hash, "raw_files_modified": False}
    (output / "batch_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
