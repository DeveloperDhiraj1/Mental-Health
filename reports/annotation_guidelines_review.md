# Annotation Guidelines Review

## Status: PROPOSED — NOT APPROVED

This document is a proposed manual for human review of observable linguistic
signals in social-media text. It is not clinically validated, does not measure
clinical severity, and must not be used to diagnose the author or infer a
condition. A human project owner must approve the scheme before annotation
begins.

The current annotation template contains 4,739 unlabeled rows from YouTube,
Reddit, and X/Twitter. This review does not modify that template, assign any
labels, modify raw data, or change splits.

## Existing tier values remain unresolved

The available provenance evidence confirms that the raw files contain `tier`
values 0, 1, 2, and 3 and related fields such as `tier_lexicon`,
`tier_corrected`, `tier_model`, `tier_pred`, source tags, and probabilities.
However, no local documentation or code establishes:

- what tier 0, 1, 2, or 3 means;
- whether any tier is human-annotated or verified ground truth;
- how lexicon, correction, model, or augmentation fields were generated; or
- whether the tiers have the same meaning across platforms.

Therefore, the proposed labels below are independent of the legacy tiers. No
numeric mapping, frequency-based interpretation, or model-output mapping is
allowed.

## Proposed label structure

Use a small multi-label core scheme for clear text signals. A post may receive
more than one core signal when the text supports that decision. Record context
and uncertainty separately. `uncertain_needs_review` is a review status and
must not be treated as a positive signal class.

### 1. `none_other`

**Definition:** No clear signal from the core scheme is expressed in the
available text.

**Include when:**

- the text is ordinary conversation or unrelated commentary;
- the text discusses a routine event without emotional-signal content;
- the text is entertainment, promotion, or general information without a core signal;
- a mental-health word appears only as an irrelevant keyword or metaphor; or
- the annotator can confidently determine that no core signal is present.

**Exclude when:**

- clear emotional strain or suffering is expressed;
- the post meaningfully discusses mental-health support, care, coping, or wellbeing;
- explicit self-harm-related content is present; or
- the available context is too incomplete to decide, in which case use review status.

**Illustrative examples:**

1. “The library closes at eight tonight.”
2. “This recipe needs two cups of rice.”
3. “The bus was late, but I caught the next one.”
4. “The new game update is available today.”
5. “Here are photos from the weekend market.”

These examples are illustrative only; annotators must consider the full available
post text.

### 2. `distress_negative_affect`

**Definition:** The text explicitly expresses emotional strain, suffering,
hopelessness, loneliness, fear, overwhelm, persistent sadness, anger, or
related negative affect, without requiring a diagnosis.

**Include when:**

- the author directly describes feeling emotionally distressed or overwhelmed;
- the text describes loneliness, hopelessness, or sustained sadness as an experience;
- the emotional effect of an event is explicitly stated;
- the wording communicates suffering without requiring clinical interpretation; or
- the text combines negative affect with a separate support or help-seeking signal.

**Exclude when:**

- only a negative event is described with no emotional impact;
- the wording is clearly an idiom, joke, quotation, fictional line, or sarcasm and not a clear signal;
- the annotator would need to infer a diagnosis or severity; or
- the text is too incomplete to distinguish literal distress from figurative language.

**Illustrative examples:**

1. “I have felt overwhelmed and alone since everything changed.”
2. “I cannot stop worrying about what will happen tomorrow.”
3. “Lately I feel empty and exhausted most days.”
4. “I am struggling to cope with this loss.”
5. “The constant pressure is making me feel hopeless.”

These statements are text-signal examples, not evidence of a clinical condition.

### 3. `mental_health_reference_or_support`

**Definition:** The text meaningfully discusses mental-health experiences,
care, coping, recovery, wellbeing, support, or help-seeking without treating
the text as a diagnosis.

**Include when:**

