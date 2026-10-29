# Annotation Batch v1 Guide

## Status

This is a blank, owner-policy-based annotation workflow. It is a research tool for observable text signals, not a diagnostic or clinical-risk system.

## Files and independence

- `Data/processed/annotation_batch_v1/A1_annotation.csv` is for A1 only.
- `Data/processed/annotation_batch_v1/A2_annotation.csv` is for A2 only.
- Annotators must not open the other annotator's file or see legacy tier/model metadata.
- The canonical `post_text` and `record_id` must not be changed.

## Label entry

Use only:

- `none_other`
- `distress_negative_affect`
- `mental_health_reference_or_support`
- `self_harm_related`

Multiple substantive labels use this exact order and separator:

`distress_negative_affect|mental_health_reference_or_support|self_harm_related`

`none_other` must stand alone. Do not use old values such as `non_mental_health`, `mental_health_self_report`, or tier numbers. Do not use `+` as a separator.

## Context flags

Keep context flags separate from labels. Approved values are:

`first_person_or_self_report`, `third_person`, `quoted_or_reported`, `educational_or_information`, `fictional_or_hypothetical`, `sarcastic_or_ironic`, `promotional_or_campaign`, `context_insufficient`.

Join multiple flags with `|`. Do not infer that a context flag means the author personally experienced the topic.

## Record-by-record procedure

1. Read the complete canonical post text.
2. Decide which observable content signals are clearly present.
3. Add applicable context flags separately.
4. Enter a short rationale based on the text, not a diagnosis or personal-risk conclusion.
5. Use `needs_review` when context is insufficient, meaning is ambiguous, sarcasm is unresolved, or the record requires adjudication.
6. Set `annotation_status` to `completed` only after the row is fully reviewed; otherwise keep `not_started` or use `needs_review`.

Quoted, educational, fictional, hypothetical, third-person, prevention, and recovery content may receive a content label when the topic is clearly present, but annotators must not infer personal experience. `self_harm_related` is a content label and does not indicate current personal risk.

## Adjudication

After A1 and A2 independently finish, preserve both files, compare by `record_id`, and send disagreements, invalid values, source-text questions, and unresolved cases to adjudication. Never silently rewrite the independent files. Use the validation script before agreement analysis.

## Prior mismatch items

`prior_text_mismatch_review.csv` records the two earlier pilot IDs whose annotator text did not match the canonical seed. Leave the decision blank until a human confirms the source-text handling; these records are not silently repaired.
