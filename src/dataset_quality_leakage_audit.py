"""Read-only quality, duplication, and leakage audit for the three raw datasets."""
from __future__ import annotations

import csv
import hashlib
import re
from datetime import datetime
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Data" / "raw"
PROCESSED = ROOT / "Data" / "processed"
REPORTS = ROOT / "reports"
REPORT = REPORTS / "dataset_quality_and_leakage_audit.md"
METRICS = REPORTS / "dataset_quality_metrics.csv"
CANDIDATES = REPORTS / "duplicate_review_candidates.csv"
FILES = {
    "youtube": RAW / "youtube_data set.csv",
    "reddit": RAW / "reddit_dataSet.csv",
    "twitter": RAW / "twitter_data set.csv",
}

def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()[:16]

def norm_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "")
    value = re.sub(r"\s+", " ", value).strip().casefold()
    return value

def load(path: Path):
    errors = []
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                reader = csv.DictReader(handle, strict=True)
                rows = list(reader)
            return encoding, reader.fieldnames or [], rows, errors
        except (UnicodeDecodeError, csv.Error) as exc:
            errors.append(f"{encoding}: {type(exc).__name__}: {exc}")
    raise RuntimeError(f"Could not parse {path}: {'; '.join(errors)}")

def safe_bool(value: str) -> bool:
    return (value or "").strip().casefold() in {"true", "1", "yes"}

def is_synthetic(row: dict[str, str]) -> bool:
    method = (row.get("aug_method", "") or "").strip().casefold()
    return safe_bool(row.get("is_synthetic", "")) or bool(row.get("parent_record_id", "").strip()) or method not in {"", "original", "none", "false"}