- the post asks for counselling, therapy, crisis resources, or other support;
- it discusses coping, recovery, wellbeing, or emotional support in a meaningful way;
- it discusses supporting another person with a mental-health concern;
- it describes a care or support experience without asserting a clinical label; or
- it provides relevant support information while clearly marked as educational or public information.

**Exclude when:**

- the term is an isolated keyword, insult, or metaphor;
- the post is only an unrelated headline or topic mention;
- the content is too ambiguous to establish meaningful reference; or
- the annotator would need to infer that the author has a condition.

**Illustrative examples:**

1. “Does anyone know where to find affordable counselling?”
2. “Talking with a trusted friend helped me get through a difficult week.”
3. “What are some practical ways to support a friend who is struggling?”
4. “I started therapy and I am learning ways to manage stressful days.”
5. “This post explains how to access local emotional-support services.”

An educational example receives the relevant context flag as well.

### 4. `self_harm_related`

**Definition:** The text explicitly refers to self-harm, suicide, wanting to
die, attempts, planning, prevention, recovery, or immediate safety support
related to those topics.

**Include when:**

- the text directly discusses self-harm-related thoughts or behavior;
- it asks for or offers immediate safety or prevention support;
- it reports a direct concern about another person's self-harm-related statement;
- it discusses an attempt, recovery, prevention, or safety planning; or
- the topic is explicit even when the text is educational, quoted, or third-person.

**Exclude when:**

- the wording is clearly figurative, sarcastic, fictional, or unrelated;
- a vague expression of sadness contains no explicit self-harm-related reference;
- the content merely uses a phrase as an insult or exaggeration; or
- the annotator must guess the meaning from missing context.

This is a content label, not a risk score, severity rating, prediction of action,
or clinical conclusion.

**Illustrative examples:**

1. “I am worried because my friend says they may hurt themselves.”
2. “Where can someone find immediate help for thoughts of suicide?”
3. “The lesson discusses preventing self-harm and finding support.”
4. “After the attempt, they began a recovery and safety plan.”
5. “I had thoughts of hurting myself and need help staying safe tonight.”

Annotators should follow the project’s approved safety and escalation procedure
for viewing such content; annotation itself is not crisis intervention.

### 5. `uncertain_needs_review`

**Definition:** The available text cannot be assigned a reliable signal label
under the written rules without guessing. This is an explicit review outcome,
not a claim that the post contains or lacks a signal.

**Include when:**

- the post is too short or lacks necessary surrounding context;
- sarcasm, irony, metaphor, or quotation cannot be resolved;
- it is unclear whether the text is personal, third-person, educational, or fictional;
- encoding or language issues make the meaning unreliable; or
- two annotators reach different labels.

**Exclude when:**

- a label can be applied confidently from the available text;
- the post is simply neutral or unrelated, which belongs under `none_other`; or
- the annotator is uncertain only because of the unresolved legacy tiers, which must be ignored rather than used as evidence.

**Illustrative examples:**

1. “I cannot do this anymore.” — context is missing.
2. “That meeting was absolutely killing me.” — literal or figurative meaning is unclear.
3. “They said, ‘I want to disappear,’ but no surrounding context is available.”
4. “A character in the story says the same thing.” — source/context may be unclear in a short excerpt.
5. “I feel fine :)” — the emoji or surrounding context may make sincerity unclear.

Annotators must record a specific `review_reason`, such as
`insufficient_context`, `sarcasm_or_irony`, `quoted_or_reported`,
`fictional_or_hypothetical`, `educational_context`, `language_or_encoding`, or
`annotator_disagreement`.

## Context rules

Record context flags separately from core signal labels where the approved
template permits. Suggested flags are:

- `first_person_or_self_report`
- `third_person`
- `quoted_or_reported`
- `educational_or_information`
- `fictional_or_hypothetical`
- `sarcastic_or_ironic`
- `promotional_or_campaign`
- `context_insufficient`

### Ambiguous or insufficient context

Do not fill gaps using platform stereotypes, legacy tiers, probabilities,
keywords, or assumptions about the author. Use `uncertain_needs_review`, low or
medium confidence, and a reason. Do not force an uncertain item into
`none_other`.

