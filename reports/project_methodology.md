# Project Methodology

## Research objective and scope

This project studies observable linguistic signals in social-media text. It is a non-clinical research prototype: labels describe text content and context, not a person's diagnosis, clinical severity, or current risk. The current documentation covers a 60-record pilot only.

## Data sources and platforms

The project uses three local CSV datasets representing YouTube, Reddit, and Twitter/X. Their exact upstream source and legacy label provenance remain incompletely documented. The raw files were read without changing them. Platform identity, record IDs, text, timestamps, anonymized user IDs, and augmentation metadata were retained for audit purposes.

## Pilot sampling

The pilot contains exactly 60 records: 20 YouTube, 20 Reddit, and 20 Twitter/X. It was sampled with Python random seed 42 from original or unspecified records. The 125 YouTube rows explicitly marked synthetic/augmented were excluded from the primary pilot sample. No legacy tier, keyword, prediction, probability, or confidence field was used to assign labels.

## Annotation scheme

The approved labels are non-ordinal content categories:

- `none_other`: none of the substantive signals is clearly present.
- `distress_negative_affect`: explicit distress, suffering, hopelessness, fear, overwhelm, sadness, or related negative affect in the text.
- `mental_health_reference_or_support`: meaningful discussion of mental-health experiences, care, therapy, coping, recovery, wellbeing, support, or help-seeking.
- `self_harm_related`: explicit discussion of self-harm, suicide, attempts, planning, prevention, recovery, safety planning, or related support.

The three substantive labels may co-occur in fixed pipe-delimited order. `none_other` must stand alone. Context flags are stored separately, including first-person/self-report, third-person, quoted/reported, educational/information, fictional/hypothetical, sarcastic/ironic, promotional/campaign, and context-insufficient. These flags do not indicate a diagnosis or personal experience.

## Annotation and adjudication procedure

Two annotators worked independently using separate work copies. Their original annotations were preserved and compared without replacing them with adjudicated labels. A manual adjudication workbook then used the canonical seed text, retained both original judgments, recorded final labels/context flags, and stored rationale notes. The current workbook contains 60 completed adjudications and no blank final labels.

## Validation and agreement analysis

Fresh validation checks confirm 60 unique seed IDs, policy-valid final labels/context flags, completed statuses, and no current validation issues. Two A2 text mismatches remain explicitly flagged and documented; canonical seed text was used in adjudication.

Original A1/A2 agreement was analyzed separately from final labels. All 60 IDs matched, but only 8/60 pairs used the approved label vocabulary. Raw label-string equality was 60/60 because both annotators retained the same older values; this does not demonstrate reliable application of the approved scheme. Kappa was undefined on the small, non-varying valid subset.

## Data quality and leakage checks

The broader audit found 4,739 raw rows, 64 normalized duplicate-text groups, 5 cross-platform duplicate groups involving 16 records, and 74 conservative near-duplicate candidates. YouTube contains 125 synthetic/augmented rows. User, duplicate, parent-child, platform, and timestamp fields were identified for future grouping. Legacy tiers, lexicon outputs, model predictions, confidence/probability fields, and unresolved split columns are not treated as ground truth or safe evaluation features.

## Ethical limitations

The project does not diagnose mental-health conditions, infer a person's private state, or estimate clinical or suicide risk. Sensitive text must remain local and reports should avoid unnecessary raw text, usernames, or user identifiers. The pilot is small and non-representative; results are descriptive and methodological only.
