# Human Review Checklist

Use this checklist for rows in `reports/annotation_quality_review.csv`. Do not edit A1/A2 source files.

1. Open the canonical seed text for the `record_id`; do not use legacy tiers or model fields.
2. Confirm the text source when `source_text_mismatch` is present; record the decision separately.
3. Check each original label against the four approved labels. Never map older values automatically.
4. Confirm `none_other` is alone; otherwise send the row to adjudication.
5. For multiple substantive labels, require exact `|` order: `distress_negative_affect|mental_health_reference_or_support|self_harm_related`.
6. Check context flags separately using only the approved policy vocabulary.
7. Decide whether a policy-valid disagreement is semantic, context-dependent, quoted, educational, fictional, sarcastic, or insufficient-context.
8. Preserve both original judgments and document the adjudicator decision in the existing adjudication workflow.
9. Use `needs_review=TRUE` for unresolved ambiguity; do not force a label.
10. Keep the work local and treat every label as an observable text signal, not a diagnosis or personal-risk conclusion.
