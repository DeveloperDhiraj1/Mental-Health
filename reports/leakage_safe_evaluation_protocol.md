# Leakage-Safe Evaluation Protocol

## Status and scope

This is a proposed evaluation protocol for a non-clinical study of observable linguistic signals. It does not treat any label as a diagnosis, clinical severity score, or measure of a person's mental-health condition. No split was created and no model was trained in preparing this document.

## Current evidence checked

The current raw datasets contain **4,739 rows**: YouTube 1,971, Reddit 1,302, and Twitter/X 1,466. The quality audit found 64 normalized duplicate-text groups, 5 cross-platform duplicate groups involving 16 records, 74 conservative near-duplicate candidates, and 125 explicitly synthetic/augmented YouTube rows.

The current workbook is `Data/processed/annotation_work/manual_adjudication_workbook.csv`. It contains 60 rows, all currently marked `completed`, with no blank final labels. The two known A2 text mismatches have explicit adjudication notes documenting use of the canonical seed text. However, `reports/final_annotation_validation_issues.csv` still contains an older `needs_review` issue for one record, and the existing validation report is stale relative to the workbook. This discrepancy must be resolved by rerunning validation before modeling.

The original A1/A2 IAA report remains unsuitable as a final target-quality claim: only 8/60 pairs used the approved label vocabulary, while many original values and context flags were invalid under the approved policy.

## Mandatory grouping rule

Create one evaluation group for every connected set of records linked by any of these relations:

1. Exact normalized `post_text` match.
2. Near-duplicate candidate confirmed by manual review.
3. Shared non-empty `parent_record_id` or an augmentation parent-child link.
4. Shared non-empty `anonymized_user_id`.
5. Any future cross-platform copy discovered by normalized text matching.

Use a deterministic connected-components implementation. Assign a stable group hash to each component; do not print raw text or user IDs. Every member of a group must remain in the same train, validation, or test partition. If a group spans too many records, exclude the whole group from the intended evaluation rather than splitting it.

Synthetic/augmented YouTube rows must remain identifiable. For a primary generalization result, exclude them or evaluate them in a separately reported synthetic-only analysis. Never allow a synthetic child and its parent to cross partitions.

## What the evaluation should mean

These are different questions and must not be conflated:

- **Unseen users:** performance on posts from users absent from training.
- **Unseen posts:** duplicate-controlled performance on new text, even if a user has appeared before.
- **Unseen platforms:** transfer from some platforms to a platform held out of training; this needs platform-specific annotations and is a harder question.
- **Future posts:** temporal generalization to later timestamps; this requires a documented time cutoff and protection against future information.

The first primary claim should be **group-aware generalization to unseen users and unseen/near-duplicate-controlled posts**, with platform-stratified results. Cross-platform transfer and future-post performance should be secondary studies.

## Proposed split policy (not yet executed)

After sufficient approved labels exist:

1. Build leakage groups before any split, using the mandatory grouping rule.
2. Keep synthetic rows separate from the primary genuine-post analysis.
3. Assign whole groups to train/validation/test using a fixed documented seed.
4. Use approximately 70%/15%/15% by groups, subject to minimum label counts; if group constraints make this impossible, report the limitation rather than breaking groups.
5. Stratify approximately by platform and multi-label signal coverage while assigning groups. Do not stratify using legacy tiers, model predictions, or probabilities as if they were targets.
6. Freeze the test set before model selection. Do not inspect test performance while tuning features or hyperparameters.
7. Recheck that no user, normalized-text hash, near-duplicate group, or augmentation parent crosses partitions.

No existing `split` or `model_split` value is accepted as an evaluation split without provenance and independent leakage checks.

## Metrics to report later

Because the approved scheme is multi-label, report each signal as a binary one-vs-rest target and also report exact label-set agreement where useful. Report class counts and prevalence for each partition, micro and macro precision/recall/F1, per-label precision/recall/F1, and support. Include a confusion matrix only for a clearly defined single-label secondary view; do not force multi-label annotations into an ordinal scale.

When the labeled test set is sufficiently large, use bootstrap confidence intervals grouped by user/evaluation group. With few positive examples, report interval instability and avoid strong conclusions. A single accuracy score is inadequate for rare labels and class imbalance.

## Explicit leakage prohibitions

Do not use `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, probability/confidence columns, lexicon-hit fields, undocumented model outputs, or legacy split columns as ground-truth targets. Exclude them from features by default. Do not use final adjudicated labels to measure original A1/A2 agreement.

## Blockers before baseline modeling

- Rerun final validation so the current workbook and issue list agree.
- Preserve the two canonical-text mismatch decisions in the final modeling artifact.
- Confirm label-policy compliance and independent annotation quality on a larger sample; the 60-record pilot is too small for a reliable performance claim.
- Define and approve the group-aware split implementation and test-set freeze.
- Exclude legacy label-derived columns and synthetic records from the primary evaluation unless separately justified.

**Safe now:** resolve the stale validation artifact and plan additional human annotation. **Blocked:** training, tuning, and performance claims until these controls are approved.
