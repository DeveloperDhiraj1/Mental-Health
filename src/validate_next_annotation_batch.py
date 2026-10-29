"""Validate the next annotation batch without repairing it."""
from __future__ import annotations

import csv
import argparse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "Data" / "processed" / "annotation_batch_v1"
RAW = ROOT / "Data" / "raw"
REPORT = ROOT / "reports" / "annotation_batch_v1_validation.md"
ERRORS = ROOT / "reports" / "annotation_batch_v1_validation_errors.csv"
FIELDS = ["record_id", "stable_record_key", "platform", "post_text", "duplicate_group_hash", "source_text_review_required", "annotator_id", "proposed_label", "context_flags", "confidence", "rationale", "annotation_status", "needs_review", "review_notes"]
LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
ORDER = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def label_errors(value: str) -> list[str]:
    if not value.strip(): return []
    parts = value.strip().split("|")
    errors = []
    if value.strip() == "none_other": return []
    if "none_other" in parts: errors.append("none_other_must_stand_alone")
    if any(part not in LABELS for part in parts): errors.append("unknown_label")
    if len(parts) != len(set(parts)): errors.append("duplicate_label")
    if "+" in value: errors.append("use_pipe_separator_not_plus")
    if not any(part not in LABELS for part in parts) and parts != [label for label in ORDER if label in parts]: errors.append("wrong_label_order")
    return errors


def context_errors(value: str) -> list[str]:
    if not value.strip(): return []
    parts = value.strip().split("|")
    errors = []
    if any(part not in CONTEXT for part in parts): errors.append("unknown_context_flag")
    if len(parts) != len(set(parts)): errors.append("duplicate_context_flag")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-dir", type=Path, default=BATCH)
    args = parser.parse_args()
    batch = args.batch_dir if args.batch_dir.is_absolute() else ROOT / args.batch_dir
    report = ROOT / "reports" / f"{batch.name}_validation.md"
    error_file = ROOT / "reports" / f"{batch.name}_validation_errors.csv"
    manifest = read(batch / "batch_manifest.csv")
    source_by_id = {}
    for filename in ("youtube_data set.csv", "reddit_dataSet.csv", "twitter_data set.csv"):
        encoding = "cp1252" if filename == "youtube_data set.csv" else "utf-8-sig"
        with (RAW / filename).open(encoding=encoding, newline="") as handle:
            for row in csv.DictReader(handle): source_by_id[row["record_id"].strip()] = row
    errors = []
    manifest_ids = [row.get("record_id", "") for row in manifest]
    if len(manifest_ids) != len(set(manifest_ids)): errors.append({"record_id": "", "issue": "duplicate_manifest_id", "detail": "Manifest contains duplicate record IDs"})
    for row in manifest:
        rid = row.get("record_id", "")
        if not rid or rid not in source_by_id: errors.append({"record_id": rid, "issue": "missing_source_id", "detail": "Manifest ID absent from raw sources"})
        elif row.get("platform") != source_by_id[rid].get("platform", row.get("platform")): errors.append({"record_id": rid, "issue": "platform_mismatch", "detail": "Manifest platform differs from source"})
    expected = {row["record_id"]: row for row in manifest}
    for annotator in ("A1", "A2"):
        rows = read(batch / f"{annotator}_annotation.csv")
        if len(rows) != len(manifest): errors.append({"record_id": "", "issue": "row_count", "detail": f"{annotator} has {len(rows)} rows; expected {len(manifest)}"})
        seen = Counter(row.get("record_id", "") for row in rows)
        for rid, count in seen.items():
            if count != 1: errors.append({"record_id": rid, "issue": "duplicate_annotation_id", "detail": f"{annotator} appears {count} times"})
        if set(seen) != set(expected): errors.append({"record_id": "", "issue": "id_set_mismatch", "detail": f"{annotator} IDs differ from manifest"})
        for row in rows:
            rid = row.get("record_id", "")
            source = source_by_id.get(rid, {})
            if row.get("post_text") != source.get("post_text"): errors.append({"record_id": rid, "issue": "text_mismatch", "detail": f"{annotator} text differs from canonical raw text"})
            if row.get("platform") != source.get("platform"): errors.append({"record_id": rid, "issue": "platform_mismatch", "detail": f"{annotator} platform differs from source"})
            for issue in label_errors(row.get("proposed_label", "")): errors.append({"record_id": rid, "issue": f"{annotator}_{issue}", "detail": "Annotation value violates approved label policy"})
            for issue in context_errors(row.get("context_flags", "")): errors.append({"record_id": rid, "issue": f"{annotator}_{issue}", "detail": "Context value violates approved vocabulary"})
    error_file.parent.mkdir(parents=True, exist_ok=True)
    with error_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "issue", "detail"]); writer.writeheader(); writer.writerows(errors)
    lines = [f"# {batch.name} Validation", "", "This validation reads the A1/A2 templates and raw canonical text without changing them. Blank annotation fields are expected before annotation begins.", "", f"- Manifest rows: **{len(manifest)}**.", f"- Platform counts: **{dict(Counter(row.get('platform', '') for row in manifest))}**.", f"- Validation issue records: **{len(errors)}**.", f"- Required columns present: **{all(set(FIELDS) <= set(read(batch / f'{a}_annotation.csv')[0]) for a in ('A1', 'A2'))}**.", f"- A1/A2 blank initial labels: **{all(not row.get('proposed_label', '').strip() for a in ('A1', 'A2') for row in read(batch / f'{a}_annotation.csv'))}**.", f"- All integrity/policy checks passed: **{not errors}**.", "", f"Machine-readable issues: `{error_file.relative_to(ROOT)}`.", "", "No labels are assigned by this script. Non-empty annotations must be revalidated after human review."]
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Validation issues: {len(errors)}")
    print(f"Created {report}")
    print(f"Created {error_file}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
