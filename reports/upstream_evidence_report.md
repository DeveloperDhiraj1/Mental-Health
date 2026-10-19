# Step 3 — Upstream data and labeling evidence

Date of inspection: 2026-10-15 (Asia/Calcutta)

## Scope and safety

This investigation covered only the current datasets:

- Data/raw/youtube_data set.csv
- Data/raw/reddit_dataSet.csv
- Data/raw/twitter_data set.csv

On Windows, the project directory is named Data/raw; this is the same case-insensitive path represented in the request as data/raw.

No raw file, label, split assignment, source file, or model was modified. No web research, replacement download, cleaning, combination, or training was performed. No secret values were read or reported.

## Workspace and Git inspection

The workspace contains src/dataset_audit.py, the existing reports, the three CSVs, and empty Data/interim and Data/processed directories.

No README, notebook, requirements file, package metadata, environment example, Dockerfile, label dictionary, source URL note, model checkpoint note, or other upstream pipeline file was found.

No .env file or other environment configuration file was found. No configuration values were inspected.

The local .git directory does not exist. There is no local Git history, branch, or prior version available. No Git command changed the working tree.

## Search results

The requested filenames and provenance fields were searched across the project. The only source-code matches are in src/dataset_audit.py:

- Line 21 declares the three expected filenames.
- Line 134 identifies label-like and probability-like columns.
- Lines 150-156 read parent_record_id, split, and model_split and count disagreements.
- Lines 167 and 182 track text and parent IDs by split for leakage indicators.
- Lines 191-205 perform the strict CSV parsing pass.
- Lines 214-216 store observed label values and mark interpretation as unverified.
- Line 239 computes privacy-preserving cross-file hash overlap.
- Lines 262 and 267 write the existing audit reports and state the provenance caution.

There is no local implementation of lexicon rules, correction logic, model inference, augmentation, label mapping, source downloading, or split construction.

## Evidence recovered from the CSVs

All three CSV headers contain tier, tier_lexicon, tier_corrected, tier_model, tier_pred, tier_source, lex_hits, lex_conf, model_accept, model_split, is_synthetic, aug_method, parent_record_id, model_conf, tier_confidence, and prob_tier_0 through prob_tier_3. This proves that these fields were stored in the current files. It does not prove what code generated them, what model was used, or that any field is ground truth.

### YouTube

- 1,971 exact rows.
- tier_source: lexicon=1,846, augmentation=125.
- is_synthetic: FALSE=1,846, TRUE=125.
- aug_method: original=1,846, css=51, generation=41, eda_delete=29, eda_synonym=4.
- parent_record_id is populated for 73 rows.
- split: silver=1,846, synthetic=125.
- model_split: train=1,971.
- tier_pred is empty for all rows.
- tier_model is empty for 125 rows, matching the observed synthetic subset.

Verified conclusion: YouTube contains an explicitly marked augmented/synthetic subset and original rows marked lexicon-sourced. The augmentation implementation and label-transfer rule are absent.

Reasonable inference: split appears to encode provenance or data status, while model_split appears to encode model use. This is not documented fact.

### Reddit

- 1,302 exact rows.
- tier_source: lexicon=1,297, corrected=5.
- is_synthetic: FALSE=1,302.
- aug_method: original=1,302.
- parent_record_id is empty for all rows.
- split: silver=1,302.
- model_split: test=1,302.
- model_accept: FALSE=1,302.

Verified conclusion: Reddit rows are tagged lexicon-sourced or corrected, but the lexicon, correction rules, annotator information, and acceptance logic are absent.

Reasonable inference: model_split=test may be an evaluation partition, but this cannot be relied on without split-construction evidence.

### X/Twitter

- 1,466 exact rows.
- tier_source: lexicon=1,449, corrected=17.
- is_synthetic: FALSE=1,466.
- aug_method: original=1,466.
- parent_record_id is empty for all rows.
- split: silver=1,466.
- model_split: test=1,466.
- model_accept: FALSE=1,466.

Verified conclusion: X rows are tagged lexicon-sourced or corrected, but the rules and documentation behind either tag are absent.

