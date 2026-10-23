"""Compare independent A1/A2 pilot annotations without adjudicating them.

The script discovers the current A1/A2 CSVs, validates them against the
seed-42 source sample, preserves original annotation values, and writes a
comparison plus adjudication queue. Invalid values are reported and excluded
from valid-agreement metrics; they are never automatically corrected.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "Data" / "processed" / "annotation_work"
REPORT_DIR = ROOT / "reports"
SOURCE_CANDIDATES = list((ROOT / "Data" / "processed").glob("pilot_annotation_seed42*.csv"))
COMPARISON = WORK_DIR / "annotation_comparison.csv"
QUEUE = WORK_DIR / "adjudication_queue.csv"
REPORT = REPORT_DIR / "annotation_agreement_report.md"

WORK_COLUMNS = (
    "record_id", "platform", "post_text", "annotator_label",
    "annotator_confidence", "needs_review", "review_reason", "context_flags",
)
SIGNAL_LABELS = (
    "none_other",
    "distress_negative_affect",
    "mental_health_reference_or_support",
    "self_harm_related",
)
SUBSTANTIVE = set(SIGNAL_LABELS[1:])
CONTEXT_FLAGS = {
    "first_person_or_self_report", "third_person", "quoted_or_reported",
    "educational_or_information", "fictional_or_hypothetical",
    "sarcastic_or_ironic", "promotional_or_campaign", "context_insufficient",
}
CONFIDENCES = {"high", "medium", "low"}
BOOLS = {"true", "false"}

COMPARISON_COLUMNS = (
    "record_id", "platform", "post_text", "A1_labels", "A2_labels",
    "A1_confidence", "A2_confidence", "A1_needs_review", "A2_needs_review",
    "A1_review_reason", "A2_review_reason", "A1_context_flags", "A2_context_flags",
    "match_status", "disagreement_reason",
)
QUEUE_COLUMNS = (
    "record_id", "platform", "post_text", "A1_labels", "A2_labels",
    "A1_confidence", "A2_confidence", "A1_needs_review", "A2_needs_review",
    "A1_review_reason", "A2_review_reason", "A1_context_flags", "A2_context_flags",
    "disagreement_reason", "final_adjudicated_label", "adjudication_notes",
    "adjudication_status",
)


def discover_one(pattern: str, description: str) -> Path:
    candidates = sorted(WORK_DIR.glob(pattern))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one {description}; found: {candidates}")
    return candidates[0]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if tuple(reader.fieldnames or ()) != WORK_COLUMNS:
            raise RuntimeError(f"Schema mismatch in {path}: {reader.fieldnames}")
        try:
            rows = list(reader)
        except csv.Error as exc:
            raise RuntimeError(f"Malformed CSV in {path}: {exc}") from exc
    return rows


def read_source(path: Path) -> list[dict[str, str]]:
    expected = (
        "record_id", "platform", "post_text", "annotator1_label",
        "annotator1_confidence", "annotator1_needs_review", "annotator1_review_reason",
        "annotator2_label", "annotator2_confidence", "annotator2_needs_review",
        "annotator2_review_reason", "context_flags",
    )
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if tuple(reader.fieldnames or ()) != expected:
            raise RuntimeError(f"Seed-42 source schema mismatch: {reader.fieldnames}")
        return list(reader)


def parse_labels(value: str) -> tuple[set[str] | None, str | None]:
    value = value.strip()
    if not value:
        return None, "missing_label"
    parts = value.split("|")
    if any(not part or part != part.strip() for part in parts):
        return None, "invalid_label_spacing_or_empty_part"
    if len(set(parts)) != len(parts):
        return None, "duplicate_label"
    if any(part not in SIGNAL_LABELS for part in parts):
        return None, "unknown_label"
    if "none_other" in parts and len(parts) != 1:
        return None, "none_other_combined"
    expected_order = [label for label in SIGNAL_LABELS[1:] if label in parts]
    if parts != expected_order and parts != ["none_other"]:
        return None, "label_order_not_policy_order"
    return set(parts), None


def validate_aux(row: dict[str, str], prefix: str) -> list[str]:
    problems: list[str] = []
    confidence = row["annotator_confidence"].strip().casefold()
    if not confidence:
        problems.append(f"{prefix}_missing_confidence")
    elif confidence not in CONFIDENCES:
        problems.append(f"{prefix}_invalid_confidence")
    review = row["needs_review"].strip().casefold()
    if not review:
        problems.append(f"{prefix}_missing_needs_review")
    elif review not in BOOLS:
        problems.append(f"{prefix}_invalid_needs_review")
    contexts = row["context_flags"].strip()
    if contexts:
        flags = contexts.split("|")
        unknown = [flag for flag in flags if flag not in CONTEXT_FLAGS]
        if unknown:
            problems.append(f"{prefix}_invalid_context_flag")
    return problems


def kappa(values_a: list[bool], values_b: list[bool]) -> float | None:
    n = len(values_a)
    if not n:
        return None
    po = sum(a == b for a, b in zip(values_a, values_b)) / n
    pa = sum(values_a) / n
    pb = sum(values_b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    if math.isclose(1 - pe, 0.0):
        return None
    return (po - pe) / (1 - pe)


def percentage(value: int, total: int) -> str:
    return "N/A" if total == 0 else f"{100 * value / total:.2f}%"


def compare_rows(a1: list[dict[str, str]], a2: list[dict[str, str]], source: list[dict[str, str]]):
    source_by_id = {row["record_id"]: row for row in source}
    a2_by_id = {row["record_id"]: row for row in a2}
    comparison: list[dict[str, str]] = []
    queue: list[dict[str, str]] = []
    validation: Counter[str] = Counter()
    valid_pairs: list[tuple[set[str], set[str]]] = []
    platform_pairs: defaultdict[str, list[tuple[set[str], set[str]]]] = defaultdict(list)

    for a1row in a1:
        rid = a1row["record_id"]
        a2row = a2_by_id.get(rid)
        source_row = source_by_id.get(rid)
        if a2row is None:
            validation["missing_in_a2"] += 1
            continue
        if source_row is None:
            validation["missing_in_source"] += 1
        else:
            if a1row["platform"] != source_row["platform"]:
                validation["A1_source_platform_mismatch"] += 1
            if a2row["platform"] != source_row["platform"]:
                validation["A2_source_platform_mismatch"] += 1
            if a1row["post_text"] != source_row["post_text"]:
                validation["A1_source_post_text_mismatch"] += 1
            if a2row["post_text"] != source_row["post_text"]:
                validation["A2_source_post_text_mismatch"] += 1
        if a1row["platform"] != a2row["platform"]:
            validation["platform_mismatch"] += 1
        if a1row["post_text"] != a2row["post_text"]:
            validation["post_text_mismatch"] += 1
        a1set, a1err = parse_labels(a1row["annotator_label"])
        a2set, a2err = parse_labels(a2row["annotator_label"])
        reasons: list[str] = []
        if a1err:
            validation[f"A1_{a1err}"] += 1
            if a1err == "unknown_label":
                validation[f"A1_unknown_value:{a1row['annotator_label']}"] += 1
            reasons.append(f"A1:{a1err}")
        if a2err:
            validation[f"A2_{a2err}"] += 1
            if a2err == "unknown_label":
                validation[f"A2_unknown_value:{a2row['annotator_label']}"] += 1
            reasons.append(f"A2:{a2err}")
        aux_reasons = validate_aux(a1row, "A1") + validate_aux(a2row, "A2")
        for reason in aux_reasons:
            validation[reason] += 1
        reasons.extend(aux_reasons)
        if a1set is not None and a2set is not None:
            valid_pairs.append((a1set, a2set))
            platform_pairs[a1row["platform"]].append((a1set, a2set))
            status = "MATCH" if a1set == a2set else "DISAGREEMENT"
            if status == "DISAGREEMENT":
                reasons.append("label_set_mismatch")
        else:
            status = "INVALID_OR_MISSING"
        if a1row["needs_review"].strip().casefold() == "true" or a2row["needs_review"].strip().casefold() == "true":
            reasons.append("annotator_flagged_review")
        row = {
            "record_id": rid, "platform": a1row["platform"], "post_text": a1row["post_text"],
            "A1_labels": a1row["annotator_label"], "A2_labels": a2row["annotator_label"],
            "A1_confidence": a1row["annotator_confidence"], "A2_confidence": a2row["annotator_confidence"],
            "A1_needs_review": a1row["needs_review"], "A2_needs_review": a2row["needs_review"],
            "A1_review_reason": a1row["review_reason"], "A2_review_reason": a2row["review_reason"],
            "A1_context_flags": a1row["context_flags"], "A2_context_flags": a2row["context_flags"],
            "match_status": status, "disagreement_reason": ";".join(dict.fromkeys(reasons)),
        }
        comparison.append(row)
        if status != "MATCH" or reasons:
            queue.append({
                **{key: row[key] for key in QUEUE_COLUMNS if key in row},
                "disagreement_reason": row["disagreement_reason"],
                "final_adjudicated_label": "", "adjudication_notes": "", "adjudication_status": "",
            })
    return comparison, queue, validation, valid_pairs, platform_pairs


def metric_lines(pairs: list[tuple[set[str], set[str]]]) -> list[str]:
    lines = [
        f"- Valid paired annotations: {len(pairs)}",
        "- Label | Valid pairs | Agreement | Cohen's kappa",
        "- |---:|---:|---:|",
    ]
    for label in SIGNAL_LABELS:
        a = [label in x for x, _ in pairs]
        b = [label in y for _, y in pairs]
        agree = sum(x == y for x, y in zip(a, b))
        kap = kappa(a, b)
        kap_text = "N/A (zero expected variance)" if kap is None else f"{kap:.4f}"
        lines.append(f"- `{label}` | {len(pairs)} | {percentage(agree, len(pairs))} | {kap_text}")
    return lines


def write_report(a1_path: Path, a2_path: Path, source_path: Path, a1: list[dict[str, str]], a2: list[dict[str, str]], source: list[dict[str, str]], comparison: list[dict[str, str]], validation: Counter, pairs, platform_pairs) -> None:
    exact_valid = sum(row["match_status"] == "MATCH" for row in comparison)
    valid_disagreements = sum(row["match_status"] == "DISAGREEMENT" for row in comparison)
    raw_equal = sum(row["A1_labels"].strip() == row["A2_labels"].strip() for row in comparison)
    lines = [
        "# Annotation Agreement Report",
        "",
        "## Scope and safety",
        "",
        "This report compares A1 and A2 annotations only. It does not correct, "
        "merge, adjudicate, relabel, train a model, or change dataset splits.",
        "Annotations are treated as non-clinical text-signal judgments, not diagnoses.",
        "",
        "## Actual input files",
        "",
        f"- Seed source: `{source_path.relative_to(ROOT)}` ({len(source)} rows)",
        f"- A1: `{a1_path.relative_to(ROOT)}` ({len(a1)} rows)",
        f"- A2: `{a2_path.relative_to(ROOT)}` ({len(a2)} rows)",
        "- Policy: `reports/pilot_annotation_policy.md`",
        "",
        "## Structural validation",
        "",
        f"- A1 exactly 60 rows: **{'yes' if len(a1) == 60 else 'no'}**",
        f"- A2 exactly 60 rows: **{'yes' if len(a2) == 60 else 'no'}**",
        f"- Same record-ID set: **{'yes' if {x['record_id'] for x in a1} == {x['record_id'] for x in a2} else 'no'}**",
        f"- A1/A2 platform/text mismatches: {validation['platform_mismatch']} / {validation['post_text_mismatch']}.",
        f"- A1/source platform/text mismatches: {validation['A1_source_platform_mismatch']} / {validation['A1_source_post_text_mismatch']}.",
        f"- A2/source platform/text mismatches: {validation['A2_source_platform_mismatch']} / {validation['A2_source_post_text_mismatch']}.",
        "",
        "## Agreement summary",
        "",
        f"- Raw label-string equality: {raw_equal}/{len(comparison)} ({percentage(raw_equal, len(comparison))}).",
        f"- Valid exact label-set matches: {exact_valid}/{len(pairs)} ({percentage(exact_valid, len(pairs))}).",
        f"- Valid exact label-set disagreements: {valid_disagreements}/{len(pairs)}.",
        f"- Invalid or missing annotation rows: {len(comparison) - len(pairs)}.",
        "",
        "The valid exact-set metric compares labels as sets after splitting on `|`; label order does not create a disagreement. Invalid/missing labels are not counted as valid agreement.",
        "",
        "## Per-label metrics: overall",
        "",
    ]
    lines.extend(metric_lines(pairs))
    lines.extend(["", "## Per-platform metrics", ""])
    for platform in ("youtube", "reddit", "twitter"):
        lines.append(f"### {platform}")
        lines.extend(metric_lines(platform_pairs.get(platform, [])))
        lines.append("")
    lines.extend([
        "## Invalid and missing values",
        "",
        "The comparison preserves invalid values and does not infer replacements.",
    ])
    if validation:
        for key, count in sorted(validation.items()):
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("- None detected.")
    lines.extend([
        "",
        "## Limitations and manual next steps",
        "",
        "Cohen's kappa is calculated on valid paired annotations only. It can be unreliable or undefined with small samples, rare labels, class imbalance, or zero expected variance. Invalid/missing rows and review-flagged rows require manual inspection.",
        "",
        "Review `Data/processed/annotation_work/adjudication_queue.csv`. An adjudicator must preserve A1/A2 labels and manually enter the final label, notes, and status. Do not use legacy tier fields as ground truth. Do not train or split data until adjudication and the approved leakage policy are complete.",
    ])
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    a1_path = discover_one("A1*.csv", "A1 annotation file")
    a2_path = discover_one("A2*.csv", "A2 annotation file")
    if not SOURCE_CANDIDATES or len(SOURCE_CANDIDATES) != 1:
        raise RuntimeError(f"Expected one seed-42 source; found {SOURCE_CANDIDATES}")
    source_path = SOURCE_CANDIDATES[0]
    a1, a2, source = read_csv(a1_path), read_csv(a2_path), read_source(source_path)
    comparison, queue, validation, pairs, platform_pairs = compare_rows(a1, a2, source)
    if len(a1) != 60 or len(a2) != 60 or len(source) != 60:
        raise RuntimeError("Required 60-row validation failed")
    if {r["record_id"] for r in a1} != {r["record_id"] for r in a2}:
        raise RuntimeError("A1/A2 record-ID set mismatch; comparison outputs not written")
    with COMPARISON.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARISON_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(comparison)
    with QUEUE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUEUE_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(queue)
    write_report(a1_path, a2_path, source_path, a1, a2, source, comparison, validation, pairs, platform_pairs)
    print(f"Created {COMPARISON}")
    print(f"Created {QUEUE}")
    print(f"Created {REPORT}")


if __name__ == "__main__":
    main()
