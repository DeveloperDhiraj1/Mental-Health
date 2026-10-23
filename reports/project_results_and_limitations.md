# Project Results and Limitations

## Pilot overview

The current pilot contains 60 adjudicated records: 20 YouTube, 20 Reddit, and 20 Twitter/X. The latest workbook has 60 completed records, zero blank final labels, and zero current policy-validation issues.

## Final label distribution

| Final label set | Count | Percentage |
|---|---:|---:|
| `none_other` | 25 | 41.67% |
| `distress_negative_affect` | 12 | 20.00% |
| `mental_health_reference_or_support` | 11 | 18.33% |
| `distress_negative_affect|mental_health_reference_or_support` | 5 | 8.33% |
| `distress_negative_affect|mental_health_reference_or_support|self_harm_related` | 4 | 6.67% |
| `distress_negative_affect|self_harm_related` | 2 | 3.33% |
| `mental_health_reference_or_support|self_harm_related` | 1 | 1.67% |

Because labels can co-occur, label-set percentages and per-signal incidence are different quantities. The machine-readable platform breakdown is in `reports/pilot60_platform_label_summary.csv`.

## Context findings

The most frequent context flags were `context_insufficient` (17) and `first_person_or_self_report` (13). Educational/information content occurred 7 times, promotional/campaign content 5 times, fictional/hypothetical content 3 times, third-person/quoted content 3 times in total, and sarcastic/ironic content once. Context flags describe presentation context; they do not establish personal experience.

## Agreement limitations

Original A1/A2 agreement cannot be interpreted as strong reliability for the approved scheme. Only 8 of 60 pairs were policy-valid. Although raw old-label string equality was 100%, many shared values were outside the approved vocabulary. The valid subset was too small and lacked useful variation for meaningful kappa.

## Quality and leakage risks

The raw audit found 64 normalized duplicate groups, 5 cross-platform duplicate groups, 74 near-duplicate candidates, and 125 synthetic YouTube rows. These records require group-aware handling in any future evaluation. The two documented A2 text mismatches remain flagged, even though adjudication used canonical seed text.

## Limitations

- Each platform has only 20 records, so platform differences may be random pilot variation.
- The sample is not prevalence-representative.
- Rare multi-label combinations have very small counts.
- Ambiguous, quoted, educational, fictional, sarcastic, and context-insufficient text can be difficult to annotate consistently.
- Legacy tier meanings and provenance remain unresolved.
- The pilot cannot support reliable predictive performance, generalization, clinical validity, or diagnostic conclusions.

## Interpretation

The pilot demonstrates that a non-clinical annotation and adjudication workflow can be applied and audited. It supports descriptive reporting and qualitative discussion of annotation decisions. It does not justify training or evaluating a baseline model.
