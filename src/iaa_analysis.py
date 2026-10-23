"""Read-only inter-annotator agreement analysis for the seed-42 pilot."""
from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "Data" / "processed" / "annotation_work"
SEED = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
A1 = WORK / "A1_annotation.csv"
A2 = WORK / "A2_annotation.csv"
REPORT = ROOT / "reports" / "inter_annotator_agreement_report.md"
METRICS = ROOT / "reports" / "inter_annotator_agreement_metrics.csv"
LABELS = ["none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
SUBSTANTIVE = LABELS[1:]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}

def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def labels(value: str) -> tuple[set[str] | None, str | None]:
    value = value.strip()
    if not value: return None, "missing"
    parts = value.split("|")
    if any(not x or x != x.strip() for x in parts): return None, "malformed_spacing"
    if len(parts) != len(set(parts)): return None, "duplicate_label"
    if "none_other" in parts and len(parts) != 1: return None, "none_other_combined"
    if any(x not in LABELS for x in parts): return None, "unknown_label"
    expected = [x for x in SUBSTANTIVE if x in parts]
    if parts != ["none_other"] and parts != expected: return None, "wrong_order"
    return set(parts), None

def context(value: str) -> tuple[set[str] | None, str | None]:
    value = value.strip()
    if not value: return set(), None
    parts = value.split("|")
    if any(not x or x != x.strip() for x in parts): return None, "malformed_context"
    if len(parts) != len(set(parts)): return None, "duplicate_context"
    unknown = [x for x in parts if x not in CONTEXT]
    return (None, "unknown_context") if unknown else (set(parts), None)

def kappa(a: list[bool], b: list[bool]) -> float | None:
    n = len(a)
    if not n: return None
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if math.isclose(1 - pe, 0.0) else (po - pe) / (1 - pe)

def pct(n: int, d: int) -> str:
    return "N/A" if not d else f"{100*n/d:.2f}%"

def binary(a: list[bool], b: list[bool]) -> dict[str, object]:
    n = len(a); tp = sum(x and y for x, y in zip(a, b)); tn = sum((not x) and (not y) for x, y in zip(a, b)); fp = sum((not x) and y for x, y in zip(a, b)); fn = sum(x and (not y) for x, y in zip(a, b))
    pos_den = 2*tp + fp + fn; neg_den = 2*tn + fp + fn
    return {"n": n, "tp": tp, "tn": tn, "fp": fp, "fn": fn, "observed": (tp+tn)/n if n else None, "positive": 2*tp/pos_den if pos_den else None, "negative": 2*tn/neg_den if neg_den else None, "kappa": kappa(a,b)}