### Sarcasm and irony

Mark `sarcastic_or_ironic` when reasonably apparent. Do not label an idiom as a
literal signal. If the intended meaning cannot be resolved, use
`uncertain_needs_review`.

### Quotations and reported speech

Mark `quoted_or_reported`. The content can receive a topical signal if the
approved study wants content labels, but it must not automatically be treated
as the annotator's or author's own experience. If the study excludes quoted
content from the target, apply that decision consistently after approval.

### Educational or informational content

Mark `educational_or_information`. Topic discussion alone is not evidence that
the author experiences the topic. The project owner must approve whether
explicit prevention/support information receives the corresponding content
label.

### Fiction, hypothetical writing, and lyrics

Mark `fictional_or_hypothetical`. Do not treat a character, imagined scenario,
or lyric as the author's personal experience. If the research target is text
content rather than author self-report, the project owner must approve whether
explicit topic labels remain applicable.

### Negation, emojis, URLs, usernames, and mixed language

Read the original text. Preserve negation and relevant context. Do not remove
emojis, URLs, usernames, hashtags, or non-English text during annotation. Mark
`language_or_encoding` or `uncertain_needs_review` when meaning cannot be
reliably understood.

## Annotation fields and independence

For each item, a human annotator should enter:

- `annotator_label`: one or more approved core labels, or the explicit review outcome;
- `confidence`: `high`, `medium`, or `low`, referring to rule clarity rather than clinical certainty;
- `needs_review`: `TRUE` when the item is ambiguous, context-limited, unreadable, or disputed; and
- `review_reason`: a concise reason when review is needed.

Do not consult `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`,
`tier_pred`, confidence/probability columns, or source tags while assigning a
new annotation. Preserve the original `record_id`, platform, text, and
`record_type`.

## Pilot procedure: 50–100 posts

Before full annotation, conduct a pilot of 50–100 posts with representation
from YouTube, Reddit, and X/Twitter where possible. Use a fixed random seed and
record the source record IDs and sampling method. Do not sample or label using
legacy tiers, keywords, predictions, or probabilities. Keep synthetic/augmented
rows explicitly identified and follow a human-approved policy for their pilot
treatment.

1. The project owner approves this proposed scheme and all unresolved choices below.
2. Create one fixed pilot list as a separate artifact; do not alter raw CSVs.
3. Two annotators independently label every pilot item, using separate copies or separate protected annotation columns.
4. Annotators record label, confidence, review status, and reason without seeing each other's decisions or legacy metadata.
5. Compare labels per core signal and context flag; report raw agreement and Cohen's kappa when applicable, noting small-sample and imbalanced-label limitations.
6. An adjudicator reviews disagreements while preserving both original annotations and records the reason for each decision.
7. Revise the manual when disagreement reveals an unclear rule, then document the version used for any subsequent annotation.
8. Proceed to larger annotation only after the pilot review shows that the rules are understandable and the project owner approves the revised manual.

Pilot agreement is evidence about annotation consistency, not evidence that a
label is clinically valid.

## Decisions requiring human approval

Before annotation begins, the project owner must approve:

- the four core signal labels and whether `uncertain_needs_review` is stored as a status or separate field;
- multi-label serialization in `annotator_label`;
- whether `none_other` can coexist with support, recovery, or educational content labels;
- whether quoted, fictional, educational, and third-person content receives content labels, context flags only, or review status;
- whether self-harm prevention, recovery, and safety information receives `self_harm_related`;
- treatment and sampling of the 125 synthetic/augmented YouTube rows;
- annotator identity, privacy, access control, and escalation procedures for sensitive content;
- the final pilot composition, random seed, and disagreement/adjudication process; and
- the leakage-safe policy for duplicate text, repeated users, parent records, and cross-platform overlap before any future evaluation split.

Until those decisions are approved and pilot agreement is reviewed, this file
remains **PROPOSED — NOT APPROVED**.

