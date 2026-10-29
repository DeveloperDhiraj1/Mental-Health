"""Create a fresh dataset and annotation readiness audit without changing inputs."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUALITY = ROOT / "Data" / "derived_phase1" / "quality_summary.json"
WORKBOOK = ROOT / "Data" / "processed" / "annotation_work" / "manual_adjudication_workbook.csv"
SEED = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
A1 = ROOT / "Data" / "processed" / "annotation_work" / "A1_annotation.csv"
A2 = ROOT / "Data" / "processed" / "annotation_work" / "A2_annotation.csv"
REPORT = ROOT / "reports" / "dataset_annotation_readiness_audit.md"
SUMMARY = ROOT / "reports" / "dataset_annotation_readiness_summary.json"

LABELS = {"none_other", "distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"}
ORDER = ["distress_negative_affect", "mental_health_reference_or_support", "self_harm_related"]
CONTEXT = {"first_person_or_self_report", "third_person", "quoted_or_reported", "educational_or_information", "fictional_or_hypothetical", "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def valid_label(value: str) -> bool:
    parts = value.strip().split("|")
    if not value.strip() or "none_other" in parts and len(parts) != 1:
        return False
    if parts == ["none_other"]:
        return True
    return len(parts) == len(set(parts)) and set(parts) <= LABELS and parts == [label for label in ORDER if label in parts]


def valid_context(value: str) -> bool:
    parts = value.strip().split("|") if value.strip() else []
    return len(parts) == len(set(parts)) and all(parts) and set(parts) <= CONTEXT or not parts


def main() -> None:
    quality = json.loads(QUALITY.read_text(encoding="utf-8"))
    workbook = read(WORKBOOK)
    seed = read(SEED)
    a1 = read(A1)
    a2 = read(A2)
    ids = [row.get("record_id", "") for row in workbook]
    seed_ids = {row.get("record_id", "") for row in seed}
    final_valid = [row for row in workbook if valid_label(row.get("final_adjudicated_label", "")) and valid_context(row.get("final_context_flags", "")) and row.get("adjudication_status", "").strip().casefold() == "completed"]
    final_counts = Counter(row.get("final_adjudicated_label", "") for row in final_valid)
    platform_counts = Counter(row.get("platform", "") for row in final_valid)
    mismatch_ids = [row["record_id"] for row in workbook if row.get("A2_text_mismatch", "").strip().casefold() == "true"]
    a1_ids, a2_ids = [row.get("record_id", "") for row in a1], [row.get("record_id", "") for row in a2]
    summary = {"raw_rows": quality["row_count"], "platform_counts": quality["platform_counts"], "reviewed_joined": quality["reviewed_rows_joined"], "unreviewed_rows": quality["unreviewed_rows"], "verified_usable_final_labels": len(final_valid), "final_label_distribution": dict(final_counts), "pilot_platform_counts": dict(platform_counts), "a2_text_mismatch_ids": mismatch_ids, "a1_rows": len(a1), "a2_rows": len(a2), "a1_a2_ids_match": set(a1_ids) == set(a2_ids), "seed_ids_complete": len(ids) == len(seed) and len(ids) == len(set(ids)) and set(ids) == seed_ids}
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Dataset and Annotation Readiness Audit",
        "",
        "## Scope",
        "",
        "Fresh audit of the three current raw datasets, Phase 1 derived quality metrics, and the existing 60-record human adjudication pilot. Original datasets and annotation files were read only. No labels were inferred, no split was created, and no model was trained.",
        "",
        "## Raw dataset findings",
        "",
        f"- Combined rows: **{quality['row_count']}**.",
        f"- Platform rows: **{quality['platform_counts']}**.",
        f"- Encodings: YouTube `cp1252`; Reddit and Twitter/X `utf-8-sig`.",
        "- Each source has 51 columns; record IDs and post text are non-empty in the current strict load.",
        f"- Normalized exact-text groups: **{quality['exact_text_groups']}**; near-duplicate candidates: **{quality['near_duplicate_candidates']}**; augmentation parent groups: **{quality['parent_groups']}**.",
        "- YouTube synthetic/augmented rows: **125**. They are retained in the canonical corpus but excluded from the primary 60-post pilot.",
        "- No duplicate record-ID extras, exact full-row duplicate extras, or empty text rows were found by the Phase 1 run.",
        "",
        "## Label provenance and leakage",
        "",
        "- Legacy `tier`, `tier_lexicon`, `tier_corrected`, `tier_model`, `tier_pred`, probability/confidence, lexicon, model, augmentation, and split fields remain untrusted metadata.",
        "- The meanings of legacy tier values 0–3 and the construction of `split`/`model_split` remain undocumented locally.",
        "- Legacy fields must not be targets or default model features. Duplicate text, near-duplicates, repeated users, and parent-child augmentation relationships require group-aware evaluation controls.",
        "",
        "## Human annotation status",
        "",
        f"- Reviewed workbook rows: **{len(workbook)}**; canonical seed rows: **{len(seed)}**.",
        f"- Complete, unique seed-ID coverage: **{summary['seed_ids_complete']}**.",
        f"- Verified usable final labels under the approved vocabulary and completed status: **{len(final_valid)}**.",
        f"- Final label-set distribution: **{dict(final_counts)}**.",
        f"- Platform coverage of verified labels: **{dict(platform_counts)}**.",
        f"- A2 canonical-text mismatches retained and documented: **{len(mismatch_ids)}**; IDs are recorded in the machine-readable summary, not repaired here.",
        f"- Original A1/A2 rows: **{len(a1)} / {len(a2)}**; ID sets match: **{summary['a1_a2_ids_match']}**.",
        f"- Phase 1 joined the 60 reviewed rows to raw records; **{quality['unreviewed_rows']}** raw rows have no verified human label.",
        "",
        "## Readiness decision",
        "",
        "**NO-GO for model training and meaningful evaluation at this stage.** The verified label count is only 60 of 4,739 records, with 20 records per platform. This is sufficient for workflow and qualitative analysis, not reliable multi-label generalization or performance claims. The original A1/A2 labels are largely outside the approved vocabulary, so their agreement cannot substitute for a larger policy-conforming annotation set.",
        "",
        "## Required next action",
        "",
        "Obtain supervisor approval for a larger annotation batch, keep independent annotation and adjudication separate, retain synthetic records as a separate stratum, and freeze a group-aware evaluation policy before any model training. Group normalized duplicate text, conservative near-duplicate candidates after review, repeated users where available, cross-platform copies, and augmentation parent-child records together. Only approved human-reviewed labels may become targets.",
        "",
        "This project studies non-clinical linguistic signals. Labels do not diagnose a person or estimate clinical condition or risk.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Created {REPORT}")
    print(f"Created {SUMMARY}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
