# Pilot-60 Final Readiness Report

## Scope

This report uses only the existing 60-record seed and adjudication workbook. It does not add posts, modify annotations, create splits, train a model, or make clinical claims. Labels describe observable text signals only.

## Current status

- Workbook rows: **60**; seed rows: **60**.
- IDs complete and unique against seed: **True**.
- Adjudication statuses: **{'completed': 60}**.
- Blank final labels: **0**.
- Final-policy issues found in this fresh audit: **0**.
- Fresh validation issue file: `reports\pilot60_final_validation_issues.csv`.

## A2 text mismatches

Two records retain `A2_text_mismatch=TRUE`: 95728c25-80b6-41e9-ad4c-f8566d580284, d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e.
Both have `source_text_verified=FALSE` and adjudication notes documenting that the canonical seed text was used. They were not silently repaired.

## Final label distribution

- Combined final label-set counts: **{'mental_health_reference_or_support': 11, 'distress_negative_affect': 12, 'none_other': 25, 'distress_negative_affect|self_harm_related': 2, 'distress_negative_affect|mental_health_reference_or_support': 5, 'distress_negative_affect|mental_health_reference_or_support|self_harm_related': 4, 'mental_health_reference_or_support|self_harm_related': 1}**.
- Platform coverage: YouTube=20, Reddit=20, Twitter/X=20.
- Descriptive distribution file: `reports\pilot60_label_distribution.csv`.

## Context and confidence

- Context flags: **{'first_person_or_self_report': 13, 'context_insufficient': 17, 'educational_or_information': 7, '<BLANK>': 11, 'promotional_or_campaign': 5, 'third_person|quoted_or_reported': 2, 'third_person': 1, 'fictional_or_hypothetical': 3, 'sarcastic_or_ironic': 1}**.
- Final confidence: **{'High': 34, 'Medium': 13, 'Low': 13}**.
- `context_insufficient` is an annotation context flag, not a clinical or risk category.

## Original A1/A2 agreement

The fresh IAA recalculation used original A1/A2 values, not final adjudicated labels. All 60 IDs matched, but only **8/60** pairs used the approved label vocabulary. Raw label-string agreement was 60/60 because both annotators retained the same older values; this is not evidence that the approved scheme was reliably applied. Policy-valid exact-set agreement was 8/8, with kappa undefined because the valid subset had no useful category variation. The IAA report also records 52 invalid labels per annotator, 50 invalid context rows per annotator, and two canonical-text mismatches per annotator.

## What this pilot supports

- It supports testing the annotation workflow, policy wording, adjudication process, and descriptive label reporting.
- It supports a small qualitative discussion of examples and annotation difficulties.
- It does not support reliable generalization or a defensible multi-label model performance claim: 60 records are small, platform-specific support is limited, rare-label estimates are unstable, and the original independent labels are largely non-policy values.
- It cannot establish clinical validity or diagnose any person.

## Decision and next step

**No baseline model should be trained from this pilot yet.** The most useful next step using these same 60 records is to preserve the fresh validation/IAA results, document the two canonical-text decisions, and use the pilot for a qualitative methods review. Any modeling attempt would be exploratory only and should wait for an approved larger annotation set and leakage-safe group policy.
