"""Fresh, read-only review of the 60 original annotation pairs."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
WORK = ROOT / "Data" / "processed" / "annotation_work"
A1 = WORK / "A1_annotation.csv"
A2 = WORK / "A2_annotation.csv"
ADJ = WORK / "manual_adjudication_workbook.csv"
OUT = ROOT / "reports" / "annotation_quality_review.csv"
REPORT = ROOT / "reports" / "annotation_quality_review.md"
CHECKLIST = ROOT / "reports" / "annotation_quality_review_checklist.md"

LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
ORDER = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def label_errors(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return ["missing_label"]
    parts = value.split("|")
    errors = []
    if any(not part or part != part.strip() for part in parts):
        errors.append("malformed_multilabel_spacing")
    if "+" in value:
        errors.append("malformed_multilabel_separator")
    unknown = [part for part in parts if part not in LABELS]
    if unknown:
        errors.append("invalid_label_vocabulary:" + "|".join(unknown))
    if "none_other" in parts and len(parts) != 1:
        errors.append("none_other_combined_with_substantive_label")
    if len(parts) != len(set(parts)):
        errors.append("duplicate_label")
    if not unknown and value != "none_other" and parts != [label for label in ORDER if label in parts]:
        errors.append("wrong_fixed_label_order")
    return errors


def context_errors(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    parts = value.split("|")
    errors = []
    if any(not part or part != part.strip() for part in parts):
        errors.append("malformed_context_flags")
    unknown = [part for part in parts if part not in CONTEXT]
    if unknown:
        errors.append("invalid_context_vocabulary:" + "|".join(unknown))
    if len(parts) != len(set(parts)):
        errors.append("duplicate_context_flag")
    return errors


def label_set(value: str) -> set[str] | None:
    return None if label_errors(value) else set(value.split("|"))


def main() -> None:
    seed = {row["record_id"]: row for row in read(SEED)}
    a1 = {row["record_id"]: row for row in read(A1)}
    a2 = {row["record_id"]: row for row in read(A2)}
    adjudicated = {row["record_id"]: row for row in read(ADJ)}
    output = []
    category_counts = Counter()
    for rid in sorted(seed):
        source = seed[rid]; left = a1.get(rid, {}); right = a2.get(rid, {}); final = adjudicated.get(rid, {})
        a1_label = left.get("annotator_label", ""); a2_label = right.get("annotator_label", "")
        a1_errors = label_errors(a1_label); a2_errors = label_errors(a2_label)
        a1_context_errors = context_errors(left.get("context_flags", "")); a2_context_errors = context_errors(right.get("context_flags", ""))
        text_mismatch = []
        if left.get("post_text") != source.get("post_text"): text_mismatch.append("A1_source_text_mismatch")
        if right.get("post_text") != source.get("post_text"): text_mismatch.append("A2_source_text_mismatch")
        categories = []
        if text_mismatch: categories.append("source_text_mismatch")
        if a1_errors or a2_errors:
            if any("none_other_combined" in error for error in a1_errors + a2_errors): categories.append("none_other_misuse")
            if any("malformed_multilabel" in error for error in a1_errors + a2_errors): categories.append("malformed_multilabel")
            if any("invalid_label_vocabulary" in error for error in a1_errors + a2_errors): categories.append("legacy_or_unmapped_label_vocabulary")
        if a1_context_errors or a2_context_errors: categories.append("invalid_context_flag")
        left_set, right_set = label_set(a1_label), label_set(a2_label)
        if left_set is not None and right_set is not None and left_set != right_set: categories.append("genuine_semantic_label_disagreement")
        if not categories: categories.append("valid_agreement")
        categories = list(dict.fromkeys(categories))
        category = "|".join(categories)
        category_counts.update(categories)
        final_errors = label_errors(final.get("final_adjudicated_label", "")) + context_errors(final.get("final_context_flags", ""))
        explanation = {
            "valid_agreement": "Both original labels and context fields conform to policy; no label-set disagreement was found.",
            "source_text_mismatch": "Annotator text differs from canonical seed text; adjudicator must confirm which canonical text governs later analysis.",
            "legacy_or_unmapped_label_vocabulary": "One or both values are outside the approved four-label vocabulary. Do not map automatically; human review is required.",
            "malformed_multilabel": "A multi-label value uses unsupported serialization or spacing. Preserve the original and review manually.",
            "none_other_misuse": "none_other appears with another signal; policy requires it to stand alone.",
            "invalid_context_flag": "One or more context values are outside the approved context vocabulary; do not silently rename them.",
            "genuine_semantic_label_disagreement": "Both values are policy-valid but their label sets differ; compare the canonical text and policy rules manually.",
        }
        explanation_text = " ".join(explanation.get(item, "Manual review required.") for item in categories)
        output.append({"record_id": rid, "platform": source.get("platform", ""), "A1_label": a1_label, "A2_label": a2_label, "adjudicated_label": final.get("final_adjudicated_label", ""), "A1_validation_errors": "|".join(a1_errors + a1_context_errors), "A2_validation_errors": "|".join(a2_errors + a2_context_errors), "final_validation_errors": "|".join(final_errors), "disagreement_category": category, "human_review_required": "no" if category == "valid_agreement" and not final_errors else "yes", "review_explanation": explanation_text})
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0])); writer.writeheader(); writer.writerows(output)
    valid_final = sum(not row["final_validation_errors"] for row in output)
    lines = ["# Annotation Quality Review", "", "## Scope and safety", "", "This is a fresh read-only comparison of all 60 A1/A2 pairs against the canonical seed and adjudication workbook. Original annotations, final labels, raw data, frontend, backend, and split assignments were not modified. No legacy tier, prediction, probability, or lexicon field was used.", "", "## Current findings", "", f"- Review rows: **{len(output)}**.", f"- A1/A2 ID coverage: **{len(a1)}/{len(a2)}** rows; IDs matched the 60-record seed: **{set(a1) == set(a2) == set(seed)}**.", f"- Final adjudicated labels/context fields policy-valid: **{valid_final}/{len(output)}**.", f"- Category counts: **{dict(category_counts)}**.", "- The approved labels are non-clinical text-content categories. A policy-invalid original annotation does not prove that the adjudicated label is wrong.", "", "## Cause interpretation", "", "- Values such as `mental_health_self_report`, `non_mental_health`, and `suicidal_ideation_or_hopelessness` are outside the approved vocabulary and require manual review; they are not automatically mapped.", "- Values containing `+` use unsupported multi-label serialization; the approved separator is `|`.", "- `none_other` must stand alone. Any combined occurrence is a policy violation.", "- When both original labels are policy-valid but differ as sets, the disagreement is classified as genuine semantic disagreement for human review.", "- Text mismatch categories identify source alignment problems only; they do not determine a label.", "", "## Review table", "", f"Machine-readable row-level table: `{OUT.relative_to(ROOT)}`. It contains labels and validation metadata but no raw post text or user identifiers.", "", "## Policy clarifications to propose, not apply", "", "1. Add explicit examples distinguishing `mental_health_reference_or_support` from `distress_negative_affect` when a post mentions coping advice without describing distress.", "2. State that first-person mental-health references may receive the content label plus a context flag, but annotators must not create a separate self-report signal label.", "3. Give examples for prevention, recovery, third-person reports, and educational content under `self_harm_related`.", "4. Provide a one-line serialization warning: use `|`, never `+`, and keep `none_other` exclusive.", "5. Require `needs_review=TRUE` when context is insufficient or a source-text mismatch is found.", "", "## Decision", "", "The 60 adjudicated final labels remain valid under this mechanical policy check, but the original independent annotations are not a reliable agreement basis because most use an older or undocumented vocabulary. Do not train a model from this pilot. Continue with a new approved, independent annotation batch and rerun validation/IAA before model preparation.", "", "This project studies non-clinical linguistic signals, not diagnosis or clinical risk prediction."]
    REPORT.write_text("\n".join(lines) + "\n\n## Recommended next annotation batch\n\nUse a new **60–100 record batch per review cycle**, subject to actual annotator capacity. Keep platform strata balanced where possible, use two independent annotators, and review each batch before expanding. Do not use legacy labels or model outputs for target assignment.\n\nContinue only when the approved vocabulary is used consistently, unresolved/source-text mismatch cases are documented, policy-valid agreement is adequate for the intended use, and each substantive label has enough reviewed examples.\n", encoding="utf-8")
    CHECKLIST.write_text("""# Human Review Checklist\n\nUse this checklist for rows in `reports/annotation_quality_review.csv`. Do not edit A1/A2 source files.\n\n1. Open the canonical seed text for the `record_id`; do not use legacy tiers or model fields.\n2. Confirm the text source when `source_text_mismatch` is present; record the decision separately.\n3. Check each original label against the four approved labels. Never map older values automatically.\n4. Confirm `none_other` is alone; otherwise send the row to adjudication.\n5. For multiple substantive labels, require exact `|` order: `distress_negative_affect|mental_health_reference_or_support|self_harm_related`.\n6. Check context flags separately using only the approved policy vocabulary.\n7. Decide whether a policy-valid disagreement is semantic, context-dependent, quoted, educational, fictional, sarcastic, or insufficient-context.\n8. Preserve both original judgments and document the adjudicator decision in the existing adjudication workflow.\n9. Use `needs_review=TRUE` for unresolved ambiguity; do not force a label.\n10. Keep the work local and treat every label as an observable text signal, not a diagnosis or personal-risk conclusion.\n""", encoding="utf-8")
    print(f"Created {OUT} with {len(output)} rows")
    print(f"Created {REPORT}")
    print(f"Created {CHECKLIST}")
    print(dict(category_counts))


if __name__ == "__main__":
    main()
