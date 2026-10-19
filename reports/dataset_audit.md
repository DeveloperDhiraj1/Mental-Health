# Initial dataset audit

Scope: exactly the three current files in `data/raw/`; raw files were not modified.

## Dataset summary

- **reddit_dataSet.csv** (reddit): 4,362,785 bytes; 1,302 exact data rows; 51 columns; encoding `utf-8-sig`; delimiter `','`.
  - Selected columns: text=`post_text`, user=`anonymized_user_id`, timestamp=`timestamp`, labels=['tier_lexicon', 'tier_corrected', 'tier_model', 'tier', 'tier_source', 'tier_confidence', 'tier_pred', 'prob_tier_0', 'prob_tier_1', 'prob_tier_2', 'prob_tier_3'].
  - Missing/validity: {'missing_text': 0, 'empty_text': 0, 'missing_user': 0, 'missing_timestamp': 0, 'invalid_timestamp': 0, 'missing_labels': 0}
  - Malformed: 0 width mismatches; 0 strict parser errors.
  - Duplicates/leakage indicators: {'repeated_user_rows': 490, 'duplicate_text_rows': 47, 'unique_record_ids': 1302, 'unique_text_hashes': 1255, 'unique_users': 812, 'unique_parent_ids': 0, 'text_hashes_in_multiple_splits': 0, 'users_in_multiple_splits': 0, 'parent_ids_in_multiple_splits': 0}

- **twitter_data set.csv** (x): 1,727,760 bytes; 1,466 exact data rows; 51 columns; encoding `utf-8-sig`; delimiter `','`.
  - Selected columns: text=`post_text`, user=`anonymized_user_id`, timestamp=`timestamp`, labels=['tier_lexicon', 'tier_corrected', 'tier_model', 'tier', 'tier_source', 'tier_confidence', 'tier_pred', 'prob_tier_0', 'prob_tier_1', 'prob_tier_2', 'prob_tier_3'].
  - Missing/validity: {'missing_text': 0, 'empty_text': 0, 'missing_user': 0, 'missing_timestamp': 0, 'invalid_timestamp': 0, 'missing_labels': 0}
  - Malformed: 0 width mismatches; 0 strict parser errors.
  - Duplicates/leakage indicators: {'duplicate_text_rows': 30, 'repeated_user_rows': 272, 'unique_record_ids': 1466, 'unique_text_hashes': 1436, 'unique_users': 1194, 'unique_parent_ids': 0, 'text_hashes_in_multiple_splits': 0, 'users_in_multiple_splits': 0, 'parent_ids_in_multiple_splits': 0}

- **youtube_data set.csv** (youtube): 2,952,633 bytes; 1,971 exact data rows; 51 columns; encoding `cp1252`; delimiter `','`.
  - Selected columns: text=`post_text`, user=`anonymized_user_id`, timestamp=`timestamp`, labels=['tier_lexicon', 'tier_corrected', 'tier_model', 'tier', 'tier_source', 'tier_confidence', 'tier_pred', 'prob_tier_0', 'prob_tier_1', 'prob_tier_2', 'prob_tier_3'].
  - Missing/validity: {'missing_text': 0, 'empty_text': 0, 'missing_user': 125, 'missing_timestamp': 125, 'invalid_timestamp': 0, 'missing_labels': 0}
  - Malformed: 0 width mismatches; 0 strict parser errors.
  - Duplicates/leakage indicators: {'repeated_user_rows': 72, 'duplicate_text_rows': 19, 'unique_record_ids': 1971, 'unique_text_hashes': 1952, 'unique_users': 1774, 'unique_parent_ids': 30, 'text_hashes_in_multiple_splits': 0, 'users_in_multiple_splits': 0, 'parent_ids_in_multiple_splits': 0}

## Interpretation cautions

Label names and values are reported as observed metadata. No label is assumed to be human-annotated or clinically valid. `tier`, `tier_corrected`, `tier_model`, `tier_source`, confidence and probabilities must be traced to documentation/code before use.

## Text preservation

The audit counts non-ASCII characters, emoji-like code points, URLs, usernames and common negation forms. These are warnings against careless normalization, not language or clinical judgments.

## Unresolved questions and recommended next steps

See `reddit_audit.json` for the dedicated Reddit questions. Obtain provenance, define leakage policy, review labels, and only then design cleaning/splitting. Do not train yet.
