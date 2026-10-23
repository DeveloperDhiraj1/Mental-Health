# Project Next-Phase Plan

## Current status

The 60-record pilot is complete for descriptive and qualitative analysis. It is not sufficient for defensible baseline-model evaluation. No model or train/test split should be created from it at this stage.

## Planned next steps

1. **Supervisor review:** obtain written approval for the label policy, privacy procedure, annotation coverage target, and evaluation protocol.
2. **Annotation-quality review:** preserve the current A1/A2 files, fresh validation outputs, adjudication notes, and the two canonical-text mismatch decisions. Do not silently rewrite older annotations.
3. **Larger annotation, if authorized:** prepare a new platform-balanced and ambiguity-aware batch. Keep A1 and A2 independent, retain synthetic rows as a separate stratum, and record duplicate/parent relationships.
4. **Agreement monitoring:** calculate valid-pair agreement, per-label agreement, disagreement reasons, and unresolved-case rates. Revise guidelines if agreement remains weak.
5. **Leakage-safe evaluation design:** group exact duplicates, confirmed near-duplicates, repeated users, cross-platform copies, and augmentation parent-child records before splitting. Keep the test set frozen before model tuning.
6. **Feature policy:** exclude legacy tiers, lexicon outputs, predictions, probabilities, undocumented model outputs, and unresolved split metadata from targets and default features.
7. **Baseline model only after approval:** if annotation size, label support, agreement, and split controls become adequate, begin with an interpretable text-classification baseline and report per-label metrics with uncertainty. This is future work, not an action performed here.

## Ethical boundary

All future outputs must remain about linguistic signals in text. They must not be presented as a diagnosis, clinical severity estimate, or individual suicide-risk prediction.

## Immediate safe action

Use the current pilot reports in the project documentation and supervisor review. Do not add records, modify labels, train a model, or create data splits until the unresolved provenance, annotation-scale, and leakage-policy decisions are formally approved.
