# Final Annotation Validation Report

## Scope

Latest reviewed workbook selected by schema: `Data\processed\annotation_work\manual_adjudication_workbook.csv`.
The workbook, original A1/A2 files, seed sample, policy, and prior annotations were read only.
Labels are non-clinical text-content annotations, not diagnoses or clinical ground truth.

## Current reviewed counts

- Workbook rows: **60**; expected 60.
- Final label distribution: {'mental_health_reference_or_support': 11, 'distress_negative_affect': 12, 'none_other': 25, 'distress_negative_affect|self_harm_related': 2, 'distress_negative_affect|mental_health_reference_or_support': 5, 'distress_negative_affect|mental_health_reference_or_support|self_harm_related': 4, 'mental_health_reference_or_support|self_harm_related': 1}
- Adjudication status distribution: {'completed': 59, 'needs_review': 1}
- Blank final labels: **0**
- Unresolved `needs_review` statuses: **1**
- A2 text mismatches against seed: **2**.
- A2 mismatch record IDs: 95728c25-80b6-41e9-ad4c-f8566d580284, d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e

## Validation issues

- Total issue records: **1**. See `reports\final_annotation_validation_issues.csv`.
- `unresolved_case`: 1

## Recommendation

**Further manual review is required before final agreement analysis or any model work.**
