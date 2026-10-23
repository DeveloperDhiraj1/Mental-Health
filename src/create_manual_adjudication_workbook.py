"""Create a blank manual adjudication workbook from the seed and A1/A2 files.

This script preserves A1/A2 values verbatim, uses the seed sample as canonical
platform/text, mechanically flags policy violations and text mismatches, and
never assigns or maps a final label.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
A1 = ROOT / "Data" / "processed" / "annotation_work" / "A1_annotation.csv"
A2 = ROOT / "Data" / "processed" / "annotation_work" / "A2_annotation.csv"
OUTPUT = ROOT / "Data" / "processed" / "annotation_work" / "manual_adjudication_workbook.csv"
INSTRUCTIONS = ROOT / "reports" / "manual_adjudication_workbook_instructions.md"

ANNOTATION_COLUMNS = (
    "record_id", "platform", "post_text",
    "A1_labels", "A1_context_flags", "A1_confidence", "A1_needs_review", "A1_review_reason",
    "A2_labels", "A2_context_flags", "A2_confidence", "A2_needs_review", "A2_review_reason",
    "A2_text_mismatch", "source_text_verified", "review_reason_category",
    "final_adjudicated_label", "final_context_flags", "final_confidence",
    "adjudication_status", "adjudication_notes",
)
REQUIRED_SOURCE = (
    "record_id", "platform", "post_text", "annotator1_label", "annotator1_confidence",
    "annotator1_needs_review", "annotator1_review_reason", "annotator2_label",
    "annotator2_confidence", "annotator2_needs_review", "annotator2_review_reason", "context_flags",
)
REQUIRED_ANNOTATOR = (
    "record_id", "platform", "post_text", "annotator_label", "annotator_confidence",
    "needs_review", "review_reason", "context_flags",
)
LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
CONTEXT_FLAGS = {
    "first_person_or_self_report", "third_person", "quoted_or_reported",
    "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic",
    "promotional_or_campaign", "context_insufficient",
}


def read_csv(path: Path, expected: tuple[str, ...]) -> list[dict[str, str]]:
    if not path.is_file():
        raise RuntimeError(f"Missing required file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if tuple(reader.fieldnames or ()) != expected:
            raise RuntimeError(f"Schema mismatch in {path}: {reader.fieldnames}")
        return list(reader)


def label_valid(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    parts = value.split("|")
    if any(part not in LABELS for part in parts) or len(set(parts)) != len(parts):
        return False
    if "none_other" in parts and len(parts) != 1:
        return False
    return parts == ["none_other"] or parts == [x for x in (
        "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"
    ) if x in parts]


def context_valid(value: str) -> bool:
    if not value.strip():
        return True
    return all(flag in CONTEXT_FLAGS for flag in value.split("|"))


def issue_category(a1: dict[str, str], a2: dict[str, str], source: dict[str, str]) -> str:
    issues: list[str] = []
    if a1["post_text"] != source["post_text"] or a2["post_text"] != source["post_text"]:
        issues.append("source_text_mismatch")
    if not label_valid(a1["annotator_label"]) or not label_valid(a2["annotator_label"]):
        issues.append("invalid_label_value")
    if not context_valid(a1["context_flags"]) or not context_valid(a2["context_flags"]):
        issues.append("invalid_context_flag")
    if a1["annotator_label"] != a2["annotator_label"]:
        issues.append("label_disagreement")
    if a1["needs_review"].strip().casefold() == "true" or a2["needs_review"].strip().casefold() == "true":
        issues.append("annotator_requested_review")
    if not issues:
        return ""
    unique = list(dict.fromkeys(issues))
    return unique[0] if len(unique) == 1 else "multiple_issues"


def write_instructions() -> None:
    INSTRUCTIONS.write_text(
        """# Manual Adjudication Workbook Instructions

## Purpose

`Data/processed/annotation_work/manual_adjudication_workbook.csv` is a blank
adjudication workbook for the 60-post seed-42 pilot. The seed sample supplies
the canonical `record_id`, `platform`, and `post_text`. A1 and A2 values are
preserved exactly as received and must not be silently repaired.

