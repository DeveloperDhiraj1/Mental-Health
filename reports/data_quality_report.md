# Data-quality assessment

Scope: read-only assessment of the three current raw datasets. No raw file was modified, relabeled, split, or deleted.

Tier-related columns are reported as existing metadata only. Numeric values are not assigned mental-health meanings and are not treated as verified ground truth.

## Dataset summaries

### youtube: youtube_data set.csv

- Path: C:\Users\dhira\OneDrive\Desktop\Mental Health\Data\raw\youtube_data set.csv
- Size: 2,952,633 bytes
- Encoding detected: cp1252
- Exact row count: 1,971
- Columns (51): platform_raw, anonymized_user_id, timestamp, post_text, source_ref, record_id, month, day, hour, weekday, is_working_hour, is_weekend, post_length_chars, post_length_tokens, score, reply_count, share_count, parent_id, raw_meta_json, post_text_clean, lang, tier_lexicon, lex_conf, lex_hits, lex_topical, tier_corrected, corr_conf, tier_model, model_conf, model_accept, tier, tier_source, tier_confidence, split, is_synthetic, aug_method, parent_record_id, aug_version, temporal_mask, text_muril, text_negation, translit_map_hits, emoji_sub_count, ruminative_repetition, model_split, platform, tier_pred, prob_tier_0, prob_tier_1, prob_tier_2, prob_tier_3
- Metadata columns: {'text': 'post_text', 'record_id': 'record_id', 'user_id': 'anonymized_user_id', 'timestamp': 'timestamp', 'platform': 'platform'}
- Missing values: {'missing_text': 0, 'whitespace_only_text': 0, 'missing_record_id': 0, 'missing_user_id': 125, 'missing_timestamp': 125}
- Timestamp metadata: {'valid_count': 1846, 'invalid_count': 0, 'min': '2019-12-31T16:43:35', 'max': '2026-06-26T06:53:42'}
- Platform values: youtube=1971
- User metadata: {'distinct_nonempty_user_ids': 1774, 'repeated_user_rows': 72}
- Record ID metadata: {'distinct_nonempty_record_ids': 1971, 'duplicate_record_id_extra_rows': 0, 'all_record_ids_unique': True}
- Exact duplicate rows: 0 extra rows across 0 hash groups
- Normalized duplicate post_text: 22 extra rows across 20 hash groups
- CSV diagnostics: 0 width anomalies; 0 strict parser errors

#### Existing tier-related distributions

- tier_lexicon: 2=255, 0=1545, 1=82, 3=89
- tier_corrected: 2=255, 0=1545, 1=82, 3=89
- tier_model: 2=214, 1=63, 0=1562, 3=7, <empty>=125
- tier: 2=255, 0=1545, 1=82, 3=89
- tier_source: lexicon=1846, augmentation=125
- tier_confidence: 0.68=119, 0.81=6, 0.7793=5, 0.8179=4, 0.856=4, 0.8564=4, 0.8673=4, 0.8717=4, 0.8927=4, 0.902=4 (top 10; 1520 distinct values in JSON)
- tier_pred: <empty>=1971
- prob_tier_0: <empty>=1971
- prob_tier_1: <empty>=1971
- prob_tier_2: <empty>=1971
- prob_tier_3: <empty>=1971

#### Split metadata

- split: silver=1846, synthetic=125
- model_split: train=1971
- disagreement rows: 1971

#### YouTube synthetic/augmented metadata

- is_synthetic: FALSE=1846, TRUE=125
- synthetic row count: 125
- synthetic rows, tier: 1=52, 3=73
- synthetic rows, tier_source: augmentation=125
- synthetic rows, aug_method: css=51, eda_delete=29, eda_synonym=4, generation=41
- synthetic rows, split: synthetic=125
- synthetic rows, model_split: train=125
- synthetic rows, parent_record_id: hash:188a12b43fda2f3c=1, hash:8e47196efd228384=3, hash:c9e8fd3c1c11fc65=3, hash:f9f4a30776139c8c=2, hash:52c09fa385ba3ec9=2, hash:cefd83952d339cc3=4, hash:f7b5c5e94ee821a2=3, hash:e278dea1b5c16f3d=1, hash:1dadfdc2dc0de668=3, hash:2fc93331f9783ce3=1, hash:05041c8d7aace01c=3, hash:3144b2187e159298=4, hash:29b098be31b9dc63=3, hash:1b46f9ddaf4c6615=5, hash:b1d90b881884949f=2, hash:98885449cde1f7ee=5, hash:c4370e9131997174=3, hash:fd27b1c63bf5ef08=4, <empty>=52, hash:aaf1f097e0df00fe=3, hash:5b9a8f0e7cb66f9d=1, hash:64270abdff0617b9=4, hash:98c30eeacb5f28d0=1, hash:41bdd152727d572c=1, hash:7af5949fb0a67c23=1, hash:abd20d84c840e1e4=1, hash:953513cfc823dbf9=3, hash:5f09f0bb17f86898=1, hash:566cee02cd9de7ee=1, hash:e04c399caeb260ee=1, hash:e18a4309df430de6=3

