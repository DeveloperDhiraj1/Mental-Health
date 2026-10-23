# Inter-Annotator Agreement Analysis

## Scope

This analysis uses original A1/A2 annotations only. Final adjudicated labels are not used as replacements. No source or annotation file was modified; labels describe non-clinical text signals, not diagnoses.

## Structural validation

- Seed rows: **60**; A1 rows: **60**; A2 rows: **60**.
- Expected IDs present exactly once in A1: **True**.
- Expected IDs present exactly once in A2: **True**.
- A1/A2 ID sets match: **True**.
- Platform counts: {'twitter': 20, 'reddit': 20, 'youtube': 20}.
- A1 text mismatches against canonical seed text: **2**.
- A2 text mismatches against canonical seed text: **2** (95728c25-80b6-41e9-ad4c-f8566d580284, d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e).

## Original-label agreement

- Raw exact label-string agreement: **60/60 (100.00%)**. This is case/order-sensitive and includes invalid values.
- Valid policy-conforming paired labels: **8/60**.
- Valid exact label-set agreement: **8/8 (100.00%)**.

### Binary agreement on valid pairs

- `none_other`: observed=100.00%, positive=N/A, negative=100.00%, kappa=N/A
- `distress_negative_affect`: observed=100.00%, positive=N/A, negative=100.00%, kappa=N/A
- `mental_health_reference_or_support`: observed=100.00%, positive=100.00%, negative=N/A, kappa=N/A
- `self_harm_related`: observed=100.00%, positive=N/A, negative=100.00%, kappa=N/A

For each binary label, observed agreement = (TP+TN)/N; positive agreement = 2TP/(2TP+FP+FN); negative agreement = 2TN/(2TN+FP+FN). Cohen's kappa is reported only when its denominator is defined; blank in the CSV means mathematically undefined, commonly because both annotators have zero variance for that label or no valid pairs.

## Validation problems

- Invalid/missing label or context observations: 204 issue counts; see details below.
- Label/context issue summary: {'A1_label_unknown_label': 52, 'A2_label_unknown_label': 52, 'A1_context_unknown_context': 50, 'A2_context_unknown_context': 50, 'a1_seed_text_mismatch': 2, 'a2_seed_text_mismatch': 2}
- Distinct invalid label values: {'A1:non_mental_health': 39, 'A2:non_mental_health': 39, 'A1:suicidal_ideation_or_hopelessness+support': 1, 'A2:suicidal_ideation_or_hopelessness+support': 1, 'A1:suicidal_ideation_or_hopelessness': 1, 'A2:suicidal_ideation_or_hopelessness': 1, 'A1:non-mental_health_or_support': 1, 'A2:non-mental_health_or_support': 1, 'A1:mental_health_self_report': 4, 'A2:mental_health_self_report': 4, 'A1:Depression_or_hopelessness': 1, 'A2:Depression_or_hopelessness': 1, 'A1:mental_health_reference_Information': 1, 'A2:mental_health_reference_Information': 1, 'A1:mental_health_advice': 1, 'A2:mental_health_advice': 1, 'A1:non_mental_health+support': 1, 'A2:non_mental_health+support': 1, 'A1:suicidal_self_report': 1, 'A2:suicidal_self_report': 1, 'A1:non_mental_health+hate': 1, 'A2:non_mental_health+hate': 1}
- Distinct invalid context values: {'A1:mental_health_reference': 21, 'A2:mental_health_reference': 21, 'A1:unrelated_or_neutral': 25, 'A2:unrelated_or_neutral': 25, 'A1:support_or_advice': 4, 'A2:support_or_advice': 4}

## Context flags

- Valid paired context rows: **10/60**.
- Exact context-set agreement on valid context pairs: **10/10 (100.00%)**.
- Context flags were analyzed independently from substantive labels; per-flag metrics are in the machine-readable file with `dimension` beginning `context:`.

## Limitations and recommendation

The approved policy is not satisfied by most original A1/A2 label values, so the valid policy-based denominator is small and cannot support a reliable overall kappa claim. Raw agreement is descriptive only. The two A1/A2 text mismatches should remain documented and should be resolved or excluded by explicit methodological decision before using this pilot for model development.

**Recommendation: conduct further manual review/annotation repair, then rerun IAA. Do not train a model or create evaluation splits from this pilot yet.**
