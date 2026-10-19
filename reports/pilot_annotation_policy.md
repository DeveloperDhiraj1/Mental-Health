# Pilot Annotation Policy

## Status: PROPOSED — HUMAN REVIEW REQUIRED

This policy defines the proposed four-label scheme for the first manual pilot.
It is ready for human review but is not approved ground truth and must not be
used to begin sampling until the project owner approves it.

The labels describe observable linguistic signals in text. They are non-ordinal,
potentially multi-label categories. They are not severity levels, risk scores,
clinical classifications, or diagnoses, and they do not establish anything
about the author's mental-health condition.

## Relationship to existing project documents

The existing `reports/label_scheme_proposal.md` and
`reports/annotation_guidelines.md` already propose the same four core signals,
separate context flags, uncertainty review, and no use of legacy tiers. This
policy makes the following decisions more specific for the pilot:

- Optional supporting labels are excluded from the pilot.
- `none_other` is mutually exclusive with every other signal label.
- The other three signal labels may co-occur when each is supported by the text.
- Context flags remain separate from signal labels.
- Synthetic/augmented YouTube rows are excluded from the primary pilot sample.

These are documented policy decisions, not silent edits to the earlier files.
The earlier documents remain unchanged and continue to be marked proposed.

## Legacy metadata prohibition

The meanings of existing tier values 0, 1, 2, and 3 remain unresolved. The
fields `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`,
confidence/probability fields, source tags, and other model-related columns must
not be used as ground truth, as sampling criteria, or as evidence for a new
annotation. No proposed label maps to any legacy tier value.

## Pilot signal labels

### `none_other`

Use only when none of the other three signal labels applies and the available
text is sufficiently clear. This includes neutral, unrelated, routine,
entertainment, promotional, or general text without a core signal.

Do not use it for clear distress, meaningful mental-health support/reference,
or explicit self-harm-related content. Do not use it to force a decision when
the meaning is unclear; flag the item for review instead.

### `distress_negative_affect`

Use when the text explicitly expresses emotional strain, suffering,
hopelessness, loneliness, fear, overwhelm, sadness, anger, or related negative
affect. The label describes wording in the post and does not imply a diagnosis
or clinical severity.

Do not infer it from a merely negative event, an isolated keyword, a metaphor,
or a phrase whose literal meaning cannot be resolved.

### `mental_health_reference_or_support`

Use when the text meaningfully discusses mental-health experiences, care,
therapy, counselling, coping, recovery, wellbeing, support, or help-seeking.
It may apply to support for the author or another person, and it may co-occur
with `distress_negative_affect` or `self_harm_related`.

Do not infer it from an isolated word, insult, metaphor, unrelated headline, or
topic mention that has no meaningful support/reference content.

### `self_harm_related`

Use when the text explicitly refers to self-harm, suicide, wanting to die,
attempts, planning, prevention, recovery, safety planning, or immediate safety
support related to those topics. It is a content label, not a prediction of
action or a severity assessment.

Do not infer it from vague sadness, figurative language, insults, or an
unresolved phrase. Explicit content can receive this label even when it is
educational, quoted, fictional, or third-person; the applicable context flag
must be recorded, and the project owner should review this rule before pilot
annotation.

## Multi-label and exclusivity rules

- Zero or more of the three substantive signal labels may be supported by a post.
- `none_other` may be assigned only when all three substantive labels are absent.
- `none_other` cannot be combined with any other signal label.
- The three substantive labels may co-occur. For example, an explicit first-person statement of emotional distress while requesting counselling can receive both `distress_negative_affect` and `mental_health_reference_or_support`.
- The pilot must use one consistent serialization in `annotator1_label` and `annotator2_label`. Recommended format: labels sorted in the fixed order `distress_negative_affect|mental_health_reference_or_support|self_harm_related`, with no spaces; `none_other` stands alone. This delimiter is a proposal requiring approval before sampling.
- `uncertain_needs_review` is a review status, not a fifth signal label. When used, do not force a signal label; record the uncertainty in `needs_review` and `review_reason`.

## Context flags

Context flags must be stored separately from signal labels in `context_flags`.
Suggested controlled values are:

- `first_person_or_self_report`
- `third_person`
- `quoted_or_reported`
- `educational_or_information`
- `fictional_or_hypothetical`
- `sarcastic_or_ironic`
- `promotional_or_campaign`
- `context_insufficient`

Multiple context flags may apply. Context flags do not automatically suppress a
content signal, but they prevent treating quoted, fictional, educational, or
third-person wording as the author's own self-report.

## Handling difficult cases

### Ambiguous or insufficient context

Use `needs_review=TRUE` when the available text is too short, incomplete,
unreadable, mixed-language in a way that prevents reliable interpretation, or
dependent on missing conversation context. Record a specific reason such as
`insufficient_context`, `ambiguous`, `language_or_encoding`, or
`annotator_disagreement`. Do not use `none_other` merely because evidence is
insufficient.

### Sarcasm and irony

Set `sarcastic_or_ironic` when reasonably apparent. Do not assign a substantive
signal from an idiom alone. If literal and sarcastic readings cannot be
resolved, flag for review instead of guessing.

### Quoted or reported text

Set `quoted_or_reported`. Do not treat quoted words as the author's own
self-report. A substantive content label may still be recorded when the text
clearly contains the topic, subject to the approved pilot policy.

### Educational or informational text

Set `educational_or_information`. Topic discussion alone does not show that the
author experiences the topic. Explicit prevention or support information may
receive the corresponding content label, but this rule requires human approval
before sampling.

### Fictional, hypothetical text, or lyrics

Set `fictional_or_hypothetical`. Do not treat a character or imagined scenario
as the author's experience. If explicit content is retained as a text-content
signal, preserve the context flag and apply the rule consistently.

### Prevention and recovery discussions

Explicit self-harm prevention, safety planning, or recovery discussion may
receive `self_harm_related` as a content label, with relevant context flags.
This does not imply current personal risk. The project owner must approve this
content-versus-self-report distinction before annotation.

## Human pilot procedure

After approval, sample 50–100 posts with a fixed documented seed, preserving
platform identity and using only original or unspecified records for the
primary pilot. Exclude explicitly synthetic/augmented YouTube rows from that
primary sample and report the exclusion. Do not use legacy labels, keywords,
predictions, probabilities, or model columns for sampling.

Two independent annotators should label every pilot item without seeing each
other's annotations or legacy metadata. They should record both signal labels
and context flags, confidence in applying the rules, review status, and a
review reason where needed. Preserve both independent annotations.

An adjudicator should review disagreements, especially ambiguity, sarcasm,
quotation, education, fiction, prevention/recovery, and missing-context cases.
Report raw agreement and Cohen's kappa when applicable, with limitations for
small samples or rare labels. Revise the policy if disagreements reveal an
unclear rule, and version the revised document.

Duplicate normalized-text groups and the known cross-platform shared hash groups
must be recorded or flagged for future leakage control. They must not be
silently deleted, relabeled, or used to alter current split assignments.

## Unresolved decisions before sampling

The following must be confirmed in writing by the project owner:

1. Approval of this four-label policy and the recommended pipe-delimited format.
2. Approval that context flags are stored only in `context_flags`, separate from signal labels.
3. Final treatment of explicit educational, quoted, fictional, and third-person content.
4. Final treatment of prevention and recovery discussion under `self_harm_related`.
5. Privacy, annotator-ID, and sensitive-content review procedures.
6. The fixed random seed and exact platform allocation for the pilot.

Until these decisions are approved, do not begin sampling. This policy remains
**PROPOSED — NOT APPROVED** and is not clinically validated.

