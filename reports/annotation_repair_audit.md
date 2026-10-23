# Annotation Repair Audit

## Scope and read-only status

This is a read-only investigation. No original annotation, source sample,
policy, report, split, or raw dataset was edited, normalized, relabeled, merged,
or overwritten. No model was trained.

The labels below describe annotation-file values and policy compliance only;
they are not clinical conclusions about any author.

## Files inspected

- `reports/pilot_annotation_policy.md`
- `Data/processed/pilot_annotation_seed42.csv`
- `Data/processed/annotation_work/A1_annotation.csv`
- `Data/processed/annotation_work/A2_annotation.csv`
- `Data/processed/annotation_work/annotation_comparison.csv`
- `Data/processed/annotation_work/adjudication_queue.csv`
- `reports/annotation_agreement_report.md`
- `reports/annotation_guidelines.md`
- `reports/annotation_guidelines_review.md`
- `reports/label_scheme_proposal.md`

The open-tab name `A1_annotation_edited.csv` is not an actual file in the
annotation-work directory. The actual A1 file is
`Data/processed/annotation_work/A1_annotation.csv`.

## Approved policy used for validation

The owner-approved policy version 0.2 allows only:

- `none_other`
- `distress_negative_affect`
- `mental_health_reference_or_support`
- `self_harm_related`

The three substantive labels may be combined in the fixed `|` order;
`none_other` must stand alone. Approved context flags are separate from signal
labels and include `first_person_or_self_report`, `third_person`,
`quoted_or_reported`, `educational_or_information`,
`fictional_or_hypothetical`, `sarcastic_or_ironic`,
`promotional_or_campaign`, and `context_insufficient`.

Legacy tiers and undocumented metadata are not ground truth.

## Structural findings

- A1 rows: **60**.
- A2 rows: **60**.
- Same record-ID set: **yes**.
- A1/A2 platform mismatches: **0**.
- A1/source platform mismatches: **0**.
- A1/source post-text mismatches: **0**.
- A2/source post-text mismatches: **2**.
- Blank `annotator_label` values: A1 **0**, A2 **0**.
- Blank `context_flags` values: A1 **0**, A2 **0**.
- Blank `annotator_confidence` values: A1 **0**, A2 **0**.
- Blank `needs_review` values: A1 **0**, A2 **0**.

## Exact A2/source post-text mismatches

Comparison was by exact `record_id`; no normalization or whitespace repair was
applied. In both cases the A2 value is a truncated prefix of the seed-source
text.

### `95728c25-80b6-41e9-ad4c-f8566d580284`

**Seed source text:**

```text
@Harry_The_Nerd @xayyush Modular monolith woh joint family hai jisme har ek ko apna alag room + bathroom mil gaya! 

Ladai ho toh sirf apne floor tak limited, baaki ghar shanti. Phir bhi ek hi building hai � AC kharab hua toh pura floor pareshan!  

Microservices ne society bana li alag-alag towers ki.
```

**A2 text:**

```text
@Harry_The_Nerd @xayyush Modular monolith woh joint family hai jisme har ek ko apna alag room + bathroom mil gaya! 

Ladai ho toh sirf apne floor tak limited, baaki ghar shanti. Phir bhi ek hi building hai � AC kharab hua toh pura floor pareshan!  

Mic
```

Difference: A2 stops after `Mic`; the source continues with `roservices ne society bana li alag-alag towers ki.`

### `d1f879bb-0b96-4aab-b2e6-7ee5b4b8c99e`

**Seed source text:**

```text
@CrazyG10624 @subhi_karma Vo shareef aadmi Atul Subhash ko itna pareshan kiya gaya ki usne suicide kar liya. Uski maut ke baad bhi kuch ladkiyon ne use gaaliyan di. Aur yeh case dekh shaadishuda Muslim, jo 4-4 bachchon ka baap hai, uske saath live-in relationship mein reh rahi hai.
https://t.co/Kfvcaa5ix9
```

**A2 text:**

```text
@CrazyG10624 @subhi_karma Vo shareef aadmi Atul Subhash ko itna pareshan kiya gaya ki usne suicide kar liya. Uski maut ke baad bhi kuch ladkiyon ne use gaaliyan di. Aur yeh case dekh shaadishuda Muslim, jo 4-4 bachchon ka baap hai, uske saath live-in rela
```

Difference: A2 stops after `rela`; the source continues with `tionship mein reh rahi hai.` and the URL `https://t.co/Kfvcaa5ix9`.

These records require manual source-text restoration or exclusion from later
analysis, but neither action was performed here.

## A1 value counts

### `annotator_label`

| Value | Count | Policy status |
|---|---:|---|
| `mental_health_self_report` | 6 | Invalid/unknown |
| `mental_health_reference_or_support` | 25 | Approved label |
| `non_mental_health` | 25 | Invalid/unknown; not automatically `none_other` |
| `suicidal_ideation_or_hopelessness` | 3 | Invalid/unknown |
| `suicidal_self_report` | 1 | Invalid/unknown |

### `context_flags`

| Value | Count | Policy status |
|---|---:|---|
| `first_person_or_self_report` | 10 | Approved |
| `mental_health_reference` | 21 | Invalid context vocabulary |
| `unrelated_or_neutral` | 25 | Invalid context vocabulary |
| `support_or_advice` | 4 | Invalid context vocabulary |

### Other fields

| Field | Values and counts |
|---|---|
| `annotator_confidence` | `High`: 37; `Low`: 23 |
| `needs_review` | `FALSE`: 56; `TRUE`: 4 |
| Blank values | None in the four inspected annotation fields |

`High` and `Low` are case variants of the policy vocabulary `high` and `low`,
but this audit does not rewrite them. `needs_review` values are valid boolean
strings.

## A2 value counts

