# Manual Adjudication Workbook Instructions

## Purpose

`Data/processed/annotation_work/manual_adjudication_workbook.csv` is a blank
adjudication workbook for the 60-post seed-42 pilot. The seed sample supplies
the canonical `record_id`, `platform`, and `post_text`. A1 and A2 values are
preserved exactly as received and must not be silently repaired.

These labels describe observable non-clinical text signals. They are not
diagnoses, clinical severity scores, or conclusions about an author's personal
condition.

## Review procedure

1. Work one row at a time using the canonical seed `post_text`.
2. Read the preserved A1/A2 labels, context flags, confidence, review flags,
   and reasons as evidence of what each annotator entered—not as ground truth.
3. Decide the final label only from the text and the approved policy.
4. Use only `none_other`, `distress_negative_affect`,
   `mental_health_reference_or_support`, and `self_harm_related`.
5. `none_other` must stand alone. The other three may co-occur.
6. For multiple substantive labels, use this order and delimiter with no spaces:
   `distress_negative_affect|mental_health_reference_or_support|self_harm_related`
7. Enter context flags separately in `final_context_flags`; never put context
   flags in the final label field.
8. For ambiguity, sarcasm, quotation, educational/fictional content, or missing
   context, use the policy's review procedure and explain the decision in
   `adjudication_notes`.
9. Do not use legacy tiers, predictions, probabilities, confidence metadata,
   keywords, or undocumented model fields to decide a final label.
10. Do not change `record_id`, `platform`, `post_text`, A1/A2 columns, or the
    mechanical issue fields.

## Adjudicator fields

Fill only `final_adjudicated_label`, `final_context_flags`,
`final_confidence`, `adjudication_status`, and `adjudication_notes`. Leave the
mechanical source and annotator evidence intact. Review every row marked with a
non-empty `review_reason_category`, especially `source_text_mismatch` and
`multiple_issues`.

Keep the workbook local and use no real personal identifiers. Preserve the
original A1 and A2 files separately. Do not train a model or change splits
during adjudication.
