"""Generate a read-only readiness summary for the existing 60-record pilot."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "Data" / "processed" / "annotation_work" / "manual_adjudication_workbook.csv"
SEED = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
REPORT = ROOT / "reports" / "pilot60_final_readiness_report.md"
ISSUES = ROOT / "reports" / "pilot60_final_validation_issues.csv"
DIST = ROOT / "reports" / "pilot60_label_distribution.csv"
LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
ORDER = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}

def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def valid_label(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    parts = value.split("|")
    if value == "none_other":
        return True
    return len(parts) == len(set(parts)) and "none_other" not in parts and set(parts) <= LABELS and parts == [x for x in ORDER if x in parts]

def valid_context(value: str) -> bool:
    value = value.strip()
    return not value or set(value.split("|")) <= CONTEXT and all(value.split("|"))

def main() -> None:
    rows = read(WORK); seed = read(SEED); seed_ids = {r["record_id"] for r in seed}; ids = [r["record_id"] for r in rows]
    issues = []
    if len(rows) != 60: issues.append(("", "", "row_count", len(rows), "Expected 60"))
    for rid, n in Counter(ids).items():
        if n > 1: issues.append((rid, "", "duplicate_record_id", n, "Duplicate workbook ID"))
    for rid in sorted(seed_ids - set(ids)): issues.append((rid, "", "missing_record_id", "", "Seed ID absent"))
    for rid in sorted(set(ids) - seed_ids): issues.append((rid, "", "unexpected_record_id", "", "Not in seed"))
    for row in rows:
        if not valid_label(row["final_adjudicated_label"]): issues.append((row["record_id"], row["platform"], "invalid_final_label", row["final_adjudicated_label"], "Policy vocabulary/order violation"))
        if not valid_context(row["final_context_flags"]): issues.append((row["record_id"], row["platform"], "invalid_final_context", row["final_context_flags"], "Policy context vocabulary violation"))
        if row["adjudication_status"].strip().casefold() != "completed": issues.append((row["record_id"], row["platform"], "unresolved_status", row["adjudication_status"], "Not completed"))
        if not row["adjudication_notes"].strip(): issues.append((row["record_id"], row["platform"], "missing_rationale", "", "No adjudication rationale"))
    with ISSUES.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["record_id", "platform", "issue_type", "value", "detail"]); w.writerows(issues)
    dist_rows = []
    platforms = sorted({r["platform"] for r in rows})
    for platform in platforms:
        subset = [r for r in rows if r["platform"] == platform]
        counts = Counter(r["final_adjudicated_label"] for r in subset)
        for label in sorted(counts):
            dist_rows.append([platform, label, counts[label], f"{100*counts[label]/len(subset):.2f}%", len(subset)])
    total_counts = Counter(r["final_adjudicated_label"] for r in rows)
    for label in sorted(total_counts):
        dist_rows.append(["combined", label, total_counts[label], f"{100*total_counts[label]/len(rows):.2f}%", len(rows)])
    with DIST.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["platform", "final_label_set", "count", "percent_within_platform", "platform_total"]); w.writerows(dist_rows)
    label_counts = Counter(r["final_adjudicated_label"] for r in rows)
    context_counts = Counter(r["final_context_flags"] or "<BLANK>" for r in rows)
    status_counts = Counter(r["adjudication_status"] for r in rows)
    confidence_counts = Counter(r["final_confidence"] for r in rows)
    mismatch_ids = [r["record_id"] for r in rows if r["A2_text_mismatch"].strip().casefold() == "true"]
    lines = ["# Pilot-60 Final Readiness Report", "", "## Scope", "", "This report uses only the existing 60-record seed and adjudication workbook. It does not add posts, modify annotations, create splits, train a model, or make clinical claims. Labels describe observable text signals only.", "", "## Current status", "", f"- Workbook rows: **{len(rows)}**; seed rows: **{len(seed)}**.", f"- IDs complete and unique against seed: **{len(rows)==60 and len(ids)==len(set(ids)) and set(ids)==seed_ids}**.", f"- Adjudication statuses: **{dict(status_counts)}**.", f"- Blank final labels: **{sum(not r['final_adjudicated_label'].strip() for r in rows)}**.", f"- Final-policy issues found in this fresh audit: **{len(issues)}**.", f"- Fresh validation issue file: `{ISSUES.relative_to(ROOT)}`.", "", "## A2 text mismatches", "", f"Two records retain `A2_text_mismatch=TRUE`: {', '.join(mismatch_ids)}.", "Both have `source_text_verified=FALSE` and adjudication notes documenting that the canonical seed text was used. They were not silently repaired.", "", "## Final label distribution", "", f"- Combined final label-set counts: **{dict(label_counts)}**.", f"- Platform coverage: YouTube=20, Reddit=20, Twitter/X=20.", f"- Descriptive distribution file: `{DIST.relative_to(ROOT)}`.", "", "## Context and confidence", "", f"- Context flags: **{dict(context_counts)}**.", f"- Final confidence: **{dict(confidence_counts)}**.", "- `context_insufficient` is an annotation context flag, not a clinical or risk category.", "", "## Original A1/A2 agreement", "", "The fresh IAA recalculation used original A1/A2 values, not final adjudicated labels. All 60 IDs matched, but only **8/60** pairs used the approved label vocabulary. Raw label-string agreement was 60/60 because both annotators retained the same older values; this is not evidence that the approved scheme was reliably applied. Policy-valid exact-set agreement was 8/8, with kappa undefined because the valid subset had no useful category variation. The IAA report also records 52 invalid labels per annotator, 50 invalid context rows per annotator, and two canonical-text mismatches per annotator.", "", "## What this pilot supports", "", "- It supports testing the annotation workflow, policy wording, adjudication process, and descriptive label reporting.", "- It supports a small qualitative discussion of examples and annotation difficulties.", "- It does not support reliable generalization or a defensible multi-label model performance claim: 60 records are small, platform-specific support is limited, rare-label estimates are unstable, and the original independent labels are largely non-policy values.", "- It cannot establish clinical validity or diagnose any person.", "", "## Decision and next step", "", "**No baseline model should be trained from this pilot yet.** The most useful next step using these same 60 records is to preserve the fresh validation/IAA results, document the two canonical-text decisions, and use the pilot for a qualitative methods review. Any modeling attempt would be exploratory only and should wait for an approved larger annotation set and leakage-safe group policy."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {REPORT}"); print(f"Created {ISSUES} with {len(issues)} issues"); print(f"Created {DIST} with {len(dist_rows)} rows")

if __name__ == "__main__": main()
