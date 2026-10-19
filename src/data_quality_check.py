"""Read-only, reproducible quality assessment for the three project CSVs.

This script does not clean, relabel, split, delete, or rewrite raw data. It
uses only the Python standard library and writes reports under reports/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


DATASETS = {
    "youtube": "youtube_data set.csv",
    "reddit": "reddit_dataSet.csv",
    "x": "twitter_data set.csv",
}
ENCODING_CANDIDATES = ("utf-8-sig", "cp1252", "latin-1")
TIER_PREFIXES = ("tier", "prob_tier")
TEXT_COLUMN = "post_text"


def short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    value = re.sub(r"\s+", " ", value).strip().casefold()
    return value


def choose_encoding(path: Path) -> str:
    for encoding in ENCODING_CANDIDATES:
        try:
            with path.open("r", encoding=encoding, errors="strict", newline="") as handle:
                handle.read(1_000_000)
            return encoding
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Could not decode {path} using {ENCODING_CANDIDATES}")


def parse_datetime(value: str):
    if not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def type_name(value: str) -> str:
    value = value.strip()
    if not value:
        return "missing"
    if value.lower() in {"true", "false"}:
        return "boolean"
    try:
        int(value)
        return "integer"
    except ValueError:
        pass
    try:
        float(value)
        return "number"
    except ValueError:
        pass
    if parse_datetime(value) is not None:
        return "datetime"
    return "string"


def add_count(counter: Counter, key: str, amount: int = 1) -> None:
    counter[key] += amount


def audit_dataset(path: Path, platform: str) -> tuple[dict, dict[str, Counter], dict[str, dict]]:
    encoding = choose_encoding(path)
    malformed = []
    row_count = 0
    header: list[str] = []
    exact_row_hashes = Counter()
    text_hash_rows = Counter()
    text_hashes = defaultdict(list)
    record_ids = Counter()
    user_ids = Counter()
    platform_values = Counter()
    timestamp_values = Counter()
    type_counts = defaultdict(Counter)
    missing = Counter()
    tier_values = defaultdict(Counter)
    split_values = Counter()
    model_split_values = Counter()
    rows_with_both_splits = 0
    split_disagreements = 0
    synthetic_values = Counter()
    synthetic_metadata = defaultdict(Counter)
    valid_timestamps = []
    invalid_timestamps = 0

    with path.open("r", encoding=encoding, errors="strict", newline="") as handle:
        reader = csv.reader(handle, delimiter=",", quotechar='"', strict=False)
        try:
            header = [column.strip() for column in next(reader)]
        except StopIteration:
            raise ValueError(f"Empty CSV: {path}")
        if not header or TEXT_COLUMN not in header:
            raise ValueError(f"{path} does not contain required text column {TEXT_COLUMN!r}")
        width = len(header)
        tier_columns = [c for c in header if c.lower().startswith(TIER_PREFIXES)]
        row_id_column = "record_id" if "record_id" in header else None
        user_column = "anonymized_user_id" if "anonymized_user_id" in header else None
        timestamp_column = "timestamp" if "timestamp" in header else None
        platform_column = "platform" if "platform" in header else None

        for fields in reader:
            physical_line = reader.line_num
            if not fields or (len(fields) == 1 and not fields[0].strip()):
                continue
            row_count += 1
            if len(fields) != width:
                malformed.append({"line": physical_line, "fields": len(fields), "expected": width})
            row = {header[i]: fields[i] if i < len(fields) else "" for i in range(width)}

            for column in header:
                type_counts[column][type_name(row[column])] += 1

            exact_row_hashes[short_hash(json.dumps(fields, ensure_ascii=False, separators=(",", ":")))] += 1
            text = row[TEXT_COLUMN]
            normalized = normalize_text(text)
            missing["missing_text"] += not bool(text)
            missing["whitespace_only_text"] += bool(text) and not bool(text.strip())
            text_hash = short_hash(normalized)
            text_hash_rows[text_hash] += 1
            text_hashes[text_hash].append(row_count)

            if row_id_column:
                record_ids[row[row_id_column]] += 1
                missing["missing_record_id"] += not bool(row[row_id_column].strip())
            if user_column:
                user_ids[row[user_column]] += 1
                missing["missing_user_id"] += not bool(row[user_column].strip())
            if platform_column:
                platform_values[row[platform_column]] += 1
            if timestamp_column:
                timestamp = row[timestamp_column]
                timestamp_values[timestamp] += 1
                missing["missing_timestamp"] += not bool(timestamp.strip())
                parsed = parse_datetime(timestamp)
                if timestamp.strip() and parsed is None:
                    invalid_timestamps += 1
                elif parsed is not None:
                    valid_timestamps.append(parsed.isoformat())

            for column in tier_columns:
                tier_values[column][row[column] if row[column] else "<empty>"] += 1

            split = row.get("split", "")
            model_split = row.get("model_split", "")
            if split:
                split_values[split] += 1
            if model_split:
                model_split_values[model_split] += 1
            if split and model_split:
                rows_with_both_splits += 1
                if split != model_split:
                    split_disagreements += 1

            synthetic = row.get("is_synthetic", "") or "<empty>"
            synthetic_values[synthetic] += 1
            if synthetic.upper() == "TRUE":
                for column in ("tier", "tier_source", "aug_method", "split", "model_split", "parent_record_id"):
                    if column in row:
                        value = row[column] if row[column] else "<empty>"
                        if column == "parent_record_id" and value != "<empty>":
                            value = "hash:" + short_hash(value)
                        synthetic_metadata[column][value] += 1

    duplicate_exact = {h: n for h, n in exact_row_hashes.items() if n > 1}
    duplicate_text = {h: n for h, n in text_hash_rows.items() if n > 1}
    record_id_duplicates = sum(n - 1 for n in record_ids.values() if n > 1)
    distinct_users = len([v for v in user_ids if v])
    distinct_platforms = len([v for v in platform_values if v])

    strict_parser_errors = []
    with path.open("r", encoding=encoding, errors="strict", newline="") as handle:
        strict_reader = csv.reader(handle, delimiter=",", quotechar='"', strict=True)
        try:
            next(strict_reader)
            while True:
                try:
                    next(strict_reader)
                except StopIteration:
                    break
        except csv.Error as exc:
            strict_parser_errors.append({"line": strict_reader.line_num, "reason": str(exc)})

    result = {
        "platform": platform,
        "filename": path.name,
        "relative_path": str(path),
        "size_bytes": path.stat().st_size,
        "encoding_detected": encoding,
        "row_count_exact": row_count,
        "columns": header,
        "inferred_type_counts_exact": {c: dict(v) for c, v in type_counts.items()},
        "metadata_columns": {
            "text": TEXT_COLUMN,
            "record_id": row_id_column,
            "user_id": user_column,
            "timestamp": timestamp_column,
            "platform": platform_column,
        },
        "missing_values_exact": dict(missing),
        "timestamp_metadata": {
            "valid_count": len(valid_timestamps),
            "invalid_count": invalid_timestamps,
            "min": min(valid_timestamps) if valid_timestamps else None,
            "max": max(valid_timestamps) if valid_timestamps else None,
        },
        "platform_values_exact": dict(platform_values),
        "user_metadata": {
            "distinct_nonempty_user_ids": distinct_users,
            "repeated_user_rows": sum(n - 1 for v, n in user_ids.items() if v and n > 1),
        },
        "record_id_metadata": {
            "distinct_nonempty_record_ids": len([v for v in record_ids if v]),
            "duplicate_record_id_extra_rows": record_id_duplicates,
            "all_record_ids_unique": record_id_duplicates == 0 and missing["missing_record_id"] == 0,
        },
        "exact_duplicate_rows": {
            "duplicate_hash_groups": len(duplicate_exact),
            "duplicate_extra_rows": sum(n - 1 for n in duplicate_exact.values()),
            "hash_counts": duplicate_exact,
        },
        "normalized_text_duplicates": {
            "normalization": "Unicode NFKC, whitespace collapsed, trim, casefold",
            "duplicate_hash_groups": len(duplicate_text),
            "duplicate_extra_rows": sum(n - 1 for n in duplicate_text.values()),
            "hash_counts": duplicate_text,
        },
        "tier_related_distributions_exact": {c: dict(v) for c, v in tier_values.items()},
        "split_metadata_exact": {
            "split": dict(split_values),
            "model_split": dict(model_split_values),
            "rows_with_both": rows_with_both_splits,
            "disagreement_rows": split_disagreements,
        },
        "synthetic_metadata": {
            "is_synthetic_distribution": dict(synthetic_values),
            "synthetic_row_count": synthetic_values.get("TRUE", 0),
            "metadata_distributions": {c: dict(v) for c, v in synthetic_metadata.items()},
        },
        "csv_parse_diagnostics": {
            "malformed_width_rows": malformed,
            "strict_parser_errors": strict_parser_errors,
        },
        "_text_hashes": set(text_hash_rows),
    }
    return result, tier_values, text_hashes


def cross_platform(results: list[dict]) -> dict:
    names = [r["platform"] for r in results]
    hash_sets = {r["platform"]: r["_text_hashes"] for r in results}
    pairs = {}
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            common = sorted(hash_sets[left] & hash_sets[right])
            pairs[f"{left}__{right}"] = {
                "shared_normalized_text_hash_groups": len(common),
                "hashes": common,
            }
    return {
        "normalization": "Unicode NFKC, whitespace collapsed, trim, casefold; SHA-256 truncated to 16 hex characters",
        "pairwise_overlap": pairs,
    }


def md_distribution(values: dict, limit: int | None = None) -> str:
    if not values:
        return "none"
    items = list(values.items())
    if limit is not None and len(items) > limit:
        items = sorted(items, key=lambda item: (-item[1], item[0]))[:limit]
        return ", ".join(f"{key}={value}" for key, value in items) + f" (top {limit}; {len(values)} distinct values in JSON)"
    return ", ".join(f"{key}={value}" for key, value in items)


def write_markdown(bundle: dict, path: Path) -> None:
    lines = [
        "# Data-quality assessment",
        "",
        "Scope: read-only assessment of the three current raw datasets. No raw file was modified, relabeled, split, or deleted.",
        "",
        "Tier-related columns are reported as existing metadata only. Numeric values are not assigned mental-health meanings and are not treated as verified ground truth.",
        "",
        "## Dataset summaries",
        "",
    ]
    for item in bundle["datasets"]:
        lines.extend([
            f"### {item['platform']}: {item['filename']}",
            "",
            f"- Path: {item['relative_path']}",
            f"- Size: {item['size_bytes']:,} bytes",
            f"- Encoding detected: {item['encoding_detected']}",
            f"- Exact row count: {item['row_count_exact']:,}",
            f"- Columns ({len(item['columns'])}): {', '.join(item['columns'])}",
            f"- Metadata columns: {item['metadata_columns']}",
            f"- Missing values: {item['missing_values_exact']}",
            f"- Timestamp metadata: {item['timestamp_metadata']}",
            f"- Platform values: {md_distribution(item['platform_values_exact'])}",
            f"- User metadata: {item['user_metadata']}",
            f"- Record ID metadata: {item['record_id_metadata']}",
            f"- Exact duplicate rows: {item['exact_duplicate_rows']['duplicate_extra_rows']:,} extra rows across {item['exact_duplicate_rows']['duplicate_hash_groups']:,} hash groups",
            f"- Normalized duplicate post_text: {item['normalized_text_duplicates']['duplicate_extra_rows']:,} extra rows across {item['normalized_text_duplicates']['duplicate_hash_groups']:,} hash groups",
            f"- CSV diagnostics: {len(item['csv_parse_diagnostics']['malformed_width_rows'])} width anomalies; {len(item['csv_parse_diagnostics']['strict_parser_errors'])} strict parser errors",
            "",
            "#### Existing tier-related distributions",
            "",
        ])
        for column, distribution in item["tier_related_distributions_exact"].items():
            limit = 10 if len(distribution) > 20 else None
            lines.append(f"- {column}: {md_distribution(distribution, limit)}")
        lines.extend([
            "",
            "#### Split metadata",
            "",
            f"- split: {md_distribution(item['split_metadata_exact']['split'])}",
            f"- model_split: {md_distribution(item['split_metadata_exact']['model_split'])}",
            f"- disagreement rows: {item['split_metadata_exact']['disagreement_rows']}",
            "",
            "#### YouTube synthetic/augmented metadata" if item["platform"] == "youtube" else "#### Synthetic/augmented metadata",
            "",
            f"- is_synthetic: {md_distribution(item['synthetic_metadata']['is_synthetic_distribution'])}",
            f"- synthetic row count: {item['synthetic_metadata']['synthetic_row_count']}",
        ])
        if item["synthetic_metadata"]["metadata_distributions"]:
            for column, distribution in item["synthetic_metadata"]["metadata_distributions"].items():
                lines.append(f"- synthetic rows, {column}: {md_distribution(distribution)}")
        lines.append("")

    lines.extend(["## Cross-platform normalized text hashes", ""])
    lines.append("Normalization: Unicode NFKC, whitespace collapsed, trimmed, casefolded; hashes are truncated SHA-256 values. Raw post text is not included.")
    lines.append("")
    for pair, overlap in bundle["cross_platform"]["pairwise_overlap"].items():
        lines.append(f"- {pair}: {overlap['shared_normalized_text_hash_groups']} shared hash groups: {', '.join(overlap['hashes']) if overlap['hashes'] else 'none'}")
    lines.extend([
        "",
        "## Interpretation and limitations",
        "",
        "- Existing tier-related distributions are descriptive only; this report does not infer class meanings.",
        "- The report does not assign proposed annotation labels and does not use keywords, tiers, predictions, or probabilities to label text.",
        "- Duplicate hashes identify possible repeated content, not whether a record is erroneous.",
        "- YouTube synthetic rows are retained and separately summarized; they were not removed.",
        "- Current split and model_split values are reported without changing them. Their provenance remains unresolved.",
        "",
        "## Recommended next step",
        "",
        "Review this quality report with the annotation guidelines, then conduct a small human-annotated pilot using a separate protected working artifact. Resolve provenance and split policies before any cleaning, relabeling, cross-platform combination, or model training.",
        "",
        "This is a non-clinical linguistic-signal research assessment; it does not produce diagnoses.",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=None, help="Raw-data directory, relative to project root by default")
    parser.add_argument("--reports-dir", type=Path, default=None, help="Reports directory, relative to project root by default")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    raw_dir = args.raw_dir or project_root / "Data" / "raw"
    reports_dir = args.reports_dir or project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    missing = [str(raw_dir / filename) for filename in DATASETS.values() if not (raw_dir / filename).is_file()]
    if missing:
        raise FileNotFoundError("Missing required dataset file(s): " + ", ".join(missing))

    results = []
    for platform, filename in DATASETS.items():
        result, _, _ = audit_dataset(raw_dir / filename, platform)
        results.append(result)

    cross = cross_platform(results)
    for result in results:
        result.pop("_text_hashes", None)
    bundle = {
        "scope": "three current raw datasets only",
        "generated_local_time": datetime.now().astimezone().isoformat(),
        "datasets": results,
        "cross_platform": cross,
        "raw_files_modified": False,
        "labels_assigned": False,
        "training_performed": False,
    }
    json_path = reports_dir / "data_quality_report.json"
    md_path = reports_dir / "data_quality_report.md"
    json_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(bundle, md_path)
    print(f"Wrote {md_path}")
    print(f"Wrote {json_path}")


if __name__ == "__main__":
    main()
