# Dataset preparation status

## Decision

**NO-GO for training-ready dataset preparation.**

No training-ready dataset and no preparation script were created. The current evidence does not support creating targets or partitions safely.

## Evidence checked

The following reports were present and inspected:

- reports/annotation_readiness_report.md
- reports/label_provenance_report.md
- reports/data_quality_report.md
- reports/annotation_guidelines.md

The following required pilot-review artifact is missing:

- reports/pilot_annotation_review.md

No human-reviewed pilot annotation artifact was found in the inspected project paths. The readiness report permits only a controlled pilot after human approval; it does not approve full annotation, relabeling, dataset preparation, split creation, cross-platform modeling, or training.

## Blockers

1. No completed pilot annotation review exists.
2. No approved human-reviewed labels are available as targets.
3. Existing tier values 0–3 remain semantically unresolved.
4. Existing tier, tier_lexicon, tier_corrected, tier_model, tier_pred, confidence, probability, and lexicon fields cannot be used as ground truth.
5. The meanings and authority of split versus model_split remain unresolved; all rows disagree between those fields.
6. Human approval is still missing for:
   - multiple-label serialization;
   - optional supporting labels;
   - educational-only text;
   - self-harm prevention/recovery discussion;
   - coexistence of none_other with supporting/topic labels;
   - synthetic YouTube-row treatment;
   - privacy and annotator-ID workflow.
7. Duplicate-text groups, five shared normalized YouTube/Reddit text hashes, repeated users, and YouTube synthetic parent groups require a documented leakage policy before partitioning.

## What was not done

- No raw CSV was modified.
- No labels were inferred from tiers, lexicon outputs, model predictions, confidence values, probabilities, or keywords.
- No rows were deleted or silently discarded.
- No new labels were assigned.
- No train/test or evaluation split was created.
- No model was trained.

## Required next actions

1. Approve the outstanding annotation-design decisions in writing.
2. Create a fixed-seed manual pilot of approximately 50–100 posts, keeping platform identity and synthetic-row treatment explicit.
3. Have two annotators independently label the same pilot while blinded to existing tier/model metadata.
4. Record uncertainty, review reasons, and disagreements in a separate protected annotation artifact.
5. Produce reports/pilot_annotation_review.md with agreement and disagreement analysis.
6. Revise and freeze the annotation guidelines based on pilot disagreements.
7. Document duplicate, user, parent-record, synthetic, cross-platform, and split policies.
8. Only after those steps, design a separate preparation script that validates approved human labels and records every exclusion reason.

## Future preparation requirements

When preparation is eventually approved, the pipeline must:

- read only the three current raw datasets;
- require explicitly approved human-reviewed labels;
- validate required columns, record-ID uniqueness, missing labels, and allowed label values;
- preserve raw files;
- document text normalization and empty-text handling;
- detect exact and normalized near-duplicates;
- apply an explicit synthetic-row policy;
- preserve platform and user-group information for leakage control;
- avoid creating splits until the split policy is approved;
- record every exclusion and its reason;
- remain a non-clinical linguistic-signal workflow.

Until the pilot is annotated and reviewed, treating the datasets as training-ready would fabricate target provenance and risk invalid evaluation.