These labels describe observable non-clinical text signals. They are not
diagnoses, clinical severity scores, or conclusions about an author's personal
condition.

## Review procedure

1. Work one row at a time using the canonical seed `post_text`.
2. Read the preserved A1/A2 labels, context flags, confidence, review flags,
   and reasons as evidence of what each annotator entered—not as ground truth.
3. Decide the final label only from the text and the approved policy.
4. Use only `none_other`, `distress_negative_affect`,
   `mental_health_reference_or_support`, and `self_harm_related`.
5. `none_other` must stand alone. The other three may co-occur.
6. For multiple substantive labels, use this order and delimiter with no spaces:
   `distress_negative_affect|mental_health_reference_or_support|self_harm_related`
7. Enter context flags separately in `final_context_flags`; never put context
   flags in the final label field.
8. For ambiguity, sarcasm, quotation, educational/fictional content, or missing
   context, use the policy's review procedure and explain the decision in
   `adjudication_notes`.
9. Do not use legacy tiers, predictions, probabilities, confidence metadata,
   keywords, or undocumented model fields to decide a final label.
10. Do not change `record_id`, `platform`, `post_text`, A1/A2 columns, or the
    mechanical issue fields.

## Adjudicator fields

Fill only `final_adjudicated_label`, `final_context_flags`,
`final_confidence`, `adjudication_status`, and `adjudication_notes`. Leave the
mechanical source and annotator evidence intact. Review every row marked with a
non-empty `review_reason_category`, especially `source_text_mismatch` and
`multiple_issues`.

Keep the workbook local and use no real personal identifiers. Preserve the
original A1 and A2 files separately. Do not train a model or change splits
during adjudication.
""",
        encoding="utf-8",
    )


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing workbook: {OUTPUT}")
    source = read_csv(SOURCE, REQUIRED_SOURCE)
    a1 = read_csv(A1, REQUIRED_ANNOTATOR)
    a2 = read_csv(A2, REQUIRED_ANNOTATOR)
    if len(source) != 60 or len(a1) != 60 or len(a2) != 60:
        raise RuntimeError(f"Expected 60 rows; source={len(source)}, A1={len(a1)}, A2={len(a2)}")
    source_by_id = {r["record_id"]: r for r in source}
    a1_by_id = {r["record_id"]: r for r in a1}
    a2_by_id = {r["record_id"]: r for r in a2}
    if len(source_by_id) != 60 or len(a1_by_id) != 60 or len(a2_by_id) != 60:
        raise RuntimeError("Duplicate record IDs detected")
    if set(source_by_id) != set(a1_by_id) or set(source_by_id) != set(a2_by_id):
        raise RuntimeError("Source/A1/A2 record-ID sets differ")

    rows: list[dict[str, str]] = []
    for rid in source_by_id:
        s, r1, r2 = source_by_id[rid], a1_by_id[rid], a2_by_id[rid]
        rows.append({
            "record_id": rid,
            "platform": s["platform"],
            "post_text": s["post_text"],
            "A1_labels": r1["annotator_label"],
            "A1_context_flags": r1["context_flags"],
            "A1_confidence": r1["annotator_confidence"],
            "A1_needs_review": r1["needs_review"],
            "A1_review_reason": r1["review_reason"],
            "A2_labels": r2["annotator_label"],
            "A2_context_flags": r2["context_flags"],
            "A2_confidence": r2["annotator_confidence"],
            "A2_needs_review": r2["needs_review"],
            "A2_review_reason": r2["review_reason"],
            "A2_text_mismatch": "TRUE" if r2["post_text"] != s["post_text"] else "FALSE",
            "source_text_verified": "TRUE" if r1["post_text"] == s["post_text"] and r2["post_text"] == s["post_text"] else "FALSE",
            "review_reason_category": issue_category(r1, r2, s),
            "final_adjudicated_label": "",
            "final_context_flags": "",
            "final_confidence": "",
            "adjudication_status": "",
            "adjudication_notes": "",
        })

    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ANNOTATION_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    write_instructions()
    print(f"Created {OUTPUT} with {len(rows)} rows")
    print(f"Created {INSTRUCTIONS}")


if __name__ == "__main__":
    main()
