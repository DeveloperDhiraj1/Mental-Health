# Annotation Batch v2 Guide

## Status and scope

This guide applies to the blank `annotation_batch_v2_20261029` templates. It uses the owner-approved policy as a research annotation proposal. Labels describe observable text signals only; they are not diagnoses, clinical severity scores, or personal-risk assessments.

## Independent files

- A1: `Data/processed/annotation_batch_v2_20261029/A1_annotation.csv`
- A2: `Data/processed/annotation_batch_v2_20261029/A2_annotation.csv`
- Both files contain the same canonical IDs and text, but must be reviewed independently.
- Do not open the other annotator's file and do not use legacy tiers, predictions, probabilities, keyword scores, or model metadata.

## Approved labels

Use only:

- `none_other`
- `distress_negative_affect`
- `mental_health_reference_or_support`
- `self_harm_related`

The three substantive labels may co-occur in this exact order, separated by `|` with no spaces:

`distress_negative_affect|mental_health_reference_or_support|self_harm_related`

`none_other` must be used alone. Do not use old values or `+` separators. Leave `proposed_label` blank until the row is actually reviewed.

## Context flags

Keep flags separate from signal labels. Approved flags are:

`first_person_or_self_report`, `third_person`, `quoted_or_reported`, `educational_or_information`, `fictional_or_hypothetical`, `sarcastic_or_ironic`, `promotional_or_campaign`, `context_insufficient`.

Use `|` between multiple flags. A flag does not prove that the author personally experienced the topic.

## One-row procedure

1. Read the complete canonical `post_text`.
2. Select only clearly observable content signals.
3. Add context flags independently.
4. Add a short text-based rationale without diagnosing or inferring personal risk.
5. Set `annotation_status` to `completed` only when finished.
6. Set `needs_review` and explain the reason when context is missing, sarcasm is unclear, content is quoted/fictional/educational and interpretation is uncertain, or the post is unreadable.

Quoted, educational, fictional, hypothetical, third-person, prevention, and recovery content can receive a content label when the topic is clearly present. Do not infer that the author personally experienced it. `self_harm_related` is a content label and does not indicate current personal risk.

## Adjudication and validation

After A1 and A2 independently complete their files, preserve both originals. Run:

```powershell
python src\validate_next_annotation_batch.py --batch-dir Data\processed\annotation_batch_v2_20261029
```

Then compare by `record_id`, preserve disagreements, and adjudicate separately. Never silently repair the source text or automatically map old labels.

The two earlier pilot text-mismatch IDs are recorded separately in the batch folder for human decision; they are not included in this new batch.
