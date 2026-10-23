# Annotation Coverage Plan

## Status

This is a proposed human-annotation expansion plan. It does not assign labels, modify raw files, or claim clinical validity. The four approved labels remain non-ordinal text-content categories:

- `none_other`
- `distress_negative_affect`
- `mental_health_reference_or_support`
- `self_harm_related`

Substantive labels may co-occur in the approved fixed pipe-delimited order; `none_other` stands alone. Context flags remain separate. Existing tier and model-related fields are not ground truth.

## Current coverage status

The current adjudication workbook has 60 rows and, according to its current contents, 60 completed records with no blank final labels. Two records retain `A2_text_mismatch=TRUE`; both have notes documenting that canonical seed text was used. The validation issue CSV still reports an older unresolved case, so validation must be rerun before treating the workbook as final.

The 60 records represent only 1.27% of the 4,739 raw posts. The earlier IAA analysis found only 8/60 policy-valid original A1/A2 label pairs. Therefore the pilot is useful for testing the workflow but is not enough for reliable multi-label model performance claims.

## Recommended next batch

Begin with **300 new genuine-post records**, approximately 100 per platform, then review the stopping criteria below before expanding to 600. This is a planning target, not an automatic sampling instruction. Keep the 60 pilot rows identified and do not silently duplicate them in the new batch.

Use two components:

1. **Random core:** approximately 80% of each platform's batch, sampled with a fixed seed from original or unspecified records, after removing records linked to already selected duplicate/parent groups. Do not use legacy tiers, model predictions, probabilities, or keyword rules to choose labels.
2. **Coverage and ambiguity stratum:** approximately 20%, selected to cover platform, language/script, timestamp availability, quotations, educational content, fictional/hypothetical content, sarcasm, insufficient context, and duplicate/parent metadata. Synthetic rows may be included only if separately marked and reviewed; they must not be mixed into the primary genuine-post estimate.

The coverage stratum is for understanding annotation difficulty, not for estimating natural prevalence. Sampling must remain blind to legacy labels and model outputs. If a human reviewer identifies a rare signal during annotation, retain it and report its support; do not manufacture examples by keyword search or augmentation.

## Independent review workflow

1. Prepare separate A1 and A2 work copies with canonical seed text.
2. Keep annotators blind to each other's decisions and to legacy tier/model metadata.
3. Record multi-label signals, context flags, confidence, and review reasons.
4. Preserve both original annotations before adjudication.
5. Adjudicate only disagreements or genuinely unclear cases; never overwrite the original judgments.
6. Keep synthetic/augmented records and duplicate/parent groups separately identified.

## Coverage and stopping criteria

Do not stop merely because 300 rows have been labeled. Continue until all of the following are met, or explicitly document why a condition is impossible:

- At least 100 policy-valid, adjudicated records per platform for an initial platform-aware analysis.
- At least 30 adjudicated positive instances for each substantive signal label across the study, with counts reported separately by platform. If a label remains rare, report uncertainty instead of oversampling and calling the result prevalence.
- Both annotators have independently reviewed the same records, with at least 90% of rows having valid labels and context values.
- Exact label-set agreement is at least 0.80 and each substantive binary label has interpretable positive and negative agreement. Kappa is supportive only; it must not be used alone when prevalence is low.
- Unresolved/needs-review cases are below 5%, with every remaining case explicitly documented.
- Every platform has reviewed examples of ambiguous, quoted, educational, fictional, sarcastic, third-person, and context-insufficient content where available.
- Duplicate, user, and parent groups are identified before any future split.

If agreement remains low, revise the guidelines and run another focused pilot instead of forcing labels. If a rare label cannot reach the support threshold, state that its evaluation is exploratory or omit the claim.

## Reporting requirements

For each batch report platform counts, genuine versus synthetic counts, label-set counts, per-label support, context-flag counts, missing/invalid values, agreement, unresolved cases, and duplicate/group exclusions. Keep raw post text and user identifiers local; reports should use record or text hashes where possible.

## Next practical action

First rerun final annotation validation against the current workbook so the stale issue list is replaced by current evidence. Then obtain approval for the 300-record plan and prepare a new, group-aware annotation batch without changing raw data or existing annotations.