def main() -> None:
    seed = read(SEED); a1 = read(A1); a2 = read(A2)
    seed_by = {r["record_id"]: r for r in seed}; a1_by = {r["record_id"]: r for r in a1}; a2_by = {r["record_id"]: r for r in a2}
    issues = Counter(); invalid_values = Counter(); context_invalid_values = Counter(); rows = []
    for rid in sorted(set(seed_by) | set(a1_by) | set(a2_by)):
        s, x, y = seed_by.get(rid), a1_by.get(rid), a2_by.get(rid)
        if s is None: issues["unexpected_id"] += 1
        if x is None: issues["missing_in_a1"] += 1
        if y is None: issues["missing_in_a2"] += 1
        if not x or not y or not s: continue
        if x["platform"] != y["platform"]: issues["platform_mismatch_a1_a2"] += 1
        if x["platform"] != s["platform"]: issues["platform_mismatch_a1_seed"] += 1
        if y["platform"] != s["platform"]: issues["platform_mismatch_a2_seed"] += 1
        if x["post_text"] != s["post_text"]: issues["a1_seed_text_mismatch"] += 1
        if y["post_text"] != s["post_text"]: issues["a2_seed_text_mismatch"] += 1
        if x["post_text"] != y["post_text"]: issues["a1_a2_text_mismatch"] += 1
        la, ea = labels(x["annotator_label"]); lb, eb = labels(y["annotator_label"])
        ca, eca = context(x["context_flags"]); cb, ecb = context(y["context_flags"])
        if ea: issues[f"A1_label_{ea}"] += 1; invalid_values[f"A1:{x['annotator_label'] or '<BLANK>'}"] += 1
        if eb: issues[f"A2_label_{eb}"] += 1; invalid_values[f"A2:{y['annotator_label'] or '<BLANK>'}"] += 1
        if eca: issues[f"A1_context_{eca}"] += 1; context_invalid_values[f"A1:{x['context_flags'] or '<BLANK>'}"] += 1
        if ecb: issues[f"A2_context_{ecb}"] += 1; context_invalid_values[f"A2:{y['context_flags'] or '<BLANK>'}"] += 1
        rows.append((rid, s["platform"], x, y, la, lb, ca, cb, ea, eb, eca, ecb))
    valid_label_rows = [r for r in rows if r[4] is not None and r[5] is not None]
    valid_context_rows = [r for r in rows if r[6] is not None and r[7] is not None]
    raw_equal = sum(r[2]["annotator_label"].strip() == r[3]["annotator_label"].strip() for r in rows)
    set_equal = sum(r[4] == r[5] for r in valid_label_rows)
    metrics = []
    def add_metric(scope, label, m, note=""):
        metrics.append({"scope": scope, "dimension": label, "valid_pairs": m["n"], "observed_agreement": "" if m["observed"] is None else f"{m['observed']:.6f}", "positive_agreement": "" if m["positive"] is None else f"{m['positive']:.6f}", "negative_agreement": "" if m["negative"] is None else f"{m['negative']:.6f}", "cohens_kappa": "" if m["kappa"] is None else f"{m['kappa']:.6f}", "note": note})
    for scope, subset in [("overall", valid_label_rows)] + [(p, [r for r in valid_label_rows if r[1] == p]) for p in sorted({r[1] for r in rows})]:
        for label in LABELS:
            add_metric(scope, label, binary([label in r[4] for r in subset], [label in r[5] for r in subset]), "Kappa undefined when expected variance is zero or no valid pairs.")
    for scope, subset in [("overall", valid_context_rows)] + [(p, [r for r in valid_context_rows if r[1] == p]) for p in sorted({r[1] for r in rows})]:
        for flag in sorted(CONTEXT):
            add_metric(scope, f"context:{flag}", binary([flag in r[6] for r in subset], [flag in r[7] for r in subset]), "Context flags analyzed separately; blank context is valid.")
    with METRICS.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics[0])); writer.writeheader(); writer.writerows(metrics)
    mismatch_ids = [r[0] for r in rows if r[3]["post_text"] != seed_by[r[0]]["post_text"]]
    platforms = Counter(r[1] for r in rows)
    label_summary = {label: binary([label in r[4] for r in valid_label_rows], [label in r[5] for r in valid_label_rows]) for label in LABELS}
    context_exact = sum(r[6] == r[7] for r in valid_context_rows)
    label_lines = [f"- `{label}`: observed={pct(round(m['observed']*100) if m['observed'] is not None else 0, 100) if m['observed'] is not None else 'N/A'}, positive={pct(round(m['positive']*100) if m['positive'] is not None else 0, 100) if m['positive'] is not None else 'N/A'}, negative={pct(round(m['negative']*100) if m['negative'] is not None else 0, 100) if m['negative'] is not None else 'N/A'}, kappa={'N/A' if m['kappa'] is None else f'{m["kappa"]:.4f}'}" for label, m in label_summary.items()]
    lines = ["# Inter-Annotator Agreement Analysis", "", "## Scope", "", "This analysis uses original A1/A2 annotations only. Final adjudicated labels are not used as replacements. No source or annotation file was modified; labels describe non-clinical text signals, not diagnoses.", "", "## Structural validation", "", f"- Seed rows: **{len(seed)}**; A1 rows: **{len(a1)}**; A2 rows: **{len(a2)}**.", f"- Expected IDs present exactly once in A1: **{len(a1)==60 and len(a1_by)==60 and set(a1_by)==set(seed_by)}**.", f"- Expected IDs present exactly once in A2: **{len(a2)==60 and len(a2_by)==60 and set(a2_by)==set(seed_by)}**.", f"- A1/A2 ID sets match: **{set(a1_by)==set(a2_by)}**.", f"- Platform counts: {dict(platforms)}.", f"- A1 text mismatches against canonical seed text: **{issues['a1_seed_text_mismatch']}**.", f"- A2 text mismatches against canonical seed text: **{len(mismatch_ids)}** ({', '.join(mismatch_ids) if mismatch_ids else 'none'}).", "", "## Original-label agreement", "", f"- Raw exact label-string agreement: **{raw_equal}/{len(rows)} ({pct(raw_equal, len(rows))})**. This is case/order-sensitive and includes invalid values.", f"- Valid policy-conforming paired labels: **{len(valid_label_rows)}/{len(rows)}**.", f"- Valid exact label-set agreement: **{set_equal}/{len(valid_label_rows)} ({pct(set_equal, len(valid_label_rows))})**.", "", "### Binary agreement on valid pairs", "", *label_lines, "", "For each binary label, observed agreement = (TP+TN)/N; positive agreement = 2TP/(2TP+FP+FN); negative agreement = 2TN/(2TN+FP+FN). Cohen's kappa is reported only when its denominator is defined; blank in the CSV means mathematically undefined, commonly because both annotators have zero variance for that label or no valid pairs.", "", "## Validation problems", "", f"- Invalid/missing label or context observations: {sum(v for k,v in issues.items() if 'label_' in k or 'context_' in k)} issue counts; see details below.", f"- Label/context issue summary: {dict(issues)}", f"- Distinct invalid label values: {dict(invalid_values)}", f"- Distinct invalid context values: {dict(context_invalid_values)}", "", "## Context flags", "", f"- Valid paired context rows: **{len(valid_context_rows)}/{len(rows)}**.", f"- Exact context-set agreement on valid context pairs: **{context_exact}/{len(valid_context_rows)} ({pct(context_exact, len(valid_context_rows))})**.", "- Context flags were analyzed independently from substantive labels; per-flag metrics are in the machine-readable file with `dimension` beginning `context:`.", "", "## Limitations and recommendation", "", "The approved policy is not satisfied by most original A1/A2 label values, so the valid policy-based denominator is small and cannot support a reliable overall kappa claim. Raw agreement is descriptive only. The two A1/A2 text mismatches should remain documented and should be resolved or excluded by explicit methodological decision before using this pilot for model development.", "", "**Recommendation: conduct further manual review/annotation repair, then rerun IAA. Do not train a model or create evaluation splits from this pilot yet.**"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {REPORT}"); print(f"Created {METRICS} with {len(metrics)} metric rows")

if __name__ == "__main__": main()
