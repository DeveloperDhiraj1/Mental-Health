# Label-design proposal for non-clinical linguistic signals

## Purpose and scope

This is a research annotation proposal only. It does not reinterpret, overwrite, or replace the existing tier fields, and it does not define clinical severity or diagnose anxiety, depression, suicidality, or any other condition.

The proposal applies only to:

- Data/raw/youtube_data set.csv
- Data/raw/reddit_dataSet.csv
- Data/raw/twitter_data set.csv

All raw files, existing labels, duplicate records, and split assignments must remain unchanged. Any future annotations should be stored in a separate artifact with stable record references and documented provenance.

## What is verified and unknown about tier 0–3

Verified:

- Each dataset contains a field named tier with observed values 0, 1, 2, and 3.
- Related fields include tier_lexicon, tier_corrected, tier_model, tier_pred, tier_source, confidence values, and probability fields.
- Most rows are tagged lexicon in tier_source.
- YouTube contains 125 rows marked synthetic/augmentation.
- Reddit and X contain smaller groups marked corrected.
- split and model_split disagree for every row.
- The workspace contains no label dictionary, annotation guidelines, lexicon rules, correction logic, model code, or upstream data-generation documentation.

Unknown:

- The semantic meaning of each numeric tier.
- Whether tier is human-annotated, lexicon-derived, model-generated, corrected, or a mixture.
- Whether any tier is verified ground truth.
- Whether tier meanings are consistent across platforms.
- Which split field is authoritative.

The existing tier values must therefore be treated as unresolved legacy metadata. They must not be mapped to this proposal by numeric value, frequency, model prediction, or probability.

## Recommended annotation structure

A single mutually exclusive four-level label would lose important context. The recommended design is a small multi-label signal scheme plus separate context and certainty fields.

### Core linguistic-signal labels

An item may receive more than one core signal label.

#### none_other

Definition: No clear target linguistic signal from the core set is expressed in the available text.

Include ordinary conversation, unrelated information, entertainment, promotion, general commentary, and neutral text. Exclude text with a clear target signal and text that is too ambiguous to classify; use uncertainty for the latter.

Illustrative example: “The new library is open until eight and has quiet study rooms.”

#### distress_negative_affect

Definition: The text expresses emotional strain, suffering, hopelessness, loneliness, overwhelm, fear, persistent sadness, anger, or related negative affect, without requiring a diagnosis.

Include explicit expressions of emotional difficulty. Exclude a merely negative event with no emotional impact, sarcasm or quotation when the context is not a direct expression, and any conclusion requiring clinical knowledge.

Illustrative example: “I have felt overwhelmed and alone since everything changed.”

#### mental_health_reference_or_support

Definition: The text explicitly discusses mental-health experiences, care, coping, recovery, wellbeing, support, or help-seeking without being treated as a diagnosis.

Include requests for help or resources and discussion of counselling, therapy, recovery, wellbeing, or supporting someone. Exclude an isolated keyword, an insult or metaphor, or content that is only a news/educational reference when the research question excludes topic-only discussion.

Illustrative example: “Does anyone know practical ways to find affordable counselling?”

#### self_harm_related

Definition: The text contains explicit reference to self-harm, suicide, wanting to die, plans or attempts, or direct prevention/safety discussion related to those topics.

Include direct discussion of self-harm-related thoughts, behavior, intent, planning, attempts, recovery, prevention, or immediate safety help. Exclude clearly figurative, fictional, quoted, sarcastic, or unrelated uses, and do not infer intent from vague sadness.

Illustrative example: “I am worried about a friend who says they may hurt themselves; what immediate support is available?”

This is a linguistic content label, not a risk score, severity level, or clinical conclusion.

### Optional supporting labels

Add these only if required by the research question:

- help_seeking: explicit request for advice, support, resources, or professional help.
- protective_or_recovery_language: coping, recovery, safety planning, social support, or improvement language.
- diagnostic_term_mentioned: a diagnostic or treatment term is mentioned, without asserting that the author has that condition.

These are not clinical-status labels.

## Context labels

