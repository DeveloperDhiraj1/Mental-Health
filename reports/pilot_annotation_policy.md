# Pilot Annotation Policy

## Status: OWNER-APPROVED PILOT POLICY — RESEARCH PROPOSAL, NOT CLINICALLY VALIDATED

This policy defines the owner-approved four-label scheme and operating rules
for the first manual pilot. Approval authorizes preparation of a pilot sample;
it does not make these labels ground truth, clinically validated, diagnostic,
or ordinal severity categories.

The labels describe observable text content only. They do not diagnose the
author, estimate clinical severity, or indicate personal risk.

## Owner approval record

The project owner approved the decisions recorded in this revision on
**2026-10-19**. Approval covers the four labels, multi-label serialization,
separate context flags, content/context handling, privacy procedure, pilot size,
random seed, synthetic-row exclusion, annotator independence, and prohibition
on legacy metadata as ground truth.

## Scope and legacy metadata prohibition

The pilot uses only these four non-ordinal core labels:

1. `none_other`
2. `distress_negative_affect`
3. `mental_health_reference_or_support`
4. `self_harm_related`

The meanings of existing tier values 0, 1, 2, and 3 remain unresolved. The
fields `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`,
confidence/probability fields, source tags, and undocumented model metadata
must not be used as ground truth, sampling criteria, or evidence for a new
annotation. No proposed label maps to any legacy tier value.

## Label rules

### `none_other`

Use only when none of the other three signal labels applies and the available
text is sufficiently clear. This covers neutral, unrelated, routine,
entertainment, promotional, or general text without a core signal. It must not
be combined with another signal label and must not be used to force an
ambiguous decision.

### `distress_negative_affect`

Use when the text explicitly expresses emotional strain, suffering,
hopelessness, loneliness, fear, overwhelm, sadness, anger, or related negative
affect. This describes wording in the post and does not imply a diagnosis or
clinical severity. Do not infer it from a merely negative event, isolated
keywords, metaphors, or unresolved figurative language.

### `mental_health_reference_or_support`

Use when the text meaningfully discusses mental-health experiences, care,
therapy, counselling, coping, recovery, wellbeing, support, or help-seeking.
It may co-occur with the other substantive labels. Do not infer it from an
isolated word, insult, metaphor, unrelated headline, or topic mention without
meaningful reference/support content.

### `self_harm_related`

Use when the text explicitly refers to self-harm, suicide, wanting to die,
attempts, planning, prevention, recovery, safety planning, or immediate safety
support related to those topics. Explicit prevention and recovery content may
receive this content label. This does not indicate current personal risk. Do
not infer it from vague sadness, figurative language, insults, or unresolved
phrases.

## Multi-label serialization

The three substantive labels may co-occur. Use only applicable labels in this
fixed order, separated by `|` with no spaces:

```text
distress_negative_affect|mental_health_reference_or_support|self_harm_related
```

`none_other` stands alone. Do not include context flags in the label field.
Uncertain cases are marked for review rather than force-labeled; uncertainty is
not a fifth signal class.

## Context flags

Store contextual information separately in `context_flags`. Approved values are:

- `first_person_or_self_report`
- `third_person`
- `quoted_or_reported`
- `educational_or_information`
- `fictional_or_hypothetical`
- `sarcastic_or_ironic`
- `promotional_or_campaign`
- `context_insufficient`

Multiple context flags may apply. Context flags are never signal labels.

For quoted, educational, fictional, hypothetical, and third-person content,
apply a content label only when the topic is clearly present in the text, add
the applicable context flag, and do not infer that the author personally
experienced the content. Sarcasm or irony must be flagged when reasonably
apparent; unresolved literal versus sarcastic meaning requires review.

If text is too short, incomplete, unreadable, language-limited, or dependent on
missing context, set the review field to `TRUE`, leave the signal label blank
when a reliable label cannot be assigned, and record a reason such as
`insufficient_context`, `ambiguous`, `sarcasm_or_irony`,
`quoted_or_reported`, `fictional_or_hypothetical`, `educational_context`, or
`language_or_encoding`.

## Privacy and annotator independence

Keep source data and annotations local. Do not upload raw posts publicly. Use
pseudonymous annotator IDs **A1** and **A2**, restrict access to authorized
project staff, and handle sensitive content carefully.

Annotators must work independently and must not see each other's labels or any
legacy tier/prediction metadata. Preserve both independent annotations for
later comparison. An adjudicator may review disagreements only after the
independent decisions are preserved.

## Approved pilot plan

- Exactly **60 posts** total.
- **20 YouTube**, **20 Reddit**, and **20 X/Twitter**.
- Fixed random seed: **42**.
- Primary sample includes only original or unspecified records.
- Explicitly synthetic/augmented YouTube rows are excluded from the primary sample.
- Sampling must not use tiers, keywords, predictions, confidence scores,
  probabilities, or undocumented model columns.
- The sample must keep platform identity and record IDs, leave annotation fields
  blank initially, and preserve raw datasets unchanged.

Duplicate and normalized-text-linked records must be recorded or flagged for
future leakage control. They must not be silently deleted, relabeled, or used
to alter existing split assignments.

## Files reviewed and document conflicts

The following were inspected before this revision:

- `reports/label_scheme_proposal.md`
- `reports/annotation_guidelines.md`
- `reports/annotation_template_report.md`
- `reports/annotation_readiness_report.md`
- `reports/data_quality_report.md`
- `reports/pilot_sampling_report.md`
- `Data/processed/annotation_template.csv`
- `Data/processed/pilot_annotation.csv`

The earlier proposal and guidelines remain unchanged. They contain optional
supporting labels and unresolved approval language; those options are excluded
for this approved pilot. The full annotation template remains unchanged.

A genuine artifact conflict remains: `Data/processed/pilot_annotation.csv`
already exists from an earlier run, and `reports/pilot_sampling_report.md`
records seed `20261019`, while this approved policy requires seed `42`. The
existing file was not modified or deleted. It must be treated as superseded or
separately reviewed; it does not satisfy the newly approved seed-42 plan.

## Remaining blockers before a seed-42 sample

1. Decide whether the existing seed-20261019 pilot file is retained as a
   superseded artifact and give the new seed-42 sample a separate filename, or
   obtain explicit permission to replace it. No replacement is created by this
   policy update.
2. Ensure the future seed-42 sample schema includes the approved separate
   `context_flags` field and both independent annotator field groups.
3. After sampling, complete independent A1/A2 annotation and disagreement
   review before any preparation pipeline or model work.

Unresolved tier provenance, legacy split semantics, duplicate groups, and the
future leakage-safe evaluation policy remain blockers for model training. They
do not alter the approved manual-pilot rules.

## Version and change history

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-10-19 | Initial proposed policy with unresolved operational decisions. |
| 0.2 | 2026-10-19 | Owner-approved four-label policy, fixed serialization, separate context flags, content/context rules, local privacy procedure, A1/A2 independence, 60-post seed-42 plan, synthetic-row exclusion, and legacy metadata prohibition. Existing seed-20261019 artifact documented as a conflict and left unchanged. |

