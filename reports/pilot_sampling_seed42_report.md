# Seed-42 Pilot Sampling Report

## Status

Created under the owner-approved policy version 0.2 dated 2026-10-19. This is an unlabeled manual-annotation sample for non-clinical text signals; it is not clinically validated and does not support diagnosis.

The previous seed-20261019 pilot artifact and report were not modified, deleted, or overwritten.

## Sources and verified counts

| Platform | Source file | Encoding | Source rows | Source platform values | Synthetic excluded | Selected |
|---|---|---|---:|---|---:|---:|
| youtube | `youtube_data set.csv` | `cp1252` | 1971 | youtube | 125 | 20 |
| reddit | `reddit_dataSet.csv` | `utf-8-sig` | 1302 | reddit | 0 | 20 |
| twitter | `twitter_data set.csv` | `utf-8-sig` | 1466 | twitter | 0 | 20 |

## Sampling method

- Fixed seed: **42**, using Python `random.Random(42)`.
- Independently sampled 20 eligible rows per platform.
- Eligibility required a non-empty unique source `record_id` and `is_synthetic` blank/false.
- No tier, keyword, prediction, probability, confidence, or model-related field was used.
- Output preserves source record IDs, platform names, and original post text.

## Synthetic handling

YouTube rows with `is_synthetic=TRUE` were excluded from the primary sample. The verified exclusion count is 125. Reddit and X/Twitter had zero rows marked synthetic in the inspected sources. No raw row was deleted.

## Duplicate handling

Duplicate diagnostics use NFKC normalization, whitespace collapse, trim, casefold, and truncated SHA-256. Raw post text is not repeated in this report.
- Selected records in any duplicate-text hash group: 0 records across 0 groups.
- Selected records in cross-platform duplicate groups: 0 records across 0 groups.
- Duplicate-linked records were not removed. Their groups must be kept together or excluded together in any future evaluation split.

Selected duplicate-group hashes:

- None selected.

## Validation

- Final data-row count: **60** (header excluded).
- Expected platform counts: YouTube=20, Reddit=20, X/Twitter=20.
- Required output columns were validated before writing.
- Source record IDs were non-empty and unique within each source; selected IDs are unique.
- No explicitly synthetic/augmented YouTube row was selected.
- All annotation fields were written blank: both annotator groups and `context_flags`.

## Pending work and limitations

Manual A1/A2 annotation and adjudication are pending. The sample is fixed and reproducible, not prevalence-representative. Existing tier provenance, legacy split semantics, and future leakage-safe evaluation policy remain unresolved. No model was trained and no split was changed.