### `annotator_label`

| Value | Count | Policy status |
|---|---:|---|
| `mental_health_self_report` | 4 | Invalid/unknown |
| `mental_health_reference_or_support` | 8 | Approved label |
| `non_mental_health` | 39 | Invalid/unknown; not automatically `none_other` |
| `suicidal_ideation_or_hopelessness` | 1 | Invalid/unknown |
| `non-mental_health_or_support` | 1 | Invalid/unknown |
| `mental_health_advice` | 1 | Invalid/unknown |
| `suicidal_self_report` | 1 | Invalid/unknown |
| `Depression_or_hopelessness` | 1 | Invalid/unknown |
| `non_mental_health+support` | 1 | Invalid/unknown serialization |
| `suicidal_ideation_or_hopelessness+support` | 1 | Invalid/unknown serialization |
| `non_mental_health+hate` | 1 | Invalid/unknown serialization |
| `mental_health_reference_Information` | 1 | Invalid/unknown spelling/casing |

### `context_flags`

| Value | Count | Policy status |
|---|---:|---|
| `first_person_or_self_report` | 10 | Approved |
| `mental_health_reference` | 21 | Invalid context vocabulary |
| `unrelated_or_neutral` | 25 | Invalid context vocabulary |
| `support_or_advice` | 4 | Invalid context vocabulary |

### Other fields

| Field | Values and counts |
|---|---|
| `annotator_confidence` | `High`: 23; `Low`: 37 |
| `needs_review` | `FALSE`: 56; `TRUE`: 4 |
| Blank values | None in the four inspected annotation fields |

## Does this appear to follow an older label scheme?

**Evidence-based conclusion:** the values appear to use a different or older
annotation vocabulary, but the exact originating scheme is not documented.

Evidence for this conclusion:

- The values `non_mental_health`, `mental_health_self_report`,
  `suicidal_ideation_or_hopelessness`, and `suicidal_self_report` are systematic
  category-like names but are not among the owner-approved labels.
- A2 additionally uses `+support` and `+hate` combinations, which do not use
  the approved pipe-delimited serialization.
- The project guidelines and proposal document only the current proposed core
  labels plus optional/context concepts; they do not define these observed
  legacy values or provide a mapping.
- The upstream/provenance reports found no local label dictionary, annotation
  code, or source documentation establishing the origin of these values.

Therefore, this is not proof of a particular older dataset or labeling system.
It is not safe to infer meanings from names alone, and `non_mental_health` must
not automatically be converted to `none_other`.

## Proposed mapping table — manual review required

These are hypotheses for an adjudicator's review queue only. **No mapping was
applied. Every row is `REQUIRES_MANUAL_REVIEW`.** The text and context must be
reviewed under the approved policy.

| Observed value | Possible approved label(s) to consider | Why automatic mapping is prohibited | Status |
|---|---|---|---|
| `non_mental_health` | `none_other` only if no substantive signal is present | Name does not prove absence of a signal; text may contain support or distress | `REQUIRES_MANUAL_REVIEW` |
| `mental_health_self_report` | `distress_negative_affect`; possibly `mental_health_reference_or_support` | Self-report may express different signals or multiple signals | `REQUIRES_MANUAL_REVIEW` |
| `suicidal_self_report` | `self_harm_related`; possibly `distress_negative_affect` or support | Explicit content and context must be checked; label is not equivalent by name | `REQUIRES_MANUAL_REVIEW` |
| `suicidal_ideation_or_hopelessness` | `self_harm_related`; possibly `distress_negative_affect` | The old compound category may not match the approved content boundary | `REQUIRES_MANUAL_REVIEW` |
| `Depression_or_hopelessness` | `distress_negative_affect`; possibly `mental_health_reference_or_support` | A diagnostic term does not establish a signal or personal condition | `REQUIRES_MANUAL_REVIEW` |
| `mental_health_advice` | `mental_health_reference_or_support` | Advice may be educational, quoted, or unrelated to a clear support signal | `REQUIRES_MANUAL_REVIEW` |
| `mental_health_reference_Information` | `mental_health_reference_or_support` | Spelling/casing resembles the approved label but still requires text/context verification | `REQUIRES_MANUAL_REVIEW` |
| `non-mental_health_or_support` | `none_other` or `mental_health_reference_or_support` | Compound meaning is ambiguous and contradicts automatic exclusivity rules | `REQUIRES_MANUAL_REVIEW` |
| `non_mental_health+support` | `none_other` or `mental_health_reference_or_support` | `+` is not approved serialization and the two concepts may conflict | `REQUIRES_MANUAL_REVIEW` |
| `suicidal_ideation_or_hopelessness+support` | `self_harm_related` plus possibly `mental_health_reference_or_support` or distress | Exact text/context and approved pipe serialization must be reviewed | `REQUIRES_MANUAL_REVIEW` |
| `non_mental_health+hate` | Usually no core label, possibly `none_other` | Hate is not an approved core signal and absence of a core signal must be confirmed | `REQUIRES_MANUAL_REVIEW` |

## Recommended manual next steps

1. Freeze the original A1/A2 files as read-only evidence.
2. Manually compare and document the two truncated A2 texts against the seed source. Do not silently repair them.
3. Have an adjudicator review all 60 queue rows, starting with invalid labels/context flags and the two text mismatches.
4. For each row, assign an approved label set only from the post text and context, not from the observed legacy value. Preserve the original values and record the reason for any decision.
5. Replace invalid context vocabulary only through explicit manual review; do not treat values such as `mental_health_reference` as approved flags automatically.
6. Recompute agreement only after the annotation schema is corrected by human adjudication and the original A1/A2 values remain preserved.
7. Do not train a model, create splits, or treat the legacy labels as ground truth until this repair/adjudication process and leakage policy are complete.

