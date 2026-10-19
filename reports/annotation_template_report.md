# Annotation Template Report

## Status

This report describes a separate, unlabeled annotation artifact generated from the three current raw CSVs. Raw files were read only and were not modified, relabeled, split, or deduplicated.

The template does not use `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, keywords, confidence/probability fields, or any other legacy metadata to assign labels. All annotation fields are blank for human completion.

## Output

- Template: `Data\processed\annotation_template.csv`
- Total template rows: **4739**
- Output encoding: UTF-8 CSV with standard quoting.
- Output columns: `record_id`, `platform`, `post_text`, `record_type`, `annotator_label`, `confidence`, `needs_review`, `review_reason`.

## Counts and identifier checks

| Platform | Source rows | Template rows | Synthetic/augmented | Fallback IDs | IDs unique |
|---|---:|---:|---:|---:|---|
| YouTube | 1971 | 1971 | 125 | 0 | yes |
| Reddit | 1302 | 1302 | 0 | 0 | yes |
| X/Twitter | 1466 | 1466 | 0 | 0 | yes |

## Synthetic-record handling

All source rows are included, including the explicitly marked synthetic or augmented YouTube rows. They are marked in `record_type` as `synthetic_or_augmented`; non-synthetic or blank-source-status rows are marked `original_or_unspecified`. No row was silently excluded.

The `record_type` value is descriptive metadata copied from the source `is_synthetic` flag. It is not an annotation label and must not be used to infer a linguistic-signal class.

## Identifier handling

The existing non-empty source `record_id` is preserved. If a source row has no record ID, the script creates a deterministic platform-and-row fallback only in the annotation artifact; it never writes back to the raw CSV. Duplicate output IDs cause the script to fail rather than be silently altered.

## Annotation safety

`annotator_label` must be assigned by a human using the approved annotation guidelines. The labels describe observable non-clinical linguistic signals, not a person's diagnosis, identity, or clinical severity.
