# Annotation Quality Review

## Scope and safety

This is a fresh read-only comparison of all 60 A1/A2 pairs against the canonical seed and adjudication workbook. Original annotations, final labels, raw data, frontend, backend, and split assignments were not modified. No legacy tier, prediction, probability, or lexicon field was used.

## Current findings

- Review rows: **60**.
- A1/A2 ID coverage: **60/60** rows; IDs matched the 60-record seed: **True**.
- Final adjudicated labels/context fields policy-valid: **60/60**.
- Category counts: **{'legacy_or_unmapped_label_vocabulary': 52, 'invalid_context_flag': 50, 'malformed_multilabel': 3, 'source_text_mismatch': 2}**.
- The approved labels are non-clinical text-content categories. A policy-invalid original annotation does not prove that the adjudicated label is wrong.

## Cause interpretation

- Values such as `mental_health_self_report`, `non_mental_health`, and `suicidal_ideation_or_hopelessness` are outside the approved vocabulary and require manual review; they are not automatically mapped.
- Values containing `+` use unsupported multi-label serialization; the approved separator is `|`.
- `none_other` must stand alone. Any combined occurrence is a policy violation.
- When both original labels are policy-valid but differ as sets, the disagreement is classified as genuine semantic disagreement for human review.
- Text mismatch categories identify source alignment problems only; they do not determine a label.

## Review table

Machine-readable row-level table: `reports\annotation_quality_review.csv`. It contains labels and validation metadata but no raw post text or user identifiers.

## Policy clarifications to propose, not apply

1. Add explicit examples distinguishing `mental_health_reference_or_support` from `distress_negative_affect` when a post mentions coping advice without describing distress.
2. State that first-person mental-health references may receive the content label plus a context flag, but annotators must not create a separate self-report signal label.
3. Give examples for prevention, recovery, third-person reports, and educational content under `self_harm_related`.
4. Provide a one-line serialization warning: use `|`, never `+`, and keep `none_other` exclusive.
5. Require `needs_review=TRUE` when context is insufficient or a source-text mismatch is found.

## Decision

The 60 adjudicated final labels remain valid under this mechanical policy check, but the original independent annotations are not a reliable agreement basis because most use an older or undocumented vocabulary. Do not train a model from this pilot. Continue with a new approved, independent annotation batch and rerun validation/IAA before model preparation.

This project studies non-clinical linguistic signals, not diagnosis or clinical risk prediction.

## Recommended next annotation batch

Use a new **60–100 record batch per review cycle**, subject to actual annotator capacity. Keep platform strata balanced where possible, use two independent annotators, and review each batch before expanding. Do not use legacy labels or model outputs for target assignment.

Continue only when the approved vocabulary is used consistently, unresolved/source-text mismatch cases are documented, policy-valid agreement is adequate for the intended use, and each substantive label has enough reviewed examples.
