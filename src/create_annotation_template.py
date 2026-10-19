"""Create a separate, unlabeled human-annotation template.

This script is intentionally limited to preparation infrastructure. It does not
read tier fields to assign labels, modify raw CSVs, remove duplicates, or create
data splits. It streams each input file with Python's standard-library CSV
reader and fails loudly on malformed rows or missing required columns.

Run from the project root:
    python src/create_annotation_template.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "Data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "Data" / "processed"
OUTPUT_TEMPLATE = OUTPUT_DIR / "annotation_template.csv"
OUTPUT_REPORT = PROJECT_ROOT / "reports" / "annotation_template_report.md"

INPUTS = (
    ("YouTube", "youtube_data set.csv", "cp1252"),
    ("Reddit", "reddit_dataSet.csv", "utf-8-sig"),
    ("X/Twitter", "twitter_data set.csv", "utf-8-sig"),
)

REQUIRED_COLUMNS = {"record_id", "platform", "post_text", "is_synthetic"}
OUTPUT_COLUMNS = (
    "record_id",
    "platform",
    "post_text",
    "record_type",
    "annotator_label",
    "confidence",
    "needs_review",
    "review_reason",
)


class TemplateInputError(RuntimeError):
    """Raised when an input cannot be safely represented in the template."""


def is_truthy(value: str) -> bool:
    return value.strip().casefold() in {"true", "1", "yes", "y"}


def read_rows(platform_name: str, filename: str, encoding: str):
    """Yield validated output rows and source statistics for one CSV."""
    path = RAW_DIR / filename
    if not path.is_file():
        raise TemplateInputError(f"Missing required input file: {path}")

    try:
        handle = path.open("r", encoding=encoding, newline="")
    except OSError as exc:
        raise TemplateInputError(f"Cannot open {path}: {exc}") from exc

    with handle:
        reader = csv.DictReader(handle, strict=True)
        if reader.fieldnames is None:
            raise TemplateInputError(f"Input has no header: {path}")
        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise TemplateInputError(
                f"{path} is missing required columns: {', '.join(sorted(missing))}"
            )

        seen_ids: set[str] = set()
        row_count = 0
        synthetic_count = 0
        fallback_ids = 0

        try:
            for source_row_number, row in enumerate(reader, start=2):
                row_count += 1
                if None in row:
                    raise TemplateInputError(
                        f"Malformed row in {path} at CSV line {source_row_number}: "
                        "more fields than the header"
                    )
                if any(value is None for value in row.values()):
                    raise TemplateInputError(
                        f"Malformed row in {path} at CSV line {source_row_number}: "
                        "missing field value"
                    )

                source_id = (row.get("record_id") or "").strip()
                if source_id:
                    record_id = source_id
                else:
                    # Deterministic, non-source identifier. The raw row is not
                    # changed; the fallback is only written to this artifact.
                    record_id = f"{platform_name.lower().replace('/', '_')}:row-{source_row_number:06d}"
                    fallback_ids += 1

                if record_id in seen_ids:
                    raise TemplateInputError(
                        f"Duplicate annotation record_id {record_id!r} in {path} "
                        f"at CSV line {source_row_number}"
                    )
                seen_ids.add(record_id)

                synthetic = is_truthy(row.get("is_synthetic", ""))
                if synthetic:
                    synthetic_count += 1
                record_type = "synthetic_or_augmented" if synthetic else "original_or_unspecified"

                yield {
                    "record_id": record_id,
                    "platform": row.get("platform", "").strip() or platform_name,
                    "post_text": row.get("post_text", ""),
                    "record_type": record_type,
                    "annotator_label": "",
                    "confidence": "",
                    "needs_review": "",
                    "review_reason": "",
                }, {
                    "rows": row_count,
                    "synthetic": synthetic_count,
                    "fallback_ids": fallback_ids,
                    "unique_ids": len(seen_ids),
                }
        except csv.Error as exc:
            line_number = getattr(reader, "line_num", "unknown")
            raise TemplateInputError(
                f"Malformed CSV in {path} near CSV line {line_number}: {exc}"
            ) from exc


def write_report(stats: dict[str, dict[str, int]], total_rows: int) -> None:
    lines = [
        "# Annotation Template Report",
        "",
        "## Status",
        "",
        "This report describes a separate, unlabeled annotation artifact generated "
        "from the three current raw CSVs. Raw files were read only and were not "
        "modified, relabeled, split, or deduplicated.",
        "",
        "The template does not use `tier`, `tier_lexicon`, `tier_corrected`, "
        "`tier_model`, `tier_pred`, keywords, confidence/probability fields, or "
        "any other legacy metadata to assign labels. All annotation fields are "
        "blank for human completion.",
        "",
        "## Output",
        "",
        f"- Template: `{OUTPUT_TEMPLATE.relative_to(PROJECT_ROOT)}`",
        f"- Total template rows: **{total_rows}**",
        "- Output encoding: UTF-8 CSV with standard quoting.",
        "- Output columns: `record_id`, `platform`, `post_text`, `record_type`, "
        "`annotator_label`, `confidence`, `needs_review`, `review_reason`.",
        "",
        "## Counts and identifier checks",
        "",
        "| Platform | Source rows | Template rows | Synthetic/augmented | Fallback IDs | IDs unique |\n"
        "|---|---:|---:|---:|---:|---|",
    ]
    for platform_name, _, _ in INPUTS:
        item = stats[platform_name]
        lines.append(
            f"| {platform_name} | {item['rows']} | {item['rows']} | "
            f"{item['synthetic']} | {item['fallback_ids']} | "
            f"{'yes' if item['unique_ids'] == item['rows'] else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Synthetic-record handling",
            "",
            "All source rows are included, including the explicitly marked synthetic "
            "or augmented YouTube rows. They are marked in `record_type` as "
            "`synthetic_or_augmented`; non-synthetic or blank-source-status rows are "
            "marked `original_or_unspecified`. No row was silently excluded.",
            "",
            "The `record_type` value is descriptive metadata copied from the source "
            "`is_synthetic` flag. It is not an annotation label and must not be used "
            "to infer a linguistic-signal class.",
            "",
            "## Identifier handling",
            "",
            "The existing non-empty source `record_id` is preserved. If a source row "
            "has no record ID, the script creates a deterministic platform-and-row "
            "fallback only in the annotation artifact; it never writes back to the "
            "raw CSV. Duplicate output IDs cause the script to fail rather than be "
            "silently altered.",
            "",
            "## Annotation safety",
            "",
            "`annotator_label` must be assigned by a human using the approved "
            "annotation guidelines. The labels describe observable non-clinical "
            "linguistic signals, not a person's diagnosis, identity, or clinical "
            "severity.",
        ]
    )
    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    stats: dict[str, dict[str, int]] = {}
    total_rows = 0

    try:
        with OUTPUT_TEMPLATE.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
            writer.writeheader()
            for platform_name, filename, encoding in INPUTS:
                platform_rows = 0
                platform_stats = None
                for output_row, current_stats in read_rows(platform_name, filename, encoding):
                    writer.writerow(output_row)
                    platform_rows += 1
                    platform_stats = current_stats
                if platform_stats is None:
                    platform_stats = {
                        "rows": 0,
                        "synthetic": 0,
                        "fallback_ids": 0,
                        "unique_ids": 0,
                    }
                platform_stats["rows"] = platform_rows
                platform_stats["unique_ids"] = platform_stats["unique_ids"]
                stats[platform_name] = platform_stats
                total_rows += platform_rows
    except (OSError, UnicodeError, csv.Error, TemplateInputError) as exc:
        if OUTPUT_TEMPLATE.exists():
            OUTPUT_TEMPLATE.unlink()
        print(f"ERROR: annotation template was not created: {exc}", file=sys.stderr)
        return 1

    write_report(stats, total_rows)
    print(f"Created {OUTPUT_TEMPLATE} with {total_rows} unlabeled rows.")
    print(f"Created {OUTPUT_REPORT}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
