"""Create the approved, unlabeled 60-post pilot annotation sample.

The sampler uses only platform, record ID, text, and the source synthetic flag
for eligibility. It never reads tier, prediction, probability, confidence, or
other model-related fields to select or label records.

Run from the project root:
    python src/create_pilot_sample.py
"""

from __future__ import annotations

import csv
import hashlib
import random
import re
import unicodedata
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "Data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "Data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "pilot_annotation.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "pilot_sampling_report.md"
SEED = 20261019
TARGET_PER_PLATFORM = 20

INPUTS = (
    ("youtube", "youtube_data set.csv", "cp1252"),
    ("reddit", "reddit_dataSet.csv", "utf-8-sig"),
    ("twitter", "twitter_data set.csv", "utf-8-sig"),
)

OUTPUT_COLUMNS = (
    "record_id",
    "platform",
    "post_text",
    "annotator1_label",
    "annotator1_confidence",
    "annotator1_needs_review",
    "annotator1_review_reason",
    "annotator2_label",
    "annotator2_confidence",
    "annotator2_needs_review",
    "annotator2_review_reason",
    "context_flags",
)


def is_truthy(value: str) -> bool:
    return value.strip().casefold() in {"true", "1", "yes", "y"}


def normalized_hash(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"\s+", " ", normalized).strip().casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def read_source(platform: str, filename: str, encoding: str) -> list[dict[str, str]]:
    path = RAW_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing required dataset: {path}")
    rows: list[dict[str, str]] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        required = {"record_id", "platform", "post_text", "is_synthetic"}
        if not reader.fieldnames:
            raise ValueError(f"Dataset has no header: {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
        try:
            for line_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f"Malformed row in {path} at CSV line {line_number}")
                record_id = (row.get("record_id") or "").strip()
                if not record_id:
                    raise ValueError(f"Missing record_id in {path} at CSV line {line_number}")
                rows.append(
                    {
                        "record_id": record_id,
                        "platform": (row.get("platform") or "").strip() or platform,
                        "post_text": row.get("post_text") or "",
                        "is_synthetic": row.get("is_synthetic") or "",
                        "text_hash": normalized_hash(row.get("post_text") or ""),
                    }
                )
        except csv.Error as exc:
            raise ValueError(f"Malformed CSV in {path} near line {reader.line_num}: {exc}") from exc
    return rows


def choose_sample(rows: list[dict[str, str]], platform: str, rng: random.Random) -> list[dict[str, str]]:
    eligible = [row for row in rows if not is_truthy(row["is_synthetic"])]
    if len(eligible) < TARGET_PER_PLATFORM:
        raise ValueError(
            f"Only {len(eligible)} original/unspecified rows available for {platform}; "
            f"{TARGET_PER_PLATFORM} required"
        )
    return rng.sample(eligible, TARGET_PER_PLATFORM)