### reddit: reddit_dataSet.csv

- Path: C:\Users\dhira\OneDrive\Desktop\Mental Health\Data\raw\reddit_dataSet.csv
- Size: 4,362,785 bytes
- Encoding detected: utf-8-sig
- Exact row count: 1,302
- Columns (51): platform_raw, anonymized_user_id, timestamp, post_text, source_ref, record_id, month, day, hour, weekday, is_working_hour, is_weekend, post_length_chars, post_length_tokens, score, reply_count, share_count, parent_id, raw_meta_json, post_text_clean, lang, tier_lexicon, lex_conf, lex_hits, lex_topical, tier_corrected, corr_conf, tier_model, model_conf, model_accept, tier, tier_source, tier_confidence, split, is_synthetic, aug_method, parent_record_id, aug_version, temporal_mask, text_muril, text_negation, translit_map_hits, emoji_sub_count, ruminative_repetition, model_split, platform, tier_pred, prob_tier_0, prob_tier_1, prob_tier_2, prob_tier_3
- Metadata columns: {'text': 'post_text', 'record_id': 'record_id', 'user_id': 'anonymized_user_id', 'timestamp': 'timestamp', 'platform': 'platform'}
- Missing values: {'missing_text': 0, 'whitespace_only_text': 0, 'missing_record_id': 0, 'missing_user_id': 0, 'missing_timestamp': 0}
- Timestamp metadata: {'valid_count': 1302, 'invalid_count': 0, 'min': '2022-02-15T14:24:00', 'max': '2026-06-26T11:41:57'}
- Platform values: reddit=1302
- User metadata: {'distinct_nonempty_user_ids': 812, 'repeated_user_rows': 490}
- Record ID metadata: {'distinct_nonempty_record_ids': 1302, 'duplicate_record_id_extra_rows': 0, 'all_record_ids_unique': True}
- Exact duplicate rows: 0 extra rows across 0 hash groups
- Normalized duplicate post_text: 48 extra rows across 22 hash groups
- CSV diagnostics: 0 width anomalies; 0 strict parser errors

#### Existing tier-related distributions

- tier_lexicon: 0=1184, 1=29, 2=67, 3=22
- tier_corrected: 0=1189, 1=24, 2=67, 3=22
- tier_model: 0=1254, 1=7, 3=11, 2=30
- tier: 0=1189, 1=24, 2=67, 3=22
- tier_source: lexicon=1297, corrected=5
- tier_confidence: 0.7574=4, 0.8529=4, 0.8699=4, 0.8825=4, 0.6262=3, 0.7184=3, 0.75=3, 0.754=3, 0.7816=3, 0.8046=3 (top 10; 1105 distinct values in JSON)
- tier_pred: 0=1194, 1=16, 2=85, 3=7
- prob_tier_0: 0.9966=19, 0.9952=17, 0.9965=17, 0.996=16, 0.9944=15, 0.9962=15, 0.9968=14, 0.9969=14, 0.9945=13, 0.9958=13 (top 10; 554 distinct values in JSON)
- prob_tier_1: 0.0003=123, 0.0002=122, 0.0004=87, 0.0005=87, 0.0001=65, 0.0008=49, 0.0007=42, 0.0006=40, 0.0009=29, 0.001=25 (top 10; 262 distinct values in JSON)
- prob_tier_2: 0.0015=29, 0.001=25, 0.0014=23, 0.0028=20, 0.0012=18, 0.002=18, 0.0023=18, 0.0026=18, 0.0024=17, 0.003=17 (top 10; 461 distinct values in JSON)
- prob_tier_3: 0=499, 0.0001=347, 0.0002=96, 0.0003=48, 0.0004=26, 0.0005=25, 0.0006=19, 0.0007=14, 0.0009=12, 0.0008=8 (top 10; 137 distinct values in JSON)

#### Split metadata

- split: silver=1302
- model_split: test=1302
- disagreement rows: 1302

#### Synthetic/augmented metadata

- is_synthetic: FALSE=1302
- synthetic row count: 0

### x: twitter_data set.csv

