"""Read-only validation of the latest manual adjudication workbook."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "Data" / "processed" / "annotation_work"
SOURCE = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
A1 = WORK_DIR / "A1_annotation.csv"
A2 = WORK_DIR / "A2_annotation.csv"
REPORT = ROOT / "reports" / "final_annotation_validation_report.md"
ISSUES = ROOT / "reports" / "final_annotation_validation_issues.csv"

LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
ORDER = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}
CONFIDENCE = {"high", "medium", "low"}
BOOL = {"true", "false", ""}

REQUIRED = {
    "record_id", "platform", "post_text", "A1_labels", "A1_context_flags", "A1_confidence", "A1_needs_review", "A1_review_reason",
    "A2_labels", "A2_context_flags", "A2_confidence", "A2_needs_review", "A2_review_reason", "A2_text_mismatch", "source_text_verified",
    "review_reason_category", "final_adjudicated_label", "final_context_flags", "final_confidence", "adjudication_status", "adjudication_notes",
}

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def add(issues, rid, platform, issue_type, field, value, detail):
    issues.append({"record_id": rid or "", "platform": platform or "", "issue_type": issue_type, "field": field, "value": value, "detail": detail})

def valid_label(value: str) -> bool:
    value = value.strip()
    if not value or value == "none_other":
        return True
    parts = value.split("|")
    return len(parts) == len(set(parts)) and "none_other" not in parts and parts == [x for x in ORDER if x in parts] and set(parts) <= LABELS

def valid_context(value: str) -> bool:
    return not value.strip() or set(value.split("|")) <= CONTEXT and all(value.split("|"))

def main() -> None:
    candidates = []
    for path in sorted(WORK_DIR.glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            header = set(next(csv.reader(handle), []))
        if REQUIRED <= header:
            candidates.append(path)
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one reviewed workbook candidate; found {len(candidates)}: {candidates}")
    reviewed_path = candidates[0]
    reviewed = read_csv(reviewed_path)
    seed = read_csv(SOURCE)
    a1 = {r.get("record_id", ""): r for r in read_csv(A1)}
    a2 = {r.get("record_id", ""): r for r in read_csv(A2)}
    seed_by_id = {r.get("record_id", ""): r for r in seed}
    issues = []
    reviewed_ids = [r.get("record_id", "") for r in reviewed]
    for rid, count in Counter(reviewed_ids).items():
        if not rid:
            add(issues, rid, "", "missing_record_id", "record_id", rid, "Record ID is blank")
        elif count > 1:
            add(issues, rid, "", "duplicate_record_id", "record_id", rid, "Duplicate workbook record ID")
    expected = set(seed_by_id)
    actual = set(reviewed_ids)
    for rid in sorted(expected - actual):
        add(issues, rid, seed_by_id[rid].get("platform", ""), "missing_record_id", "record_id", rid, "Expected seed record absent")
    for rid in sorted(actual - expected):
        add(issues, rid, "", "unexpected_record_id", "record_id", rid, "Workbook ID not found in seed")
    for row in reviewed:
        rid = row.get("record_id", "")
        if rid not in seed_by_id:
            continue
        source = seed_by_id[rid]
        if row.get("platform", "") != source.get("platform", ""):
            add(issues, rid, row.get("platform", ""), "platform_mismatch", "platform", row.get("platform", ""), "Does not match seed")
        if row.get("post_text", "") != source.get("post_text", ""):
            add(issues, rid, row.get("platform", ""), "canonical_text_mismatch", "post_text", "<present>", "Workbook text differs from seed")
        expected_a2 = row.get("post_text", "") != a2.get(rid, {}).get("post_text", row.get("post_text", ""))
        if row.get("A2_text_mismatch", "").strip().casefold() not in {"true", "false"} or (row["A2_text_mismatch"].strip().casefold() == "true") != expected_a2:
            add(issues, rid, row.get("platform", ""), "A2_text_mismatch_flag_error", "A2_text_mismatch", row.get("A2_text_mismatch", ""), "Flag does not match seed/A2 comparison")
        expected_verified = row.get("post_text", "") == source.get("post_text", "") and a1.get(rid, {}).get("post_text") == source.get("post_text", "") and a2.get(rid, {}).get("post_text") == source.get("post_text", "")
        if (row.get("source_text_verified", "").strip().casefold() == "true") != expected_verified:
            add(issues, rid, row.get("platform", ""), "source_text_verified_flag_error", "source_text_verified", row.get("source_text_verified", ""), "Flag does not match seed/A1/A2 comparison")
        label = row.get("final_adjudicated_label", "")
        if not label.strip():
            add(issues, rid, row.get("platform", ""), "blank_final_label", "final_adjudicated_label", "", "Final label not entered")
        elif not valid_label(label):
            add(issues, rid, row.get("platform", ""), "invalid_final_label", "final_adjudicated_label", label, "Not valid under approved vocabulary/order")
        if not valid_context(row.get("final_context_flags", "")):
            add(issues, rid, row.get("platform", ""), "invalid_context_flag", "final_context_flags", row.get("final_context_flags", ""), "Unknown or malformed context flag")
        confidence = row.get("final_confidence", "").strip().casefold()
        if confidence and confidence not in CONFIDENCE:
            add(issues, rid, row.get("platform", ""), "invalid_confidence", "final_confidence", row.get("final_confidence", ""), "Expected High, Medium, Low, or blank")
        status = row.get("adjudication_status", "").strip().casefold()
        if status not in {"", "completed", "needs_review"}:
            add(issues, rid, row.get("platform", ""), "invalid_status", "adjudication_status", row.get("adjudication_status", ""), "Unexpected adjudication status")
        if status == "needs_review":
            add(issues, rid, row.get("platform", ""), "unresolved_case", "adjudication_status", row.get("adjudication_status", ""), "Needs review remains unresolved")
        if status in {"completed", "needs_review"} and not row.get("adjudication_notes", "").strip():
            add(issues, rid, row.get("platform", ""), "missing_adjudication_rationale", "adjudication_notes", "", "Completed/unresolved case lacks rationale")
    with ISSUES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["record_id", "platform", "issue_type", "field", "value", "detail"])
        writer.writeheader(); writer.writerows(issues)
    final_counts = Counter(r.get("final_adjudicated_label", "") or "<BLANK>" for r in reviewed)
    status_counts = Counter(r.get("adjudication_status", "") or "<BLANK>" for r in reviewed)
    mismatch_ids = [r["record_id"] for r in reviewed if r.get("A2_text_mismatch", "").strip().casefold() == "true"]
    issue_counts = Counter(i["issue_type"] for i in issues)
    lines = ["# Final Annotation Validation Report", "", "## Scope", "", f"Latest reviewed workbook selected by schema: `{reviewed_path.relative_to(ROOT)}`.", "The workbook, original A1/A2 files, seed sample, policy, and prior annotations were read only.", "Labels are non-clinical text-content annotations, not diagnoses or clinical ground truth.", "", "## Current reviewed counts", "", f"- Workbook rows: **{len(reviewed)}**; expected 60.", f"- Final label distribution: {dict(final_counts)}", f"- Adjudication status distribution: {dict(status_counts)}", f"- Blank final labels: **{sum(not r.get('final_adjudicated_label', '').strip() for r in reviewed)}**", f"- Unresolved `needs_review` statuses: **{sum(r.get('adjudication_status', '').strip().casefold() == 'needs_review' for r in reviewed)}**", f"- A2 text mismatches against seed: **{len(mismatch_ids)}**.", f"- A2 mismatch record IDs: {', '.join(mismatch_ids) if mismatch_ids else 'None'}", "", "## Validation issues", "", f"- Total issue records: **{len(issues)}**. See `{ISSUES.relative_to(ROOT)}`."]
    lines += [f"- `{k}`: {v}" for k, v in sorted(issue_counts.items())] or ["- None detected."]
    lines += ["", "## Recommendation", "", "**Further manual review is required before final agreement analysis or any model work.**" if issues else "**Validation passed; proceed to documented agreement analysis.**"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reviewed workbook: {reviewed_path}")
    print(f"Created {REPORT}")
    print(f"Created {ISSUES} with {len(issues)} issues")

if __name__ == "__main__":
    main()
