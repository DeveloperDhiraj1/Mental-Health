# Baseline Model Readiness Review

**Project scope:** non-clinical research on linguistic signals in the three current social-media datasets. This review does not treat text as evidence of a person's clinical condition and does not authorize model training.

## Decision

**NO-GO — do not train a baseline model yet.** Required annotation and leakage-control prerequisites are incomplete.

## Artifact review

| Requirement | Current evidence | Status |
|---|---|---|
| Annotation guidelines | `reports/annotation_guidelines.md` exists and defines a proposed non-clinical scheme, including `none_other`, `distress_negative_affect`, `mental_health_reference_or_support`, and `self_harm_related`, with optional supporting labels and uncertainty/context handling. | Present, but not shown to be finally approved |
| Annotation readiness decision | `reports/annotation_readiness_report.md` exists. It permits only a controlled pilot after project-owner approval and recommends NO-GO for full annotation, cross-platform modeling, and training until open decisions are resolved. | NO-GO for training |
| Human-reviewed labels | No completed human annotation artifact was found. `reports/annotation_template.csv` is only a header/template; `Data/processed/pilot_annotation_template.csv` is absent. | Missing |
| Pilot review | `reports/pilot_annotation_review.md` is absent. | Missing |
| Dataset preparation status | `reports/dataset_preparation_status.md` exists and records NO-GO because reviewed labels, approved targets, pilot review, split policy, and preparation tooling are missing. | NO-GO |
| Preparation script | `src/prepare_dataset.py` is absent. `src/data_quality_check.py` is an audit script, not a human-label preparation and validation pipeline. | Missing |
| Existing tier definitions | The provenance and upstream-evidence reports do not establish meanings for tier values 0, 1, 2, or 3. Their numeric values, frequencies, predictions, and probabilities cannot be used as target definitions. | Unresolved |
| Split policy | No approved train/validation/test construction policy was found. Existing `split` and `model_split` fields are documented as disagreeing for all rows and must not be assumed to be safe partitions. | Missing |

## Verified evidence

- The proposal and guidelines are research annotations for textual signals, not clinical diagnoses. They explicitly leave the existing tier values unresolved.
- The readiness report identifies unresolved approval decisions, including multilabel representation, treatment of optional/context labels, ambiguous or educational content, synthetic YouTube rows, and the annotator/review workflow.
- The pilot review is not present, so inter-annotator agreement, disagreement patterns, and guideline performance have not been evaluated.
- The dataset-preparation status report states that no training-ready dataset should be built. No reviewed target labels or approved label vocabulary are available in the inspected artifacts.
- No preparation script with required-column, missing-label, allowed-label, duplicate-ID, exclusion-ledger, and leakage checks exists.
- Existing quality reports document potential leakage sources rather than resolving them. They include normalized duplicate-text groups, repeated-user risks, synthetic/augmented records and parent-record relationships, cross-platform duplicate-text hashes, and disagreement between `split` and `model_split`.
- No train/validation/test split was created or changed during this review, and no raw CSV was modified.

## Blockers

1. **No completed human-reviewed target labels.** Existing `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, confidence, and probability fields are not verified ground truth.
2. **No pilot-quality review.** There is no evidence of two independent annotators, adjudication, agreement measurement, or resolved disagreement rules.
3. **The label scheme is still a proposal.** The project owner must approve the final class set, single-label versus multilabel representation, optional supporting labels, context flags, uncertainty handling, and serialization.
4. **No validated preparation pipeline.** `src/prepare_dataset.py` does not exist, so exclusions, label validation, duplicate handling, synthetic-row policy, and audit logging are not reproducibly implemented.
5. **No approved leakage-safe split policy.** A future policy must group exact/normalized duplicate texts, repeated users, augmented rows sharing parent records, and cross-platform duplicate hashes before partitioning. The existing split columns cannot be treated as validated partitions.

## What is not established

The evidence does not establish that any existing label was human-annotated, that tier 0–3 have a particular mental-health interpretation, or that model-derived columns represent ground truth. No class meaning is inferred here. It is also not established that the three platforms share equivalent label definitions or that they should use one target without platform-specific validation.

## Exact next actions

1. Approve the annotation guidelines and record the final label vocabulary and serialization rules.
2. Prepare a separate, reproducible pilot sample of 50–100 posts without using tier-related fields or model outputs to select or label records. Apply the documented synthetic-row policy.
3. Have two annotators independently label the same pilot, recording confidence, uncertainty, and review reasons while remaining blind to existing tier/model fields.
4. Create `reports/pilot_annotation_review.md` with raw agreement, Cohen's kappa when applicable, disagreement categories, and decisions on unclear rules. Revise the guidelines and repeat the pilot if needed.
5. Implement and validate `src/prepare_dataset.py` using only explicitly approved human labels. It must validate required columns, missing labels, allowed labels, record-ID uniqueness, duplicates, synthetic policy, and an exclusion ledger without altering raw files.
6. Approve a leakage-safe partition policy covering duplicate-text groups, users, parent/augmented records, and cross-platform overlap. Do not rely on the existing `split` or `model_split` fields until their construction is documented and validated.
7. Only after these steps, create partitions and review class balance. A reasonable future baseline would be a TF-IDF word/character n-gram model with logistic regression or a linear SVM, evaluated with the approved leakage-safe split; it must not be run now.

## Final status

No baseline model was trained. No labels were assigned. No raw dataset, split assignment, or existing source file was modified. The project remains at **NO-GO for baseline modeling** until the blockers above are resolved and documented.