def timestamp_valid(value: str) -> bool:
    value = (value or "").strip()
    if not value:
        return True
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def main() -> None:
    datasets = {}
    metric_rows = []
    all_records = []
    for platform, path in FILES.items():
        if not path.exists():
            raise FileNotFoundError(path)
        encoding, columns, rows, parse_attempts = load(path)
        datasets[platform] = {"path": path, "encoding": encoding, "columns": columns, "rows": rows, "parse_attempts": parse_attempts}
        full_keys = Counter(tuple(row.get(c, "") for c in columns) for row in rows)
        text_keys = Counter(norm_text(row.get("post_text", "")) for row in rows if norm_text(row.get("post_text", "")))
        ids = [row.get("record_id", "") for row in rows]
        users = [row.get("anonymized_user_id", "") for row in rows]
        timestamps = [row.get("timestamp", "") for row in rows]
        for field, values in [("record_id", ids), ("anonymized_user_id", users), ("timestamp", timestamps)]:
            metric_rows.append({"platform": platform, "metric": f"missing_{field}", "value": sum(not v.strip() for v in values), "detail": "count"})
        metric_rows += [
            {"platform": platform, "metric": "row_count", "value": len(rows), "detail": "exact"},
            {"platform": platform, "metric": "column_count", "value": len(columns), "detail": "exact"},
            {"platform": platform, "metric": "exact_duplicate_rows_extra", "value": sum(n-1 for n in full_keys.values() if n > 1), "detail": "full row duplicates beyond first"},
            {"platform": platform, "metric": "duplicate_record_ids_extra", "value": sum(n-1 for n in Counter(x for x in ids if x).values() if n > 1), "detail": "record_id duplicates beyond first"},
            {"platform": platform, "metric": "duplicate_normalized_text_extra", "value": sum(n-1 for n in text_keys.values() if n > 1), "detail": "normalized post_text duplicates beyond first"},
            {"platform": platform, "metric": "empty_post_text", "value": sum(not row.get("post_text", "").strip() for row in rows), "detail": "blank or whitespace-only"},
            {"platform": platform, "metric": "invalid_timestamp", "value": sum(not timestamp_valid(row.get("timestamp", "")) for row in rows), "detail": "non-empty timestamp not parsed by ISO parser"},
            {"platform": platform, "metric": "synthetic_or_augmented", "value": sum(is_synthetic(row) for row in rows), "detail": "is_synthetic=true, non-original aug_method, or parent_record_id"},
            {"platform": platform, "metric": "explicit_is_synthetic_true", "value": sum(safe_bool(row.get("is_synthetic", "")) for row in rows), "detail": "source flag"},
        ]
        all_records.extend({"platform": platform, "row": row, "text": norm_text(row.get("post_text", ""))} for row in rows)
    # Cross-platform and within-platform exact normalized text groups.
    text_groups = defaultdict(list)
    for item in all_records:
        if item["text"]:
            text_groups[digest(item["text"])].append(item)
    exact_groups = [group for group in text_groups.values() if len(group) > 1]
    cross_groups = [group for group in exact_groups if len({x["platform"] for x in group}) > 1]
    metric_rows += [
        {"platform": "combined", "metric": "row_count", "value": len(all_records), "detail": "exact"},
        {"platform": "combined", "metric": "column_count_common", "value": len(set.intersection(*(set(d["columns"]) for d in datasets.values())),), "detail": "columns common to all three"},
        {"platform": "combined", "metric": "unique_record_ids", "value": len({x["row"].get("record_id", "") for x in all_records if x["row"].get("record_id", "").strip()}), "detail": "non-empty IDs"},
        {"platform": "combined", "metric": "cross_platform_exact_text_groups", "value": len(cross_groups), "detail": "normalized text hash groups"},
        {"platform": "combined", "metric": "cross_platform_exact_text_records", "value": sum(len(g) for g in cross_groups), "detail": "records in those groups"},
    ]
    user_by_platform = {p: {r.get("anonymized_user_id", "").strip() for r in d["rows"] if r.get("anonymized_user_id", "").strip()} for p, d in datasets.items()}
    all_users = set().union(*user_by_platform.values())
    cross_users = set.intersection(*user_by_platform.values()) if user_by_platform else set()
    metric_rows += [
        {"platform": "combined", "metric": "unique_nonempty_anonymized_users", "value": len(all_users), "detail": "identifier count; values not printed"},
        {"platform": "combined", "metric": "users_present_on_all_three_platforms", "value": len(cross_users), "detail": "identifier count; values not printed"},
    ]
    # Conservative near-duplicate review candidates; no raw text is written.
    near = []
    buckets = defaultdict(list)
    for item in all_records:
        if item["text"]:
            key = (item["text"][:32], len(item["text"]) // 25)
            buckets[key].append(item)
    seen = set()
    for bucket in buckets.values():
        for i, left in enumerate(bucket):
            for right in bucket[i+1:]:
                if left["text"] == right["text"]: continue
                if abs(len(left["text"]) - len(right["text"])) / max(len(left["text"]), len(right["text"]), 1) > 0.15: continue
                score = SequenceMatcher(None, left["text"], right["text"]).ratio()
                if score >= 0.95:
                    pair = tuple(sorted((left["row"].get("record_id", ""), right["row"].get("record_id", ""))))
                    if pair not in seen:
                        seen.add(pair); near.append({"platform_a": left["platform"], "platform_b": right["platform"], "record_id_hash_a": digest(pair[0]), "record_id_hash_b": digest(pair[1]), "text_hash_a": digest(left["text"]), "text_hash_b": digest(right["text"]), "similarity": f"{score:.4f}", "review_reason": "near-duplicate candidate; inspect locally without automatic removal"})
    if near:
        with CANDIDATES.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(near[0])); writer.writeheader(); writer.writerows(near)
    elif CANDIDATES.exists():
        CANDIDATES.unlink()
    # Label/leakage inventory.
    label_columns = ["tier", "tier_lexicon", "tier_corrected", "tier_model", "tier_pred", "tier_source", "tier_confidence", "lex_conf", "lex_hits", "corr_conf", "model_conf", "model_accept", "prob_tier_0", "prob_tier_1", "prob_tier_2", "prob_tier_3", "split", "model_split", "is_synthetic", "aug_method", "parent_record_id"]
    common = set.intersection(*(set(d["columns"]) for d in datasets.values()))
    for col in label_columns:
        if col in common:
            metric_rows.append({"platform": "combined", "metric": f"column_present_{col}", "value": 1, "detail": "legacy/metadata; not human target"})
    with METRICS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["platform", "metric", "value", "detail"]); writer.writeheader(); writer.writerows(metric_rows)
    synthetic = {p: sum(is_synthetic(r) for r in d["rows"]) for p,d in datasets.items()}
    common_cols = sorted(set.intersection(*(set(d["columns"]) for d in datasets.values())))
    lines = ["# Dataset Quality and Leakage Audit", "", "## Scope and safety", "", "Audited the three current raw CSV files only. Raw data was read without modification; no labels were assigned, rows deleted, splits changed, or model trained. Reports use hashes/counts rather than raw post text or user identifiers. Labels are non-clinical text-signal annotations, not diagnoses.", "", "## Current files and counts", "", "| Platform | File | Encoding | Rows | Columns |", "|---|---|---|---:|---:|"]
    for p,d in datasets.items(): lines.append(f"| {p} | `{d['path'].relative_to(ROOT)}` | {d['encoding']} | {len(d['rows'])} | {len(d['columns'])} |")
    lines += [f"| combined | three files | — | **{len(all_records)}** | common columns: {len(common_cols)} |", "", "The combined row count is a count of rows, not a license to concatenate them for modeling; platform and provenance must remain explicit.", "", "## Quality findings", "", "The machine-readable metrics file contains exact counts for missing IDs/text, duplicates, synthetic metadata, and column presence.", ""]
    for p,d in datasets.items():
        rows=d["rows"]; lines.append(f"### {p}"); lines.append(f"- Missing record IDs: {sum(not r.get('record_id','').strip() for r in rows)}; missing text: {sum(not r.get('post_text','').strip() for r in rows)}.")
        lines.append(f"- Synthetic/augmented indicators: **{synthetic[p]}** rows (explicit `is_synthetic`, `parent_record_id`, or `aug_method` evidence).")
        lines.append(f"- Exact duplicate full rows: {sum(n-1 for n in Counter(tuple(r.get(c,'') for c in d['columns']) for r in rows).values() if n>1)} extra rows; duplicate record IDs: {sum(n-1 for n in Counter(r.get('record_id','') for r in rows if r.get('record_id','')).values() if n>1)} extra rows.")
    lines += ["", "## Exact and near-duplicate text", "", f"- Normalized exact-text groups across the combined data: **{len(exact_groups)}** groups with more than one record.", f"- Cross-platform normalized exact-text groups: **{len(cross_groups)}** groups involving {sum(len(g) for g in cross_groups)} records.", f"- Conservative near-duplicate candidates found: **{len(near)}**. Candidates are in `{CANDIDATES.relative_to(ROOT)}` when non-empty; only hashes/IDs are stored.", "- Duplicate records were not removed. Parent/augmented relationships and duplicate groups must be kept together or explicitly controlled in later evaluation.", "", "## Labels and target leakage", "", "The raw datasets contain legacy tier, lexicon, correction, model, confidence/probability, split, and augmentation columns. These are metadata or generated signals, not verified ground truth. The approved human-reviewed labels are stored separately in the 60-record adjudication workbook; they are not present as a raw-dataset target column.", "", "Potential target leakage if used as features: `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, `tier_source`, `tier_confidence`, `lex_conf`, `lex_hits`, `corr_conf`, `model_conf`, `model_accept`, `prob_tier_0`–`prob_tier_3`, and any derived text/model fields such as `text_muril`, `text_negation`, or `ruminative_repetition` if they were generated using labels or post-hoc model outputs. `split` and `model_split` are not safe evaluation partitions because their provenance is unresolved and prior audits found disagreement.", "", "## Grouping and evaluation risks", "", "- `anonymized_user_id`, `record_id`, `parent_id`, `parent_record_id`, timestamps, platform, and augmentation metadata are available in the schemas and require explicit grouping/time policies.", f"- The audit found {len(all_users)} unique non-empty anonymized-user identifiers across the combined files; {len(cross_users)} identifiers occur on all three platforms. Values are intentionally not printed.", "- User overlap, duplicate text, cross-platform copies, and synthetic-parent relationships can leak information across train and evaluation sets.", "- Do not expose user IDs in reports; use them only locally for grouping diagnostics.", "", "## Annotation coverage and pilot sufficiency", "", f"The current human-reviewed pilot covers 60 records out of **{len(all_records)}** raw records ({100*60/len(all_records):.2f}%). The latest validation reports 59 completed adjudications and 1 unresolved review case. The original A1/A2 labels mostly do not follow the approved vocabulary, so the pilot is not yet a defensible training/evaluation target without further review and agreement work. It is suitable for methodology testing, not performance claims.", "", "## Safe next steps", "", "1. Resolve the remaining adjudication issue and decide how the two canonical-text mismatches are handled.", "2. Complete/verify policy-conforming independent annotations and rerun IAA.", "3. Define a leakage-safe split policy: group by user, normalized duplicate text, and augmentation parent; keep cross-platform duplicate groups together; document time/platform handling.", "4. Only after approval, create a separate training artifact using human-reviewed labels and feature exclusion rules.", "", "## Reproducibility", "", "Run from the project root:", "", "```powershell", "python src\\dataset_quality_leakage_audit.py", "```", "", "This script reads the three raw CSVs with strict CSV parsing, detects UTF-8/CP1252 decoding, computes exact counts and normalized SHA-256 text hashes, and writes the two reports plus duplicate candidates without changing inputs.", "", "## Decision", "", "**Safe now:** review the audit, resolve annotation/mismatch issues, and document grouping/split policy. **Blocked:** model training, target construction from legacy tiers, and leakage-sensitive evaluation until human-label quality and split policy are approved."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {REPORT}"); print(f"Created {METRICS}"); print(f"Near-duplicate candidates: {len(near)}")

if __name__ == "__main__": main()
