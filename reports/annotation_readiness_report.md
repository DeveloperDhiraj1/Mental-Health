# Annotation readiness review

## Review scope

Reviewed reports:

- reports/label_provenance_report.md — present
- reports/label_scheme_proposal.md — present
- reports/annotation_guidelines.md — present
- reports/data_quality_report.md — present

The project remains a non-clinical linguistic-signal research project. No report establishes or claims that text can diagnose a person's mental-health condition.

## Decision summary

### GO for a controlled manual pilot

A small pilot of approximately 50–100 posts may proceed after the project owner approves the operational decisions listed below. The pilot must use independent human review, explicit uncertainty marking, and a separate annotation artifact.

### NO-GO for full-scale annotation, label replacement, cross-platform modeling, or model training

The existing tiers cannot yet be used as ground truth, and the current split fields cannot yet define evaluation partitions.

## Completed prerequisites

- The three current raw datasets have been identified and audited.
- Row counts, schemas, encodings, missingness, duplicate indicators, metadata columns, and timestamp information are documented.
- Existing tier-related columns are documented without assigning meanings to values 0, 1, 2, or 3.
- The label provenance review found no local evidence defining tier semantics or proving human annotation.
- A proposed non-clinical label scheme exists.
- Human annotation guidelines exist with inclusion/exclusion rules for:
  - none_other
  - distress_negative_affect
  - mental_health_reference_or_support
  - self_harm_related
  - optional supporting labels
  - context flags
  - uncertainty and review reasons
- The guidelines address sarcasm, quotation, educational content, fictional/hypothetical text, third-person content, mixed language, emojis, URLs, usernames, hashtags, and negations.
- Duplicate-text groups and cross-platform normalized text-hash overlap are documented.
- YouTube synthetic/augmented rows and parent-record metadata are documented.
- Split and model_split disagreements are documented for every row.
- The guidelines require independent annotation, adjudication, disagreement tracking, and later held-out evaluation safeguards.

## Existing data risks documented

The data-quality report documents:

- YouTube: 1,971 exact rows, 22 extra normalized-text duplicate rows, 125 synthetic rows, and 1,971 split disagreements.
- Reddit: 1,302 exact rows, 48 extra normalized-text duplicate rows, and 1,302 split disagreements.
- X/Twitter: 1,466 exact rows, 32 extra normalized-text duplicate rows, and 1,466 split disagreements.
- Five shared normalized text-hash groups between YouTube and Reddit.
- No exact duplicate full rows in any of the three datasets.
- Missing user IDs and timestamps in 125 YouTube rows.

These findings do not justify deleting records or changing splits. They define controls needed for later annotation and evaluation.

## Missing prerequisites

The following are not resolved:

1. The meanings of existing tier values 0, 1, 2, and 3.
2. Whether existing tier fields are human, lexicon, model, corrected, or mixed labels.
3. The authoritative meaning of split versus model_split.
4. Whether YouTube synthetic labels should be included in a human pilot or reviewed in a separate stratum.
5. The exact serialization format for multiple signal labels and context flags in the current annotation template.
6. Whether topic-only educational posts receive mental_health_reference_or_support.
7. Whether self-harm prevention/recovery discussion receives self_harm_related.
8. Whether none_other can coexist with informational or recovery labels.
9. The privacy/access procedure for copying post_text into a working annotation artifact.
10. The annotator identifiers and review workflow.

These are annotation-design decisions, not reasons to infer or repair the legacy tiers.

## Risks that could invalidate later evaluation

- Treating tier, tier_model, tier_pred, or probabilities as ground truth.
- Treating numeric tiers as ordinal linguistic or clinical severity.
- Allowing exact duplicate text across development and evaluation partitions.
- Allowing YouTube augmented records and their parent records to cross evaluation boundaries.
- Using the unresolved split or model_split fields as if they were documented partitions.
- Mixing the five shared YouTube/Reddit normalized text groups across evaluation partitions.
- Allowing repeated users to appear across partitions without a declared policy.
- Letting annotators see existing tiers, model outputs, probabilities, or source tags.
- Treating quoted, educational, fictional, sarcastic, or third-person text as first-person self-report.
- Forcing ambiguous posts into none_other.
- Combining platforms before checking annotation agreement separately by platform.
- Describing linguistic labels as diagnoses, clinical severity, or individual risk.

## Internal consistency of the proposal and guidelines

The proposal and guidelines are substantively consistent:

- Both use multi-label linguistic signals rather than an ordinal severity scale.
- Both define none_other, distress_negative_affect, mental_health_reference_or_support, and self_harm_related.
- Both separate signal labels from context flags and uncertainty.
- Both prohibit using existing tiers to determine new labels.
- Both require independent review, adjudication, and platform-specific analysis.

Operational details still need approval:

- The proposal allows multiple labels, but the existing annotation template has one proposed_label field and no dedicated context field.
- The proposal lists optional supporting labels, but does not require them.
- The guidelines identify cases where none_other may conflict with informational or recovery labels, but do not choose a final policy.
- The guidelines define review reasons, but the project has not chosen a controlled vocabulary or annotator ID policy.

## Decisions requiring human approval before the pilot

Approve these decisions in writing:

1. Use the four core signal labels only for the pilot, or include optional supporting labels.
2. Store multiple labels in a fixed delimiter format in proposed_label.
3. Decide whether context flags will be recorded in proposed_label for this pilot or in a separate later column.
4. Decide how topic-only educational posts are handled.
5. Decide how prevention/recovery discussion is handled under self_harm_related.
6. Decide whether none_other may coexist with supporting/topic labels.
7. Decide whether synthetic YouTube rows are excluded from the main pilot and sampled separately.
8. Approve the privacy-controlled working location and annotator identifiers.

## Pilot conditions

After those decisions are approved, run a 50–100 post pilot:

- Represent YouTube, Reddit, and X separately wherever possible.
- Keep platform identity in every annotation.
- Use a fixed, documented random seed.
- Do not use existing tier fields, predictions, probabilities, or keywords to assign labels.
- Keep annotators blind to legacy labels and source tags.
- Include a small separately identified synthetic YouTube stratum only if approved; do not silently mix it with original rows.
- Keep known duplicate-text groups and shared cross-platform hashes together or flag them for review.
- Have two annotators independently review the same posts.
- Record confidence, needs_review, and review_reason.
- Preserve disagreements and send them to adjudication.
- Review agreement and difficult cases before expanding annotation.

## Final recommendation

**GO:** controlled manual pilot annotation, subject to the human approvals above.

**NO-GO:** full annotation, relabeling, changing splits, combining platforms into one target, or training a model.

The pilot should be used to test whether the proposed definitions are understandable and consistently applied. It must not be used to validate or reinterpret the existing tier values, and its labels describe text signals rather than clinical conditions.
