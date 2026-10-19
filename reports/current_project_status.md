# Current Project Status

**Inspection date:** 2026-10-19  
**Scope:** the three current raw datasets only: YouTube, Reddit, and X/Twitter.  
**Safety scope:** this is a non-clinical linguistic-signal research prototype. No conclusion here is a diagnosis or a clinical assessment.

## Executive status

The project is currently at the audit and annotation-readiness stage. The datasets have been inspected and their quality risks are documented, but there are no completed human-reviewed target labels, no validated cleaned/prepared dataset, no approved leakage-safe split policy, and no evidence of a trained or evaluated model.

**Most important blocker:** there is no approved, human-reviewed target-label dataset. The existing `tier` values and related fields have unresolved provenance and must not be used as verified targets.

## Files actually present

### Source scripts

- `src/dataset_audit.py` — dataset parsing and audit script.
- `src/data_quality_check.py` — data-quality and leakage-indicator audit script.

No `src/prepare_dataset.py` or model-training/evaluation script was found.

### Reports

- `reports/dataset_audit.md`
- `reports/dataset_audit.json`
- `reports/reddit_audit.json`
- `reports/label_provenance_report.md`
- `reports/upstream_evidence_report.md`
- `reports/label_scheme_proposal.md`
- `reports/annotation_guidelines.md`
- `reports/annotation_readiness_report.md`
- `reports/annotation_template.csv` — header-only annotation template
- `reports/data_quality_report.md`
- `reports/data_quality_report.json`
- `reports/dataset_preparation_status.md`
- `reports/baseline_model_readiness.md`

The following expected artifacts were not found:

- `reports/pilot_annotation_review.md`
- `Data/processed/pilot_annotation_template.csv`
- `src/prepare_dataset.py`

### Data directories

`Data/raw/` contains exactly these three CSV inputs:

| Filename | Size | Exact data rows | Verified format notes |
|---|---:|---:|---|
| `youtube_data set.csv` | 2,952,633 bytes | 1,971 | CSV, comma-delimited, `cp1252` detected |
| `reddit_dataSet.csv` | 4,362,785 bytes | 1,302 | CSV, comma-delimited, `utf-8-sig` detected |
| `twitter_data set.csv` | 1,727,760 bytes | 1,466 | CSV, comma-delimited, `utf-8-sig` detected |

`Data/processed/` exists but contains no files. The case-insensitive `data/` references resolve to the same Windows directory structure; no additional dataset inputs were used.

No README, requirements file, package metadata, notebook, environment example, or other project metadata was found by the workspace inspection.

## Verified dataset findings

### YouTube — `youtube_data set.csv`

- **Row count:** 1,971 exact rows.
- **Text and metadata:** the audit identifies `post_text`, `anonymized_user_id`, and `timestamp`; tier-related fields are present.
- **Missingness:** 0 missing/empty text values; 125 rows lack user IDs and timestamps; the audited tier-related fields have no missing labels for the primary observed fields.
- **Duplicates:** no exact duplicate full rows; 22 extra rows belong to normalized-text duplicate groups.
- **Synthetic/augmented data:** 125 rows are marked synthetic/augmentation. Parent-record metadata is present for 73 rows.
- **Splits:** `split` and `model_split` disagree for every row; `split` contains `silver`/`synthetic`, while `model_split` is `train` for all rows.
- **Leakage risks:** duplicate text, synthetic/parent relationships, and cross-platform overlap require explicit grouping rules before evaluation.

### Reddit — `reddit_dataSet.csv`

- **Row count:** 1,302 exact rows.
- **Text and metadata:** the audit identifies `post_text`, `anonymized_user_id`, and `timestamp`; tier-related fields are present.
- **Missingness:** 0 missing/empty text values, 0 missing users, 0 missing timestamps, and 0 invalid timestamps in the audit.
- **Duplicates:** no exact duplicate full rows; 48 extra rows belong to normalized-text duplicate groups in the data-quality report. The initial audit separately reports 47 duplicate-text rows, reflecting different duplicate-count conventions.
- **Synthetic/augmented data:** no rows are marked synthetic; no parent IDs are populated.
- **Splits:** `split` is `silver` for all rows and `model_split` is `test` for all rows; their disagreement is present for every row.
- **Leakage risks:** repeated users, duplicate text, and cross-platform overlap require grouping or exclusion policy before evaluation.

### X/Twitter — `twitter_data set.csv`

- **Row count:** 1,466 exact rows.
- **Text and metadata:** the audit identifies `post_text`, `anonymized_user_id`, and `timestamp`; tier-related fields are present.
- **Missingness:** 0 missing/empty text values, 0 missing users, 0 missing timestamps, and 0 invalid timestamps in the audit.
- **Duplicates:** no exact duplicate full rows; 32 extra rows belong to normalized-text duplicate groups in the data-quality report. The initial audit separately reports 30 duplicate-text rows, reflecting different duplicate-count conventions.
- **Synthetic/augmented data:** no rows are marked synthetic; no parent IDs are populated.
- **Splits:** `split` is `silver` for all rows and `model_split` is `test` for all rows; their disagreement is present for every row.
- **Leakage risks:** repeated users, duplicate text, and cross-platform overlap require grouping or exclusion policy before evaluation.

The reports also document five normalized text-hash groups shared between YouTube and Reddit, with no raw post text or private identifiers reproduced in this status report.

## Label meaning and annotation status

The meanings of existing tier values **0, 1, 2, and 3 have not been verified**. The reports state that the workspace contains no label dictionary, lexicon rules, correction logic, model-inference code, augmentation code, or upstream source documentation establishing their semantics.

Observed metadata such as `tier_source`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, confidence, and probability fields documents stored fields and processing-like tags only. It does not prove human annotation or ground truth. Their numeric frequencies are not interpreted here.

The project has a proposed annotation scheme and guidelines for non-clinical text signals, but they are not evidence that labels have been applied. No completed human annotations were found. The pilot review report is missing, and the available annotation template is header-only.

## Cleaned dataset and split policy

No cleaned or training-ready dataset exists. `Data/processed/` is empty, and `src/prepare_dataset.py` is absent.

No valid, approved train/validation/test split policy exists. The current `split` and `model_split` fields are documented but their construction and authority are unresolved; they disagree for every audited row. Existing duplicate-text, repeated-user, synthetic-parent, and cross-platform-overlap risks have been reported but not resolved through a reproducible partition policy.

## Model status

No model-training or evaluation script, checkpoint, metric report, or experiment artifact was found. Existing reports explicitly state that no model was trained. Therefore there are no verified baseline results, validation results, test results, or clinical claims to report.

## Next practical implementation task

Complete and approve a small manual annotation pilot before writing a preparation pipeline:

1. Resolve the outstanding annotation decisions and freeze the proposed label schema.
2. Create a separate fixed-seed pilot sample without using tier fields or model outputs to choose or assign labels.
3. Have two independent annotators label the same posts, recording confidence and review reasons.
4. Produce `reports/pilot_annotation_review.md` with agreement and disagreement analysis.
5. Use those results to finalize the guidelines, then implement a validated `src/prepare_dataset.py` using only approved human labels and an explicit leakage-safe grouping/split policy.

Do not train a model until these steps are complete and documented.