def write_report(
    selected: list[dict[str, str]],
    all_rows: dict[str, list[dict[str, str]]],
    excluded_synthetic: dict[str, int],
) -> None:
    hash_to_records: dict[str, list[tuple[str, str]]] = {}
    for platform, rows in all_rows.items():
        for row in rows:
            hash_to_records.setdefault(row["text_hash"], []).append((platform, row["record_id"]))

    selected_hashes = {row["text_hash"] for row in selected}
    selected_linked: dict[str, list[tuple[str, str]]] = {}
    for text_hash in sorted(selected_hashes):
        records = hash_to_records[text_hash]
        if len(records) > 1:
            selected_linked[text_hash] = records

    cross_platform_selected = {
        text_hash: records
        for text_hash, records in selected_linked.items()
        if len({platform for platform, _ in records}) > 1
    }

    lines = [
        "# Pilot Sampling Report",
        "",
        "## Status",
        "",
        "The project owner approved the proposed four-label pilot policy before "
        "sampling. This report documents a reproducible, unlabeled sample only. "
        "The labels describe non-clinical linguistic signals, not diagnoses or "
        "clinical severity.",
        "",
        "Raw CSVs, existing annotations, and split assignments were not modified. "
        "No labels were assigned.",
        "",
        "## Sampling method",
        "",
        f"- Random seed: **{SEED}** using Python `random.Random`.",
        "- Sampling unit: one source row, sampled independently within each platform.",
        "- Eligibility: source `is_synthetic` is blank/false; no tier, keyword, prediction, probability, or model field was used.",
        "- Target: 20 YouTube + 20 Reddit + 20 X/Twitter = 60 rows.",
        "- Sampling was performed from the raw rows after eligibility filtering; source order was not used as a selection criterion.",
        "",
        "## Output",
        "",
        f"- File: `{OUTPUT_FILE.relative_to(PROJECT_ROOT)}`",
        f"- Exact rows: **{len(selected)}**",
        "- Annotation fields are blank for both annotators.",
        "- Context flags are blank for human entry and are separate from signal labels.",
        "",
        "| Platform | Source rows | Eligible original/unspecified | Synthetic excluded | Selected |\n"
        "|---|---:|---:|---:|---:|",
    ]
    for platform, _, _ in INPUTS:
        source_count = len(all_rows[platform])
        excluded = excluded_synthetic[platform]
        eligible = source_count - excluded
        selected_count = sum(1 for row in selected if row["platform"] == platform)
        lines.append(f"| {platform} | {source_count} | {eligible} | {excluded} | {selected_count} |")

    lines.extend(
        [
            "",
            "## Synthetic-row handling",
            "",
            "Explicitly synthetic/augmented rows were excluded from the primary "
            "pilot. This includes the 125 marked YouTube synthetic rows documented "
            "in the data-quality reports. No synthetic row was silently deleted "
            "from the raw data; it was only ineligible for this pilot sample.",
            "",
            "## Duplicate and shared-hash handling",
            "",
            "Text hashes use Unicode NFKC normalization, collapsed whitespace, "
            "trimming, casefolding, and truncated SHA-256. Raw post text is not "
            "printed in this report.",
            f"- Selected records belonging to any within-file or cross-platform duplicate hash group: {sum(len(records) for records in selected_linked.values())} source records across {len(selected_linked)} hash groups.",
            f"- Selected records in cross-platform duplicate hash groups: {sum(len(records) for records in cross_platform_selected.values())} source records across {len(cross_platform_selected)} hash groups.",
            "- Linked records were not removed from the pilot; their hashes are flagged here so they must be kept together or excluded as a group from any later evaluation partition.",
            "",
            "Selected duplicate-group hashes (privacy-preserving):",
            "",
        ]
    )
    if selected_linked:
        for text_hash, records in selected_linked.items():
            platforms = ", ".join(sorted({platform for platform, _ in records}))
            lines.append(f"- `{text_hash}` — {len(records)} source records; platforms: {platforms}")
    else:
        lines.append("- None selected.")

    lines.extend(
        [
            "",
            "## Annotation instructions",
            "",
            "Two annotators must independently fill the label, confidence, review, "
            "and context fields. They must remain blind to legacy tier/model "
            "metadata. Use only the approved four-label policy; do not treat any "
            "label as a diagnosis or severity level.",
            "",
            "## Limitations",
            "",
            "This is a fixed-size pilot, not a representative estimate of platform "
            "prevalence. It does not resolve legacy tier provenance, establish a "
            "leakage-safe train/test split, or validate the proposed labels. The "
            "sample must be reviewed for annotation agreement before any larger "
            "annotation or modeling decision.",
        ]
    )
    REPORT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rng = random.Random(SEED)
    all_rows: dict[str, list[dict[str, str]]] = {}
    excluded_synthetic: dict[str, int] = {}
    selected: list[dict[str, str]] = []

    for platform, filename, encoding in INPUTS:
        rows = read_source(platform, filename, encoding)
        all_rows[platform] = rows
        excluded_synthetic[platform] = sum(is_truthy(row["is_synthetic"]) for row in rows)
        selected.extend(choose_sample(rows, platform, rng))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in selected:
            writer.writerow(
                {
                    "record_id": row["record_id"],
                    "platform": row["platform"],
                    "post_text": row["post_text"],
                    "annotator1_label": "",
                    "annotator1_confidence": "",
                    "annotator1_needs_review": "",
                    "annotator1_review_reason": "",
                    "annotator2_label": "",
                    "annotator2_confidence": "",
                    "annotator2_needs_review": "",
                    "annotator2_review_reason": "",
                    "context_flags": "",
                }
            )

    write_report(selected, all_rows, excluded_synthetic)
    print(f"Created {OUTPUT_FILE} with {len(selected)} unlabeled rows.")
    print(f"Created {REPORT_FILE}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
