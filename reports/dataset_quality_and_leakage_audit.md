# Dataset Quality and Leakage Audit

## Scope and safety

Audited the three current raw CSV files only. Raw data was read without modification; no labels were assigned, rows deleted, splits changed, or model trained. Reports use hashes/counts rather than raw post text or user identifiers. Labels are non-clinical text-signal annotations, not diagnoses.

## Current files and counts

| Platform | File | Encoding | Rows | Columns |
|---|---|---|---:|---:|
| youtube | `Data\raw\youtube_data set.csv` | cp1252 | 1971 | 51 |
| reddit | `Data\raw\reddit_dataSet.csv` | utf-8-sig | 1302 | 51 |
| twitter | `Data\raw\twitter_data set.csv` | utf-8-sig | 1466 | 51 |
| combined | three files | — | **4739** | common columns: 51 |

The combined row count is a count of rows, not a license to concatenate them for modeling; platform and provenance must remain explicit.

## Quality findings

The machine-readable metrics file contains exact counts for missing IDs/text, duplicates, synthetic metadata, and column presence.

### youtube
- Missing record IDs: 0; missing text: 0.
- Synthetic/augmented indicators: **125** rows (explicit `is_synthetic`, `parent_record_id`, or `aug_method` evidence).
- Exact duplicate full rows: 0 extra rows; duplicate record IDs: 0 extra rows.
### reddit
- Missing record IDs: 0; missing text: 0.
- Synthetic/augmented indicators: **0** rows (explicit `is_synthetic`, `parent_record_id`, or `aug_method` evidence).
- Exact duplicate full rows: 0 extra rows; duplicate record IDs: 0 extra rows.
### twitter
- Missing record IDs: 0; missing text: 0.
- Synthetic/augmented indicators: **0** rows (explicit `is_synthetic`, `parent_record_id`, or `aug_method` evidence).
- Exact duplicate full rows: 0 extra rows; duplicate record IDs: 0 extra rows.

## Exact and near-duplicate text

- Normalized exact-text groups across the combined data: **64** groups with more than one record.
- Cross-platform normalized exact-text groups: **5** groups involving 16 records.
- Conservative near-duplicate candidates found: **74**. Candidates are in `reports\duplicate_review_candidates.csv` when non-empty; only hashes/IDs are stored.
- Duplicate records were not removed. Parent/augmented relationships and duplicate groups must be kept together or explicitly controlled in later evaluation.

## Labels and target leakage

The raw datasets contain legacy tier, lexicon, correction, model, confidence/probability, split, and augmentation columns. These are metadata or generated signals, not verified ground truth. The approved human-reviewed labels are stored separately in the 60-record adjudication workbook; they are not present as a raw-dataset target column.

Potential target leakage if used as features: `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, `tier_source`, `tier_confidence`, `lex_conf`, `lex_hits`, `corr_conf`, `model_conf`, `model_accept`, `prob_tier_0`–`prob_tier_3`, and any derived text/model fields such as `text_muril`, `text_negation`, or `ruminative_repetition` if they were generated using labels or post-hoc model outputs. `split` and `model_split` are not safe evaluation partitions because their provenance is unresolved and prior audits found disagreement.

## Grouping and evaluation risks

- `anonymized_user_id`, `record_id`, `parent_id`, `parent_record_id`, timestamps, platform, and augmentation metadata are available in the schemas and require explicit grouping/time policies.
- The audit found 3780 unique non-empty anonymized-user identifiers across the combined files; 0 identifiers occur on all three platforms. Values are intentionally not printed.
- User overlap, duplicate text, cross-platform copies, and synthetic-parent relationships can leak information across train and evaluation sets.
- Do not expose user IDs in reports; use them only locally for grouping diagnostics.

## Annotation coverage and pilot sufficiency

The current human-reviewed pilot covers 60 records out of **4739** raw records (1.27%). The latest validation reports 59 completed adjudications and 1 unresolved review case. The original A1/A2 labels mostly do not follow the approved vocabulary, so the pilot is not yet a defensible training/evaluation target without further review and agreement work. It is suitable for methodology testing, not performance claims.

## Safe next steps

1. Resolve the remaining adjudication issue and decide how the two canonical-text mismatches are handled.
2. Complete/verify policy-conforming independent annotations and rerun IAA.
3. Define a leakage-safe split policy: group by user, normalized duplicate text, and augmentation parent; keep cross-platform duplicate groups together; document time/platform handling.
4. Only after approval, create a separate training artifact using human-reviewed labels and feature exclusion rules.

## Reproducibility

Run from the project root:

```powershell
python src\dataset_quality_leakage_audit.py
```

This script reads the three raw CSVs with strict CSV parsing, detects UTF-8/CP1252 decoding, computes exact counts and normalized SHA-256 text hashes, and writes the two reports plus duplicate candidates without changing inputs.

## Decision

**Safe now:** review the audit, resolve annotation/mismatch issues, and document grouping/split policy. **Blocked:** model training, target construction from legacy tiers, and leakage-sensitive evaluation until human-label quality and split policy are approved.
