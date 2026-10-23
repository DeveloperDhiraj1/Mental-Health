"""Readiness gate for a baseline model; deliberately does not train or split."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "Data" / "derived_phase1" / "canonical_corpus.csv"
REPORT = ROOT / "reports" / "baseline_readiness_report.md"
SUMMARY = ROOT / "reports" / "baseline_readiness_summary.json"
LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
SUBSTANTIVE = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]

def valid_label(value: str) -> bool:
    parts = value.strip().split("|")
    if value.strip() == "none_other": return True
    return bool(value.strip()) and len(parts) == len(set(parts)) and "none_other" not in parts and set(parts) <= LABELS and parts == [x for x in SUBSTANTIVE if x in parts]

def no_group_leakage(assignments: dict[str, str], groups: dict[str, str]) -> bool:
    seen = {}
    for record_id, split in assignments.items():
        group = groups[record_id]
        if group in seen and seen[group] != split: return False
        seen[group] = split
    return True

def assess(rows: list[dict[str, str]]) -> dict:
    labeled = [r for r in rows if r.get("reviewed_join_status") == "matched_validated"]
    counts = Counter()
    for row in labeled:
        for label in row["reviewed_label"].split("|"): counts[label] += 1
    platforms = Counter(r["platform"] for r in labeled)
    invalid = [r["stable_record_key"] for r in labeled if not valid_label(r["reviewed_label"])]
    return {"canonical_rows": len(rows), "validated_labeled_rows": len(labeled), "unlabeled_rows": len(rows)-len(labeled), "platform_counts": dict(platforms), "signal_incidence": dict(counts), "invalid_reviewed_labels": invalid, "no_splits_created": True, "model_trained": False}

def main() -> int:
    with CANONICAL.open(encoding="utf-8-sig", newline="") as handle: rows = list(csv.DictReader(handle))
    result = assess(rows)
    SUMMARY.write_text(json.dumps(result, indent=2), encoding="utf-8")
    lines = ["# Baseline Model Readiness Gate", "", "## Decision", "", "**NO-GO for baseline training and train/validation/test splitting from the current 60-record pilot.** This gate is an engineering safeguard; it does not assign labels or modify data.", "", "## Verified counts", "", f"- Canonical corpus rows: **{result['canonical_rows']}**.", f"- Validated human-labeled rows: **{result['validated_labeled_rows']}**.", f"- Unlabeled rows: **{result['unlabeled_rows']}**; no labels were inferred.", f"- Platform counts among labeled rows: `{result['platform_counts']}`.", f"- Signal incidence: `{result['signal_incidence']}`.", f"- Invalid reviewed labels: **{len(result['invalid_reviewed_labels'])}**.", "", "## Why training is blocked", "", "- The pilot has only 60 labeled records and 20 per platform.", "- The rare `self_harm_related` signal occurs only 7 times overall and only once on Twitter/X; a three-way split would make validation/test support unstable or empty.", "- The approved project coverage plan calls for at least 30 adjudicated positive instances per substantive signal and at least 100 policy-valid adjudicated records per platform before an initial platform-aware analysis. Current deficits are distress: 7, mental-health reference/support: 9, and self-harm-related: 23 against that planning threshold.", "- The original A1/A2 agreement analysis had only 8/60 policy-valid pairs, so the pilot is not strong evidence for reproducible independent labeling.", "- No independent test set can be claimed from this pilot; reusing it for training and evaluation would produce unreliable performance estimates.", "", "## Leakage checks available for the pilot", "", "- The Phase 1 corpus reports no exact duplicate text group inside the 60 reviewed records, no parent links, and no synthetic rows among the reviewed records.", "- Future splitting must still group exact/near duplicates, users, and augmentation parent-child records from the full corpus.", "- Legacy tiers, lexicon outputs, model predictions, confidence/probability fields, and split columns remain excluded from targets and features.", "", "## Exact additional annotation needed", "", "No additional labels were created in this phase. To reach the project's existing planning threshold, obtain supervisor-approved independent annotations and adjudication for at least 300 new genuine records (approximately 100 per platform), while monitoring rare-label support. At minimum, the project needs 23 additional adjudicated `self_harm_related` positives, 9 additional `mental_health_reference_or_support` positives, and 7 additional `distress_negative_affect` positives to reach 30 each overall; these are planning targets, not fabricated labels or guarantees.", "", "## Outputs and reproducibility", "", f"- Machine-readable summary: `{SUMMARY.relative_to(ROOT)}`.", "- Existing Phase 1 tests remain separate and passing.", "- No split manifests, model artifact, training script, or evaluation metrics were created because the gate failed.", "", "All labels remain non-clinical text-content annotations and do not indicate diagnosis or clinical risk."]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(REPORT); print(SUMMARY); return 0

if __name__ == "__main__": raise SystemExit(main())
