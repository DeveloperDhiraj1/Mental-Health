"""Create the approved seed-42 pilot sample without touching prior artifacts.

This script reads only the platform, record_id, post_text, and is_synthetic
fields needed for eligibility/output plus the complete text for duplicate-hash
diagnostics. It never uses tier, predictions, probabilities, confidence, or
other model fields to sample or assign labels.
"""

from __future__ import annotations

import csv
import hashlib
import random
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "Data" / "raw"
OUT = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
REPORT = ROOT / "reports" / "pilot_sampling_seed42_report.md"
SEED = 42
PER_PLATFORM = 20

SOURCES = (
    ("youtube", "youtube_data set.csv", "cp1252"),
    ("reddit", "reddit_dataSet.csv", "utf-8-sig"),
    ("twitter", "twitter_data set.csv", "utf-8-sig"),
)

OUTPUT_COLUMNS = (
    "record_id", "platform", "post_text",
    "annotator1_label", "annotator1_confidence", "annotator1_needs_review",
    "annotator1_review_reason", "annotator2_label", "annotator2_confidence",
    "annotator2_needs_review", "annotator2_review_reason", "context_flags",
)


def truthy(value: str) -> bool:
    return value.strip().casefold() in {"true", "1", "yes", "y"}


def text_hash(text: str) -> str:
    value = unicodedata.normalize("NFKC", text)
    value = re.sub(r"\s+", " ", value).strip().casefold()
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def load_source(name: str, filename: str, encoding: str) -> list[dict[str, str]]:
    path = RAW / filename
    if not path.is_file():
        raise RuntimeError(f"Missing source dataset: {path}")
    rows: list[dict[str, str]] = []
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        required = {"record_id", "platform", "post_text", "is_synthetic"}
        if not reader.fieldnames:
            raise RuntimeError(f"No header found in {path}")
        missing = required - set(reader.fieldnames)
        if missing:
            raise RuntimeError(f"{path} missing required columns: {sorted(missing)}")
        seen: set[str] = set()
        try:
            for line, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    raise RuntimeError(f"Malformed row in {path} at CSV line {line}")
                record_id = (row["record_id"] or "").strip()
                if not record_id:
                    raise RuntimeError(f"Missing record_id in {path} at CSV line {line}")
                if record_id in seen:
                    raise RuntimeError(f"Duplicate record_id {record_id!r} in {path}")
                seen.add(record_id)
                source_platform = (row["platform"] or "").strip()
                if source_platform != name:
                    raise RuntimeError(
                        f"Unexpected platform {source_platform!r} in {path} at CSV line {line}; expected {name!r}"
                    )
                post_text = row["post_text"] or ""
                rows.append({
                    "record_id": record_id,
                    "platform": source_platform,
                    "post_text": post_text,
                    "synthetic": "true" if truthy(row["is_synthetic"] or "") else "false",
                    "hash": text_hash(post_text),
                })
        except csv.Error as exc:
            raise RuntimeError(f"CSV parse error in {path} near line {reader.line_num}: {exc}") from exc
    return rows


