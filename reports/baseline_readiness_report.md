# Baseline Model Readiness Gate

## Decision

**NO-GO for baseline training and train/validation/test splitting from the current 60-record pilot.** This gate is an engineering safeguard; it does not assign labels or modify data.

## Verified counts

- Canonical corpus rows: **4739**.
- Validated human-labeled rows: **60**.
- Unlabeled rows: **4679**; no labels were inferred.
- Platform counts among labeled rows: `{'youtube': 20, 'reddit': 20, 'twitter': 20}`.
- Signal incidence: `{'mental_health_reference_or_support': 21, 'distress_negative_affect': 23, 'none_other': 25, 'self_harm_related': 7}`.
- Invalid reviewed labels: **0**.

## Why training is blocked

- The pilot has only 60 labeled records and 20 per platform.
- The rare `self_harm_related` signal occurs only 7 times overall and only once on Twitter/X; a three-way split would make validation/test support unstable or empty.
- The approved project coverage plan calls for at least 30 adjudicated positive instances per substantive signal and at least 100 policy-valid adjudicated records per platform before an initial platform-aware analysis. Current deficits are distress: 7, mental-health reference/support: 9, and self-harm-related: 23 against that planning threshold.
- The original A1/A2 agreement analysis had only 8/60 policy-valid pairs, so the pilot is not strong evidence for reproducible independent labeling.
- No independent test set can be claimed from this pilot; reusing it for training and evaluation would produce unreliable performance estimates.

## Leakage checks available for the pilot

- The Phase 1 corpus reports no exact duplicate text group inside the 60 reviewed records, no parent links, and no synthetic rows among the reviewed records.
- Future splitting must still group exact/near duplicates, users, and augmentation parent-child records from the full corpus.
- Legacy tiers, lexicon outputs, model predictions, confidence/probability fields, and split columns remain excluded from targets and features.

## Exact additional annotation needed

No additional labels were created in this phase. To reach the project's existing planning threshold, obtain supervisor-approved independent annotations and adjudication for at least 300 new genuine records (approximately 100 per platform), while monitoring rare-label support. At minimum, the project needs 23 additional adjudicated `self_harm_related` positives, 9 additional `mental_health_reference_or_support` positives, and 7 additional `distress_negative_affect` positives to reach 30 each overall; these are planning targets, not fabricated labels or guarantees.

## Outputs and reproducibility

- Machine-readable summary: `reports\baseline_readiness_summary.json`.
- Existing Phase 1 tests remain separate and passing.
- No split manifests, model artifact, training script, or evaluation metrics were created because the gate failed.

All labels remain non-clinical text-content annotations and do not indicate diagnosis or clinical risk.