- Path: C:\Users\dhira\OneDrive\Desktop\Mental Health\Data\raw\twitter_data set.csv
- Size: 1,727,760 bytes
- Encoding detected: utf-8-sig
- Exact row count: 1,466
- Columns (51): platform_raw, anonymized_user_id, timestamp, post_text, source_ref, record_id, month, day, hour, weekday, is_working_hour, is_weekend, post_length_chars, post_length_tokens, score, reply_count, share_count, parent_id, raw_meta_json, post_text_clean, lang, tier_lexicon, lex_conf, lex_hits, lex_topical, tier_corrected, corr_conf, tier_model, model_conf, model_accept, tier, tier_source, tier_confidence, split, is_synthetic, aug_method, parent_record_id, aug_version, temporal_mask, text_muril, text_negation, translit_map_hits, emoji_sub_count, ruminative_repetition, model_split, platform, tier_pred, prob_tier_0, prob_tier_1, prob_tier_2, prob_tier_3
- Metadata columns: {'text': 'post_text', 'record_id': 'record_id', 'user_id': 'anonymized_user_id', 'timestamp': 'timestamp', 'platform': 'platform'}
- Missing values: {'missing_text': 0, 'whitespace_only_text': 0, 'missing_record_id': 0, 'missing_user_id': 0, 'missing_timestamp': 0}
- Timestamp metadata: {'valid_count': 1466, 'invalid_count': 0, 'min': '2024-09-15T06:36:27', 'max': '2026-06-26T11:55:56'}
- Platform values: twitter=1466
- User metadata: {'distinct_nonempty_user_ids': 1194, 'repeated_user_rows': 272}
- Record ID metadata: {'distinct_nonempty_record_ids': 1466, 'duplicate_record_id_extra_rows': 0, 'all_record_ids_unique': True}
- Exact duplicate rows: 0 extra rows across 0 hash groups
- Normalized duplicate post_text: 32 extra rows across 21 hash groups
- CSV diagnostics: 0 width anomalies; 0 strict parser errors

#### Existing tier-related distributions

- tier_lexicon: 0=403, 2=534, 3=23, 1=506
- tier_corrected: 0=392, 2=529, 3=24, 1=521
- tier_model: 0=448, 3=12, 2=513, 1=493
- tier: 0=392, 2=529, 3=24, 1=521
- tier_source: lexicon=1449, corrected=17
- tier_confidence: 1=11, 0.7989=5, 0.7464=4, 0.7544=4, 0.9053=4, 0.6327=3, 0.6786=3, 0.6908=3, 0.7251=3, 0.7639=3 (top 10; 1272 distinct values in JSON)
- tier_pred: 0=944, 2=276, 1=224, 3=22
- prob_tier_0: 0.0012=9, 0.0007=8, 0.0013=8, 0.9902=8, 0.9965=7, 0.9972=7, 0.9973=7, 0.9976=7, 0.0002=6, 0.0003=6 (top 10; 1076 distinct values in JSON)
- prob_tier_1: 0.0001=244, 0.0002=134, 0.0003=82, 0=61, 0.0004=53, 0.0006=28, 0.0005=27, 0.0007=18, 0.0008=17, 0.0009=13 (top 10; 574 distinct values in JSON)
- prob_tier_2: 0.0008=23, 0.0022=18, 0.0006=17, 0.0014=15, 0.0007=14, 0.0003=13, 0.0009=12, 0.002=12, 0.0004=11, 0.0017=11 (top 10; 848 distinct values in JSON)
- prob_tier_3: 0=274, 0.0001=231, 0.0002=106, 0.0003=78, 0.0005=42, 0.0006=39, 0.0004=31, 0.0008=22, 0.001=22, 0.0007=19 (top 10; 330 distinct values in JSON)

#### Split metadata

- split: silver=1466
- model_split: test=1466
- disagreement rows: 1466

#### Synthetic/augmented metadata

- is_synthetic: FALSE=1466
- synthetic row count: 0

## Cross-platform normalized text hashes

Normalization: Unicode NFKC, whitespace collapsed, trimmed, casefolded; hashes are truncated SHA-256 values. Raw post text is not included.

- youtube__reddit: 5 shared hash groups: 844347e54f00c4b9, 8a798890fe938171, b5bea41b6c623f7c, e0a63ff92eb85c02, e186022d0931afe9
- youtube__x: 0 shared hash groups: none
- reddit__x: 0 shared hash groups: none

## Interpretation and limitations

- Existing tier-related distributions are descriptive only; this report does not infer class meanings.
- The report does not assign proposed annotation labels and does not use keywords, tiers, predictions, or probabilities to label text.
- Duplicate hashes identify possible repeated content, not whether a record is erroneous.
- YouTube synthetic rows are retained and separately summarized; they were not removed.
- Current split and model_split values are reported without changing them. Their provenance remains unresolved.

## Recommended next step

Review this quality report with the annotation guidelines, then conduct a small human-annotated pilot using a separate protected working artifact. Resolve provenance and split policies before any cleaning, relabeling, cross-platform combination, or model training.

This is a non-clinical linguistic-signal research assessment; it does not produce diagnoses.
