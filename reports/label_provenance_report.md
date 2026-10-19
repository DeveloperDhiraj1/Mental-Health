# Step 2 — Label provenance investigation

## Scope and evidence limits

This investigation covers only:

- Data/raw/youtube_data set.csv
- Data/raw/reddit_dataSet.csv
- Data/raw/twitter_data set.csv

No raw file was modified. No rows were removed, relabeled, combined, split, or trained on.

The workspace contains no README, metadata file, notebook, label dictionary, lexicon implementation, correction script, model-inference script, or augmentation script. The only project code found is src/dataset_audit.py. Consequently, the strongest available evidence is the metadata embedded in the CSVs themselves; generation logic and the semantic mapping of classes remain unresolved.

The audit script identifies the current input files at src/dataset_audit.py:21, collects tier-related columns at src/dataset_audit.py:134, compares split and model_split at src/dataset_audit.py:151-156, and explicitly records label provenance as unverified at src/dataset_audit.py:214-216.

## Verified field-level observations

All three files contain:

tier, tier_lexicon, tier_corrected, tier_model, tier_pred, tier_source, tier_confidence, model_conf, prob_tier_0 through prob_tier_3, split, model_split, is_synthetic, aug_method, and parent_record_id.

These names are evidence of stored processing stages or metadata. They do not, by themselves, establish what the stages did or whether any output is ground truth.

### YouTube — youtube_data set.csv

- Exact rows: 1,971.
- tier: 0=1,545, 2=255, 3=89, 1=82.
- tier_lexicon, tier_corrected, and tier have the same distribution.
- tier_model: 0=1,562, 2=214, 1=63, 3=7, plus 125 empty values.
- tier_pred: empty for all 1,971 rows.
- tier_source: lexicon=1,846, augmentation=125.
- is_synthetic: FALSE=1,846, TRUE=125.
- aug_method: original=1,846, css=51, generation=41, eda_delete=29, eda_synonym=4.
- parent_record_id is populated for 73 rows; the remaining 1,898 are empty.
- split: silver=1,846, synthetic=125.
- model_split: train=1,971.
- model_accept: FALSE=1,971.

Evidence-based interpretation: 1,846 rows are marked as lexicon-sourced and 125 as augmentation/synthetic. The 125 synthetic rows have augmentation methods and parent-record metadata. This supports classifying those rows as generated or augmented records, but the workspace does not explain how their tier values were assigned. The equal tier/tier_lexicon distributions do not prove that tier is ground truth.

### Reddit — reddit_dataSet.csv

- Exact rows: 1,302.
- tier: 0=1,189, 2=67, 1=24, 3=22.
- tier_lexicon: 0=1,184, 2=67, 1=29, 3=22.
- tier_corrected: 0=1,189, 2=67, 1=24, 3=22.
- tier_model: 0=1,254, 2=30, 3=11, 1=7.
- tier_pred: 0=1,194, 2=85, 1=16, 3=7.
- tier_source: lexicon=1,297, corrected=5.
- is_synthetic: FALSE=1,302.
- aug_method: original=1,302.
- parent_record_id: empty for all rows.
- split: silver=1,302.
- model_split: test=1,302.
- model_accept: FALSE=1,302.

Evidence-based interpretation: The file records 1,297 lexicon-sourced rows and 5 rows marked corrected. The names suggest processing stages, but no correction rule, annotator information, or verification procedure exists in the workspace. tier_pred and probability fields must remain model-output metadata, not target labels.

### X/Twitter — twitter_data set.csv

- Exact rows: 1,466.
- tier: 2=529, 1=521, 0=392, 3=24.
- tier_lexicon: 2=534, 1=506, 0=403, 3=23.
- tier_corrected: 2=529, 1=521, 0=392, 3=24.
- tier_model: 2=513, 1=493, 0=448, 3=12.
- tier_pred: 0=944, 2=276, 1=224, 3=22.
- tier_source: lexicon=1,449, corrected=17.
- is_synthetic: FALSE=1,466.
- aug_method: original=1,466.
- parent_record_id: empty for all rows.
- split: silver=1,466.
- model_split: test=1,466.
- model_accept: FALSE=1,466.

Evidence-based interpretation: The file records mostly lexicon-sourced rows and 17 rows marked corrected. There is no project evidence identifying human annotators, correction rules, or verified ground truth.

## Meaning of tier values

The meanings of tier values 0, 1, 2, and 3 are unresolved.

This report deliberately does not map numeric values to mental-health categories. The observed frequencies, field names, lexicon hits, probability columns, or examples cannot safely establish class semantics. In particular:

- tier is not demonstrated to be human annotation.
- tier_lexicon is not demonstrated to be a validated lexicon label.
- tier_corrected is not demonstrated to reflect human correction.
- tier_model is not demonstrated to be a specific model output or to use a documented target.
- tier_pred and prob_tier_* are prediction metadata and must not be treated as verified labels.
- tier_source values (lexicon, corrected, augmentation) are provenance tags, but their generating code is absent.
- Confidence fields (lex_conf, corr_conf, model_conf, tier_confidence) have no documented calibration or interpretation in the workspace.

## Human, lexicon, model, corrected, and augmented provenance

| Provenance category | Finding | Evidence |
|---|---|---|
| Human-annotated | Not established for any dataset | No annotation metadata, annotator IDs, guidelines, or labeling code found |
| Lexicon-generated | Strongly indicated for rows with tier_source=lexicon and populated lex_hits/lex_conf | CSV fields and observed source distributions; generation rules absent |
| Corrected | Processing stage is indicated for rows with tier_source=corrected and tier_corrected | CSV fields; correction logic absent |
| Model-generated | Candidate model-output fields exist (tier_model, tier_pred, model_conf, probabilities) | CSV schema; model code and model identity absent |
| Augmented/synthetic | Strongly indicated for YouTube's 125 rows with is_synthetic=TRUE, tier_source=augmentation, non-original aug_method, and populated parent IDs | YouTube CSV metadata |
| Verified clinical ground truth | Not established | No validation or annotation documentation found |

## split versus model_split

The fields have different values in every row:

- YouTube: split is silver or synthetic; model_split is train for all rows.
- Reddit: split=silver; model_split=test.
- X: split=silver; model_split=test.

The audit found disagreements in all 1,971 YouTube rows, all 1,302 Reddit rows, and all 1,466 X rows. The field values suggest that split may describe a data/provenance tier while model_split may describe a model-use partition, but this is an inference from names and values, not documented fact. No code explains which field is authoritative, when it was assigned, or whether either field was independently constructed.

No split assignments were changed.

## Duplicate text and shared Reddit/YouTube hashes

The audit reports these within-file duplicate-text row counts:

- YouTube: 19 duplicate-text rows
- Reddit: 47 duplicate-text rows
- X: 30 duplicate-text rows

The audit also reports no repeated text hashes across the audited split values within any dataset.

The privacy-preserving cross-file comparison found:

- Reddit/YouTube: 3 shared text-hash groups
- Reddit/X: 0 shared text-hash groups
- YouTube/X: 0 shared text-hash groups
- Cross-file user-hash overlap: 0 for every pair

For the three Reddit/YouTube shared text-hash groups, the observed rows were all:

- tier=0
- tier_source=lexicon
- is_synthetic=FALSE
- split=silver

This establishes possible cross-dataset duplication, not the meaning of tier 0. The shared text could represent the same source material, reposting, or collection overlap; the workspace contains no source-linkage documentation. The records were not removed or altered.

## Conclusions

1. The files contain substantial evidence of automated labeling and preprocessing metadata.
2. YouTube contains a clearly marked augmented/synthetic subset of 125 rows.
3. Reddit and X contain mostly lexicon-sourced rows with small corrected subsets.
4. No available project artifact proves that any tier value is human-verified ground truth.
5. No available project artifact defines the semantic meaning of tiers 0–3.
6. A responsible train/test interpretation cannot be made until split and model_split are documented.
7. The datasets should not yet be combined under one classification target.

## Unresolved questions and required evidence

- What do classes 0–3 mean?
- What lexicon and threshold produced tier_lexicon, lex_hits, and lex_conf?
- What process produced tier_corrected and the corrected source tag?
- What model produced tier_model, tier_pred, and the probability columns?
- Why are all model_accept values FALSE?
- What do silver, synthetic, train, and test mean operationally?
- Is YouTube augmentation label-preserving, and how were parent labels transferred?
- Are the shared Reddit/YouTube texts expected cross-platform duplicates?
- Are labels comparable across YouTube, Reddit, and X?

Required next evidence is the upstream labeling/augmentation pipeline or dataset documentation, including class definitions, lexicon rules, correction policy, model identity/checkpoint, split-construction code, and augmentation-label transfer logic.

## Recommended next step

Do a provenance-only review of the upstream data-generation artifacts. Freeze a written label dictionary and split policy, and separately flag or exclude augmentation/duplicate groups for a later leakage review. Only after that review should a modeling plan be designed. This remains a non-clinical linguistic-signal research prototype; no diagnostic interpretation is supported.