Reasonable inference: X and Reddit appear to share a metadata convention, but this does not establish that their labels have the same meaning.

## Label provenance assessment

| Field or stage | Local evidence | Unproven |
|---|---|---|
| tier | A populated four-valued field exists | Class meanings, target status, annotation source |
| tier_lexicon | Source tags and lex_hits/lex_conf fields exist | Lexicon contents, thresholds, aggregation, validation |
| tier_corrected | A corrected field and corrected source tag exist | Manual versus rule-based process and verification |
| tier_model | A model-like tier field and model_conf exist | Model identity, checkpoint, target, and inference process |
| tier_pred and probabilities | Prediction-like fields exist | Whether they correspond to tier; they are not ground truth |
| tier_source | Stored source tags exist | Code or policy that assigned them |
| model_accept | All current rows are FALSE | Meaning of acceptance and why no rows are accepted |
| YouTube augmentation | 125 rows have synthetic/augmentation metadata | Generation code and label-transfer policy |

No local evidence establishes human annotation or verified clinical ground truth. The meanings of tier values 0, 1, 2, and 3 remain unresolved and are not inferred from frequencies or predictions.

## Split-construction evidence

The fields disagree for every row:

- YouTube: split is silver or synthetic; model_split is always train.
- Reddit: split=silver; model_split=test.
- X: split=silver; model_split=test.

The only code examining this relationship is src/dataset_audit.py:151-156. No local code constructs either field or documents which is authoritative. Therefore split cannot safely be assumed to be a train/test split, and model_split cannot safely be assumed to be a valid evaluation partition.

No split assignments were changed.

## Duplicate and shared-text investigation

The existing audit reports these within-file duplicate-text row counts:

- YouTube: 19
- Reddit: 47
- X: 30

The audit reports three Reddit/YouTube shared text-hash groups, zero Reddit/X groups, zero YouTube/X groups, and zero cross-file user-hash overlap.

The three Reddit/YouTube shared hash groups were checked against stored metadata without exposing text or identifiers. All observed rows were tier=0, tier_source=lexicon, is_synthetic=FALSE, and split=silver.

This verifies possible cross-dataset text duplication. It does not establish whether one dataset was derived from the other or what tier 0 means. No records were removed or changed.

## Final evidence classification

### Verified

- No upstream labeling or data-generation implementation exists in the local workspace.
- The CSVs contain the listed provenance, model-output, augmentation, and split fields.
- YouTube has 125 explicitly synthetic/augmented rows.
- Reddit and X contain rows tagged corrected.
- All split and model_split values disagree row-by-row.
- Three Reddit/YouTube shared text-hash groups exist.
- No local artifact defines the semantic mapping of tiers 0-3.

### Reasonable inferences, not confirmed facts

- tier_lexicon and lex_hits likely relate to lexicon processing.
- tier_corrected and tier_source=corrected likely identify a later correction stage.
- tier_model, tier_pred, and probability fields likely represent model outputs.
- YouTube aug_method and parent IDs likely identify generated variants and source records.
- model_split may represent model-use partitioning while split may represent data provenance.

These inferences must not be used as label definitions or training assumptions without upstream evidence.

## Unresolved questions

1. What do classes 0, 1, 2, and 3 mean?
2. What lexicon and thresholds produced tier_lexicon, lex_hits, and lex_conf?
3. What process created tier_corrected?
4. What model produced tier_model, tier_pred, and probability fields?
5. Why is model_accept=FALSE for every row?
6. Which field is authoritative for train/test/evaluation use?
7. How were YouTube synthetic labels transferred from parent records?
8. Are the shared Reddit/YouTube texts expected source overlap or leakage?
9. Are labels comparable across YouTube, Reddit, and X?

## Recommended next action

Do not train or combine the datasets yet. Obtain the upstream data-generation artifacts from the dataset creator or original project environment: class-definition documentation, lexicon/rule files, correction code, model/checkpoint metadata, augmentation code, and split-construction code. Until those artifacts are available, treat tier as an unresolved processing label rather than verified ground truth.

This remains a non-clinical research prototype for linguistic-signal analysis and does not support diagnostic conclusions.