def report_text(selected: list[dict[str, str]], all_rows: dict[str, list[dict[str, str]]]) -> str:
    groups: dict[str, list[tuple[str, str]]] = {}
    for platform, rows in all_rows.items():
        for row in rows:
            groups.setdefault(row["hash"], []).append((platform, row["record_id"]))
    selected_hashes = {row["hash"] for row in selected}
    selected_groups = {
        h: groups[h] for h in sorted(selected_hashes) if len(groups[h]) > 1
    }
    cross_groups = {
        h: records for h, records in selected_groups.items()
        if len({platform for platform, _ in records}) > 1
    }

    lines = [
        "# Seed-42 Pilot Sampling Report",
        "",
        "## Status",
        "",
        "Created under the owner-approved policy version 0.2 dated 2026-10-19. "
        "This is an unlabeled manual-annotation sample for non-clinical text "
        "signals; it is not clinically validated and does not support diagnosis.",
        "",
        "The previous seed-20261019 pilot artifact and report were not modified, "
        "deleted, or overwritten.",
        "",
        "## Sources and verified counts",
        "",
        "| Platform | Source file | Encoding | Source rows | Source platform values | Synthetic excluded | Selected |",
        "|---|---|---|---:|---|---:|---:|",
    ]
    for platform, filename, encoding in SOURCES:
        rows = all_rows[platform]
        excluded = sum(row["synthetic"] == "true" for row in rows)
        values = ", ".join(sorted({row["platform"] for row in rows}))
        chosen = sum(row["platform"] == platform for row in selected)
        lines.append(f"| {platform} | `{filename}` | `{encoding}` | {len(rows)} | {values} | {excluded} | {chosen} |")

    lines.extend([
        "",
        "## Sampling method",
        "",
        f"- Fixed seed: **{SEED}**, using Python `random.Random(42)`.",
        "- Independently sampled 20 eligible rows per platform.",
        "- Eligibility required a non-empty unique source `record_id` and `is_synthetic` blank/false.",
        "- No tier, keyword, prediction, probability, confidence, or model-related field was used.",
        "- Output preserves source record IDs, platform names, and original post text.",
        "",
        "## Synthetic handling",
        "",
        "YouTube rows with `is_synthetic=TRUE` were excluded from the primary sample. "
        "The verified exclusion count is 125. Reddit and X/Twitter had zero rows "
        "marked synthetic in the inspected sources. No raw row was deleted.",
        "",
        "## Duplicate handling",
        "",
        "Duplicate diagnostics use NFKC normalization, whitespace collapse, trim, "
        "casefold, and truncated SHA-256. Raw post text is not repeated in this report.",
        f"- Selected records in any duplicate-text hash group: {sum(len(v) for v in selected_groups.values())} records across {len(selected_groups)} groups.",
        f"- Selected records in cross-platform duplicate groups: {sum(len(v) for v in cross_groups.values())} records across {len(cross_groups)} groups.",
        "- Duplicate-linked records were not removed. Their groups must be kept together or excluded together in any future evaluation split.",
        "",
        "Selected duplicate-group hashes:",
        "",
    ])
    if selected_groups:
        for digest, records in selected_groups.items():
            platforms = ", ".join(sorted({p for p, _ in records}))
            lines.append(f"- `{digest}` — {len(records)} source records; platforms: {platforms}")
    else:
        lines.append("- None selected.")

    lines.extend([
        "",
        "## Validation",
        "",
        f"- Final data-row count: **{len(selected)}** (header excluded).",
        "- Expected platform counts: YouTube=20, Reddit=20, X/Twitter=20.",
        "- Required output columns were validated before writing.",
        "- Source record IDs were non-empty and unique within each source; selected IDs are unique.",
        "- No explicitly synthetic/augmented YouTube row was selected.",
        "- All annotation fields were written blank: both annotator groups and `context_flags`.",
        "",
        "## Pending work and limitations",
        "",
        "Manual A1/A2 annotation and adjudication are pending. The sample is fixed "
        "and reproducible, not prevalence-representative. Existing tier provenance, "
        "legacy split semantics, and future leakage-safe evaluation policy remain "
        "unresolved. No model was trained and no split was changed.",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    if OUT.exists():
        raise RuntimeError(f"Refusing to overwrite existing output: {OUT}")
    if REPORT.exists():
        raise RuntimeError(f"Refusing to overwrite existing report: {REPORT}")

    all_rows: dict[str, list[dict[str, str]]] = {}
    rng = random.Random(SEED)
    selected: list[dict[str, str]] = []
    for platform, filename, encoding in SOURCES:
        rows = load_source(platform, filename, encoding)
        all_rows[platform] = rows
        eligible = [row for row in rows if row["synthetic"] == "false"]
        if len(eligible) < PER_PLATFORM:
            raise RuntimeError(f"Only {len(eligible)} eligible rows for {platform}")
        selected.extend(rng.sample(eligible, PER_PLATFORM))

    if len(selected) != 60:
        raise RuntimeError(f"Sampling produced {len(selected)} rows, expected 60")

    OUTPUT_FIELDS = set(OUTPUT_COLUMNS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in selected:
            writer.writerow({
                "record_id": row["record_id"], "platform": row["platform"], "post_text": row["post_text"],
                **{field: "" for field in OUTPUT_FIELDS - {"record_id", "platform", "post_text"}},
            })

    REPORT.write_text(report_text(selected, all_rows), encoding="utf-8")
    print(f"Created {OUT} with {len(selected)} rows")
    print(f"Created {REPORT}")


if __name__ == "__main__":
    main()