Each item should receive one or more context flags:

- first_person_or_self_report
- third_person
- quoted_or_reported
- educational_or_information
- fictional_or_hypothetical
- sarcastic_or_ironic
- promotional_or_campaign
- context_insufficient

Multiple flags are allowed. For example, a quoted educational post can have both quoted_or_reported and educational_or_information.

The same words must not be treated as a first-person experience when they occur in a quotation, headline, educational explanation, fictional scenario, or report about someone else.

## Uncertainty and difficult cases

Use a separate uncertainty field:

- clear
- ambiguous
- insufficient_context
- unreadable_or_corrupted
- out_of_scope

Do not force an ambiguous item into none_other. Do not infer a signal from a platform stereotype or existing tier. If literal intent, sarcasm, quotation, or context cannot be resolved, preserve the uncertainty reason and send the item to adjudication or an uncertainty slice.

Handling rules:

- Sarcasm/irony: flag the context; do not assign a signal from an idiom alone.
- Quoted/reported text: flag it and do not treat the quote as the author's own experience.
- Educational text: separate topic discussion from self-report.
- Fiction/hypothetical/lyrics: do not treat characters or imagined scenarios as author experience.
- Context-dependent text: use context_insufficient or ambiguous when the available text is inadequate.
- Mixed language, emojis, URLs, usernames, hashtags, and negations: inspect original text and avoid destructive normalization.

## Human annotation protocol

1. Write an annotation manual with definitions and counterexamples.
2. Train annotators on a small pilot from each platform.
3. Have at least two independent annotators label the same pilot and calibration items.
4. Use an adjudicator for disagreements while retaining the independent labels.
5. Report per-label agreement, such as Cohen kappa, Krippendorff alpha, and label-wise F1 after the label structure is finalized.
6. Track disagreement reasons including quotation, sarcasm, educational context, ambiguous wording, language/encoding, and insufficient context.
7. Version every change to the manual.

Agreement should be measured separately for signal labels, context labels, and uncertainty. Low agreement means the label is underspecified; it is not evidence of clinical truth.

## Held-out evaluation design

The current split and model_split fields should not be trusted as evaluation definitions until their provenance is recovered.

For a later evaluation set:

- Create a new frozen human-annotated artifact without changing the raw CSVs.
- Keep annotators blind to tier, tier_model, tier_pred, probabilities, and source tags.
- Prevent exact duplicate text across development and evaluation partitions.
- Keep augmented items with the same parent_record_id in one partition.
- Consider grouping by anonymized user ID within each platform.
- Keep the three shared Reddit/YouTube text groups in one partition or exclude them from cross-platform evaluation until their origin is understood.
- Report results separately by platform, label, context type, language, and uncertainty status.
- Include an uncertain slice and report abstention/coverage instead of forcing every item into a class.

## Platform strategy

The three platforms should initially be annotated separately.

Reasons:

- Existing tier distributions differ substantially.
- Provenance tags and synthetic content are not identical.
- Reddit discussions, YouTube comments, and X posts have different context, length, quoting, and reposting behavior.
- The reports show cross-platform text overlap and unresolved split semantics.
- A shared label system should be demonstrated through cross-platform agreement, not assumed from common column names.

Recommended sequence:

1. Apply the same conceptual manual independently within each platform.
2. Measure agreement and label prevalence per platform without treating prevalence as class meaning.
3. Review platform-specific failures and revise the manual.
4. Test whether annotators apply the definitions consistently across platforms.
5. Only then consider a shared harmonized dataset or cross-platform model target.

Preserve platform identity and platform-specific context/uncertainty analyses.

## Main recommendation

Do not map or replace tiers 0–3. Use a separately versioned annotation scheme consisting of multi-label linguistic signals, context flags, and an explicit uncertainty field. Start with separate human annotation for YouTube, Reddit, and X while preserving platform identity and source provenance.

The next practical step is a privacy-preserving, stratified pilot from each platform using this manual. Review agreement and difficult cases before annotating a larger set or designing a model. This is non-clinical linguistic-signal research only.
