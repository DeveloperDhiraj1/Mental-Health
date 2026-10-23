# Pilot-60 Qualitative Analysis

## Methodology

This analysis uses only the final adjudicated labels and context flags in `Data/processed/annotation_work/manual_adjudication_workbook.csv`. Legacy tiers, lexicon outputs, model predictions, confidence/probability fields, and original A1/A2 labels were not used to calculate the descriptive distributions. No records, labels, source files, or splits were changed.

The sample contains 60 records: 20 YouTube, 20 Reddit, and 20 Twitter/X. Percentages are descriptive percentages within this fixed pilot, not population estimates.

## Label frequencies

- Label-set combinations: `{'mental_health_reference_or_support': 11, 'distress_negative_affect': 12, 'none_other': 25, 'distress_negative_affect|self_harm_related': 2, 'distress_negative_affect|mental_health_reference_or_support': 5, 'distress_negative_affect|mental_health_reference_or_support|self_harm_related': 4, 'mental_health_reference_or_support|self_harm_related': 1}`.
- Substantive signal incidence, counting a multi-label record once for each applicable signal: `{'mental_health_reference_or_support': 21, 'distress_negative_affect': 23, 'none_other': 25, 'self_harm_related': 7}`.
- `none_other` appears alone in 25 records; it was not combined with another label.
- The complete platform-by-label table is in `reports/pilot60_platform_label_summary.csv`.

### Platform observations

- **YouTube:** 20 records; the most frequent label set was `mental_health_reference_or_support` (6), followed by `none_other` (6) and `distress_negative_affect` (4).
- **Reddit:** 20 records; `none_other` was most frequent (11). The combined three-signal label occurred 3 times, but this is only a small pilot count.
- **Twitter/X:** 20 records; `none_other` occurred 8 times and `distress_negative_affect` occurred 6 times. These differences are descriptive only and should not be generalized to the platforms.

## Context patterns

Context-flag counts, treating each flag separately, were: `{'first_person_or_self_report': 13, 'context_insufficient': 17, 'educational_or_information': 7, '<BLANK>': 11, 'promotional_or_campaign': 5, 'third_person': 3, 'quoted_or_reported': 2, 'fictional_or_hypothetical': 3, 'sarcastic_or_ironic': 1}`.
- `first_person_or_self_report`: 13 records. This indicates wording presented as self-report; it does not establish a clinical condition.
- `context_insufficient`: 17 records. These are important uncertainty cases and show why forcing every text into a confident interpretation can be unsafe.
- `educational_or_information`: 7; `promotional_or_campaign`: 5; `fictional_or_hypothetical`: 3; `third_person` or quoted/reported combinations: 3; `sarcastic_or_ironic`: 1.
- The complete platform-by-context table is in `reports/pilot60_context_flag_distribution.csv`.

## Illustrative policy decisions

The examples below are brief paraphrases of adjudication notes, identified by record ID; raw usernames and full post text are omitted.

- `7cb4f4f5-62be-4740-85d8-82ffb9206eb8` (YouTube): a first-person mention of anxiety alongside a breathing strategy was labeled `mental_health_reference_or_support`; no self-harm signal was inferred.
- `8c1799db-1200-4737-99e0-3bb5dae7f31b` (YouTube): recommending content about understanding or addressing anxiety was treated as educational/informational support, not as a first-person report.
- `cd0d2086-60d8-4965-9cac-5b8514fcc2f2` (Twitter/X): a third-person/quoted reference to loneliness was treated as a possible negative-affect signal, without inferring that the author personally experienced it.
- `e0b6a34c-7cce-46e2-8cf0-4781de66722a` (Twitter/X): an ironic statement about repeatedly hearing a sentence received `none_other` with a sarcasm flag because no approved signal was clearly present.
- `2a23caa3-f2d4-4222-bb7f-ae10c0dc698f` (YouTube): a mental-health reference was retained while `context_insufficient` was recorded because surrounding context was missing.

## Text-mismatch handling

Two records have documented A2 text mismatches: `95728c25-80b6-41e9-ad4c-f8566d580284` and `d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e`. Their adjudication notes state that canonical seed text was used. This preserves a clear audit trail, but these records should remain flagged in any later analysis.

## Biases and limitations

- Each platform contributes only 20 records; platform differences may be random variation rather than real platform effects.
- The pilot was not prevalence-representative and contains multi-label outcomes, so label-set percentages do not measure population rates.
- Rare combinations have very small support; no stable platform comparison or model metric can be inferred.
- Context insufficiency, sarcasm, quotation, educational content, and third-person wording create interpretation uncertainty.
- Synthetic/augmented data and duplicate groups require separate leakage controls; this analysis does not create evaluation splits.
- The original A1/A2 data had only 8/60 policy-valid pairs, so the final adjudication distribution should not be described as strong inter-annotator reliability evidence.
- Nothing here identifies a diagnosis, current suicide risk, or actual mental-health condition of any author.

## Final-year project wording

In this 60-record pilot, human adjudication produced descriptive, non-ordinal labels for observable linguistic content across three platforms. The pilot demonstrated the annotation and adjudication workflow and exposed uncertainty cases, but its small and non-representative sample, rare label combinations, documented text mismatches, and limited policy-valid original agreement prevent reliable model evaluation or clinical interpretation.

## Recommended next step

Use these outputs for the qualitative/methodology chapter and preserve the audit trail. Do not train or evaluate a model from this pilot. Any future modeling requires a larger approved annotation set and the leakage-safe grouping protocol already documented in the project.
