# Annotation Batch v1 Validation

This validation reads the new A1/A2 templates and raw canonical text without changing them. Blank annotation fields are expected before annotation begins.

- Manifest rows: **60**.
- Platform counts: **{'youtube': 20, 'reddit': 20, 'twitter': 20}**.
- Validation issue records: **0**.
- Required columns present: **True**.
- A1/A2 blank initial labels: **True**.
- All integrity/policy checks passed: **True**.

Machine-readable issues: `reports\annotation_batch_v1_validation_errors.csv`.

No labels are assigned by this script. Non-empty annotations must be revalidated after human review.
