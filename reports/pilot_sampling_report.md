# Pilot Sampling Report

## Status

The project owner approved the proposed four-label pilot policy before sampling. This report documents a reproducible, unlabeled sample only. The labels describe non-clinical linguistic signals, not diagnoses or clinical severity.

Raw CSVs, existing annotations, and split assignments were not modified. No labels were assigned.

## Sampling method

- Random seed: **20261019** using Python `random.Random`.
- Sampling unit: one source row, sampled independently within each platform.
- Eligibility: source `is_synthetic` is blank/false; no tier, keyword, prediction, probability, or model field was used.
- Target: 20 YouTube + 20 Reddit + 20 X/Twitter = 60 rows.
- Sampling was performed from the raw rows after eligibility filtering; source order was not used as a selection criterion.

## Output

- File: `Data\processed\pilot_annotation.csv`
- Exact rows: **60**
- Annotation fields are blank for both annotators.
- Context flags are blank for human entry and are separate from signal labels.

| Platform | Source rows | Eligible original/unspecified | Synthetic excluded | Selected |
|---|---:|---:|---:|---:|
| youtube | 1971 | 1846 | 125 | 20 |
| reddit | 1302 | 1302 | 0 | 20 |
| twitter | 1466 | 1466 | 0 | 20 |

## Synthetic-row handling

Explicitly synthetic/augmented rows were excluded from the primary pilot. This includes the 125 marked YouTube synthetic rows documented in the data-quality reports. No synthetic row was silently deleted from the raw data; it was only ineligible for this pilot sample.

## Duplicate and shared-hash handling

Text hashes use Unicode NFKC normalization, collapsed whitespace, trimming, casefolding, and truncated SHA-256. Raw post text is not printed in this report.
- Selected records belonging to any within-file or cross-platform duplicate hash group: 13 source records across 3 hash groups.
- Selected records in cross-platform duplicate hash groups: 0 source records across 0 hash groups.
- Linked records were not removed from the pilot; their hashes are flagged here so they must be kept together or excluded as a group from any later evaluation partition.

Selected duplicate-group hashes (privacy-preserving):

- `0807d06edde7cb51` — 4 source records; platforms: twitter
- `7e1305e4d6d145a3` — 3 source records; platforms: reddit
- `acfb277febd03263` — 6 source records; platforms: twitter

## Annotation instructions

Two annotators must independently fill the label, confidence, review, and context fields. They must remain blind to legacy tier/model metadata. Use only the approved four-label policy; do not treat any label as a diagnosis or severity level.

## Limitations

This is a fixed-size pilot, not a representative estimate of platform prevalence. It does not resolve legacy tier provenance, establish a leakage-safe train/test split, or validate the proposed labels. The sample must be reviewed for annotation agreement before any larger annotation or modeling decision.
