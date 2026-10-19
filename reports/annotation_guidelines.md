# Human annotation guidelines (PROPOSED — human approval required)

## Status and scope

**Status: PROPOSED.** These definitions are not final ground truth and must be
approved by the project owner and tested in a two-annotator pilot before use for
dataset preparation or model evaluation.

These guidelines are for a non-clinical research prototype studying linguistic signals in social-media text. An annotation describes observable text content and context; it does not describe a person's clinical condition and must not be used as a diagnosis or clinical severity rating.

The existing tier, tier_lexicon, tier_corrected, tier_model, tier_pred, probability, confidence, and source fields are unresolved legacy metadata. Annotators must not use them to decide a new label or infer the meanings of values 0, 1, 2, and 3.

These guidelines apply to the three current platforms only: YouTube, Reddit, and X/Twitter. Keep platform identity with every annotation.

## Proposed signal labels

Signal labels are multi-label: more than one may apply to a post.

### none_other

No clear target signal is expressed in the available text.

Include ordinary conversation, unrelated information, entertainment, promotion, general commentary, and neutral text.

Exclude clear distress, support-seeking, mental-health discussion, or self-harm-related content. Do not use this label when the text is too ambiguous; use needs_review instead.

Example: “The new library is open until eight.”

### distress_negative_affect

The text expresses emotional strain, suffering, hopelessness, loneliness, overwhelm, fear, persistent sadness, anger, or related negative affect without requiring a diagnosis.

Include explicit expressions of emotional difficulty. Exclude a negative event with no emotional impact, an unclear figurative phrase, or a conclusion requiring clinical knowledge.

Example: “I have felt overwhelmed and alone since everything changed.”

### mental_health_reference_or_support

The text explicitly discusses mental-health experiences, care, coping, recovery, wellbeing, support, or help-seeking without asserting a diagnosis.

Include requests for advice or resources and discussion of counselling, therapy, recovery, wellbeing, or supporting someone. Exclude isolated keywords, insults, metaphors, and topic-only references when no meaningful support or experience is expressed.

Example: “Does anyone know practical ways to find affordable counselling?”

### self_harm_related

The text explicitly refers to self-harm, suicide, wanting to die, plans or attempts, or direct prevention/safety discussion about those topics.

Include direct discussion of thoughts, behavior, intent, planning, attempts, recovery, prevention, or immediate safety help. Exclude clearly figurative, fictional, quoted, sarcastic, or unrelated uses. Do not infer intent from vague sadness.

Example: “I am worried about a friend who says they may hurt themselves; what immediate support is available?”

This is a content label, not a risk score, severity level, or clinical conclusion.

## Optional supporting labels

Use only if approved for the study:

- help_seeking: explicit request for advice, support, resources, or professional help.
- protective_or_recovery_language: coping, recovery, safety planning, social support, or improvement language.
- diagnostic_term_mentioned: a diagnostic or treatment term is mentioned without asserting that the author has that condition.

These are not clinical-status labels.

## Context labels

Record one or more applicable context flags separately from signal labels:

- first_person_or_self_report
- third_person
- quoted_or_reported
- educational_or_information
- fictional_or_hypothetical
- sarcastic_or_ironic
- promotional_or_campaign
- context_insufficient

Do not treat quoted, reported, fictional, educational, or third-person wording as the author's own experience.

## Difficult and borderline cases

Sarcasm or irony: mark sarcastic_or_ironic when reasonably apparent. Do not assign a signal from an idiom alone. If literal meaning cannot be resolved, mark needs_review.

Quotation or reporting: mark quoted_or_reported. The quoted words may receive a topic signal if relevant, but they must not be treated as a first-person self-report.

Educational or public-information content: mark educational_or_information. Discussion of a topic is not evidence that the author experiences it.

Fiction, hypothetical text, or lyrics: mark fictional_or_hypothetical. Do not treat a character or imagined scenario as the author's experience.

Third-person content: mark third_person. Label the text content if relevant, but do not convert it into a first-person signal.

Context-dependent posts: if the available text is insufficient, use context_insufficient and needs_review rather than guessing.

Mixed-language text, emojis, URLs, usernames, hashtags, and negations: inspect the original text. Do not remove or normalize them during annotation.

## Uncertainty and review

The template field needs_review must be TRUE whenever:

- The signal is ambiguous.
- The context could be literal, sarcastic, quoted, fictional, or educational.
- The post is too short or missing surrounding context.
- The text is unreadable or encoding appears damaged.
- Annotators disagree.
- The annotator would need outside information to decide.

Use review_reason values such as ambiguous, insufficient_context, sarcasm_or_irony, quoted_or_reported, educational, fictional_or_hypothetical, unreadable_or_corrupted, language_context, or annotator_disagreement.

Confidence should be the annotator's confidence in applying the written rules, not confidence that a person has a condition. Suggested values are high, medium, and low. Low confidence should normally have needs_review=TRUE.

Do not force an ambiguous item into none_other.

## Annotation procedure

1. Read the full available post text without consulting existing tier or model fields.
2. Decide whether one or more proposed signal labels apply.
3. Record the agreed signal-label format in the template's `annotator_label` field. Keep context flags in the agreed format or in a separately approved context field; do not encode them by guessing from legacy columns.
4. Set confidence based on rule clarity.
5. Set needs_review and review_reason when required.
6. Do not infer a diagnosis, intent, severity, or personal identity.
7. Preserve the original record_id and platform; do not edit the raw CSV.

For a formal study, at least two annotators should independently review the same pilot items. An adjudicator should resolve disagreements while preserving both original annotations. Report agreement separately for each signal and context label, and track the reasons for disagreement.

## Template handling

The generated `data/processed/annotation_template.csv` is a separate working artifact. Its rows contain copied source text and blank annotation fields; it does not overwrite raw data. The older `reports/annotation_template.csv` remains a header-only template.

Populate the working artifact only through a controlled, read-only annotation process. A human annotator should enter `annotator_label`, `confidence`, `needs_review`, and `review_reason`; no script should fill labels from keywords, existing tiers, model predictions, or probabilities. For independent review, maintain separate copies or separate annotator columns rather than overwriting the first annotation.

The required columns are:

record_id, platform, post_text, record_type, annotator_label, confidence, needs_review, review_reason

If raw text is copied into a working annotation file, restrict access, preserve CSV quoting and encoding, and do not overwrite the raw source. Consider using a protected local annotation environment and a separate redacted export for analysis.

## Future evaluation safeguards

Do not trust the current split or model_split fields as evaluation definitions until their provenance is documented. For a later held-out set:

- Keep exact duplicate text out of more than one partition.
- Keep augmented records with the same parent_record_id together.
- Consider grouping by anonymized user ID within each platform.
- Keep the three known Reddit/YouTube shared text groups together or exclude them from cross-platform evaluation until their origin is understood.
- Keep annotators blind to existing tier, predictions, probabilities, confidence, and source tags.
- Report results separately by platform, label, context, language, and uncertainty.

## Decisions requiring human approval

Before large-scale annotation, the project owner should approve:

- Whether optional supporting labels are included.
- Whether a post can receive none_other together with an informational or recovery label.
- The exact string format for multiple labels in proposed_label.
- Whether topic-only educational posts receive mental_health_reference_or_support.
- Whether self-harm prevention and recovery discussion receive self_harm_related.
- How to handle posts needing conversation context that is not present.
- The annotator identifiers and privacy controls.

Until these decisions are approved and pilot agreement is reviewed, these definitions remain a proposal and should not be treated as finalized ground truth.
