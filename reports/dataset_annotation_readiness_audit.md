# Dataset and Annotation Readiness Audit

## Scope

Fresh audit of the three current raw datasets, Phase 1 derived quality metrics, and the existing 60-record human adjudication pilot. Original datasets and annotation files were read only. No labels were inferred, no split was created, and no model was trained.

## Raw dataset findings

- Combined rows: **4739**.
- Platform rows: **{'youtube': 1971, 'reddit': 1302, 'twitter': 1466}**.
- Encodings: YouTube `cp1252`; Reddit and Twitter/X `utf-8-sig`.
- Each source has 51 columns; record IDs and post text are non-empty in the current strict load.
- Normalized exact-text groups: **64**; near-duplicate candidates: **74**; augmentation parent groups: **30**.
- YouTube synthetic/augmented rows: **125**. They are retained in the canonical corpus but excluded from the primary 60-post pilot.
- No duplicate record-ID extras, exact full-row duplicate extras, or empty text rows were found by the Phase 1 run.

## Label provenance and leakage

- Legacy `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, probability/confidence, lexicon, model, augmentation, and split fields remain untrusted metadata.
- The meanings of legacy tier values 0–3 and the construction of `split`/`model_split` remain undocumented locally.
- Legacy fields must not be targets or default model features. Duplicate text, near-duplicates, repeated users, and parent-child augmentation relationships require group-aware evaluation controls.

## Human annotation status

- Reviewed workbook rows: **60**; canonical seed rows: **60**.
- Complete, unique seed-ID coverage: **True**.
- Verified usable final labels under the approved vocabulary and completed status: **60**.
- Final label-set distribution: **{'mental_health_reference_or_support': 11, 'distress_negative_affect': 12, 'none_other': 25, 'distress_negative_affect|self_harm_related': 2, 'distress_negative_affect|mental_health_reference_or_support': 5, 'distress_negative_affect|mental_health_reference_or_support|self_harm_related': 4, 'mental_health_reference_or_support|self_harm_related': 1}**.
- Platform coverage of verified labels: **{'youtube': 20, 'reddit': 20, 'twitter': 20}**.
- A2 canonical-text mismatches retained and documented: **2**; IDs are recorded in the machine-readable summary, not repaired here.
- Original A1/A2 rows: **60 / 60**; ID sets match: **True**.
- Phase 1 joined the 60 reviewed rows to raw records; **4679** raw rows have no verified human label.

## Readiness decision

**NO-GO for model training and meaningful evaluation at this stage.** The verified label count is only 60 of 4,739 records, with 20 records per platform. This is sufficient for workflow and qualitative analysis, not reliable multi-label generalization or performance claims. The original A1/A2 labels are largely outside the approved vocabulary, so their agreement cannot substitute for a larger policy-conforming annotation set.

## Required next action

Obtain supervisor approval for a larger annotation batch, keep independent annotation and adjudication separate, retain synthetic records as a separate stratum, and freeze a group-aware evaluation policy before any model training. Group normalized duplicate text, conservative near-duplicate candidates after review, repeated users where available, cross-platform copies, and augmentation parent-child records together. Only approved human-reviewed labels may become targets.

This project studies non-clinical linguistic signals. Labels do not diagnose a person or estimate clinical condition or risk.
