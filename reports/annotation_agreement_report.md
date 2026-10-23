# Annotation Agreement Report

## Scope and safety

This report compares A1 and A2 annotations only. It does not correct, merge, adjudicate, relabel, train a model, or change dataset splits.
Annotations are treated as non-clinical text-signal judgments, not diagnoses.

## Actual input files

- Seed source: `Data\processed\pilot_annotation_seed42.csv` (60 rows)
- A1: `Data\processed\annotation_work\A1_annotation.csv` (60 rows)
- A2: `Data\processed\annotation_work\A2_annotation.csv` (60 rows)
- Policy: `reports/pilot_annotation_policy.md`

## Structural validation

- A1 exactly 60 rows: **yes**
- A2 exactly 60 rows: **yes**
- Same record-ID set: **yes**
- A1/A2 platform/text mismatches: 0 / 2.
- A1/source platform/text mismatches: 0 / 0.
- A2/source platform/text mismatches: 0 / 2.

## Agreement summary

- Raw label-string equality: 38/60 (63.33%).
- Valid exact label-set matches: 8/8 (100.00%).
- Valid exact label-set disagreements: 0/8.
- Invalid or missing annotation rows: 52.

The valid exact-set metric compares labels as sets after splitting on `|`; label order does not create a disagreement. Invalid/missing labels are not counted as valid agreement.

## Per-label metrics: overall

- Valid paired annotations: 8
- Label | Valid pairs | Agreement | Cohen's kappa
- |---:|---:|---:|
- `none_other` | 8 | 100.00% | N/A (zero expected variance)
- `distress_negative_affect` | 8 | 100.00% | N/A (zero expected variance)
- `mental_health_reference_or_support` | 8 | 100.00% | N/A (zero expected variance)
- `self_harm_related` | 8 | 100.00% | N/A (zero expected variance)

## Per-platform metrics

### youtube
- Valid paired annotations: 2
- Label | Valid pairs | Agreement | Cohen's kappa
- |---:|---:|---:|
- `none_other` | 2 | 100.00% | N/A (zero expected variance)
- `distress_negative_affect` | 2 | 100.00% | N/A (zero expected variance)
- `mental_health_reference_or_support` | 2 | 100.00% | N/A (zero expected variance)
- `self_harm_related` | 2 | 100.00% | N/A (zero expected variance)

### reddit
- Valid paired annotations: 2
- Label | Valid pairs | Agreement | Cohen's kappa
- |---:|---:|---:|
- `none_other` | 2 | 100.00% | N/A (zero expected variance)
- `distress_negative_affect` | 2 | 100.00% | N/A (zero expected variance)
- `mental_health_reference_or_support` | 2 | 100.00% | N/A (zero expected variance)
- `self_harm_related` | 2 | 100.00% | N/A (zero expected variance)

### twitter
- Valid paired annotations: 4
- Label | Valid pairs | Agreement | Cohen's kappa
- |---:|---:|---:|
- `none_other` | 4 | 100.00% | N/A (zero expected variance)
- `distress_negative_affect` | 4 | 100.00% | N/A (zero expected variance)
- `mental_health_reference_or_support` | 4 | 100.00% | N/A (zero expected variance)
- `self_harm_related` | 4 | 100.00% | N/A (zero expected variance)

## Invalid and missing values

The comparison preserves invalid values and does not infer replacements.
- `A1_invalid_context_flag`: 50
- `A1_unknown_label`: 35
- `A1_unknown_value:mental_health_self_report`: 6
- `A1_unknown_value:non_mental_health`: 25
- `A1_unknown_value:suicidal_ideation_or_hopelessness`: 3
- `A1_unknown_value:suicidal_self_report`: 1
- `A2_invalid_context_flag`: 50
- `A2_source_post_text_mismatch`: 2
- `A2_unknown_label`: 52
- `A2_unknown_value:Depression_or_hopelessness`: 1
- `A2_unknown_value:mental_health_advice`: 1
- `A2_unknown_value:mental_health_reference_Information`: 1
- `A2_unknown_value:mental_health_self_report`: 4
- `A2_unknown_value:non-mental_health_or_support`: 1
- `A2_unknown_value:non_mental_health`: 39
- `A2_unknown_value:non_mental_health+hate`: 1
- `A2_unknown_value:non_mental_health+support`: 1
- `A2_unknown_value:suicidal_ideation_or_hopelessness`: 1
- `A2_unknown_value:suicidal_ideation_or_hopelessness+support`: 1
- `A2_unknown_value:suicidal_self_report`: 1
- `post_text_mismatch`: 2

## Limitations and manual next steps

Cohen's kappa is calculated on valid paired annotations only. It can be unreliable or undefined with small samples, rare labels, class imbalance, or zero expected variance. Invalid/missing rows and review-flagged rows require manual inspection.

Review `Data/processed/annotation_work/adjudication_queue.csv`. An adjudicator must preserve A1/A2 labels and manually enter the final label, notes, and status. Do not use legacy tier fields as ground truth. Do not train or split data until adjudication and the approved leakage policy are complete.
