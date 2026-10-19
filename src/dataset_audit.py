"""Safe, streaming audit for the three current social-media CSV inputs.

This script never writes to data/raw. It uses the Python standard library so it
can be rerun on a clean Windows installation. Statistics are full-file unless
explicitly marked as sample-based. Reports contain hashes/counts, not raw text
or user identifiers.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


EXPECTED_FILES = {"reddit": "reddit_dataSet.csv", "x": "twitter_data set.csv", "youtube": "youtube_data set.csv"}
TEXT_CANDIDATES = ["post_text", "text", "tweet", "comment", "content", "description"]
USER_CANDIDATES = ["anonymized_user_id", "user_id", "author_id", "username", "author"]
TIME_CANDIDATES = ["timestamp", "created_at", "date", "datetime", "time"]
LABEL_CANDIDATES = ["tier", "label", "class", "target", "category", "sentiment"]


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()[:16]


def detect_encoding(path: Path) -> dict:
    raw = path.read_bytes()
    bom = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else None
    candidates = ["utf-8-sig", "utf-16", "cp1252", "latin-1"]
    for enc in candidates:
        try:
            text = raw[:1_000_000].decode(enc)
            nul = text.count("\x00")
            return {"encoding": enc, "bom": bom, "decode_errors": 0, "sample_nul_chars": nul, "sample_bytes": min(len(raw), 1_000_000)}
        except UnicodeDecodeError:
            continue
    return {"encoding": "utf-8", "bom": bom, "decode_errors": "sample failed", "sample_nul_chars": None, "sample_bytes": min(len(raw), 1_000_000)}


def sniff_format(path: Path, encoding: str) -> dict:
    sample = path.open("r", encoding=encoding, errors="replace", newline="").read(128_000)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        delimiter, quotechar, quoting = dialect.delimiter, dialect.quotechar, dialect.quoting
    except csv.Error:
        delimiter, quotechar, quoting = ",", '"', csv.QUOTE_MINIMAL
    try:
        has_header = csv.Sniffer().has_header(sample)
    except csv.Error:
        has_header = None
    return {"delimiter": repr(delimiter), "quotechar": quotechar, "quoting": repr(quoting), "has_header_guess": has_header}


def parse_time(value: str):
    if not value:
        return None
    s = value.strip()
    for candidate in (s, s.replace("Z", "+00:00")):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass
    return None


def inferred_type(value: str) -> str:
    s = value.strip()
    if not s:
        return "missing"
    if s.lower() in {"true", "false"}:
        return "boolean"
    try:
        int(s)
        return "integer"
    except ValueError:
        pass
    try:
        float(s)
        return "number"
    except ValueError:
        pass
    if parse_time(s) is not None:
        return "datetime"
    return "string"


def choose(columns, candidates):
    lower = {c.lower(): c for c in columns}
    return next((lower[c] for c in candidates if c in lower), None)


def safe_value(row, col):
    return (row.get(col) or "").strip() if col else ""


def audit_file(path: Path, platform: str) -> dict:
    enc_info = detect_encoding(path)
    encoding = enc_info["encoding"]
    fmt = sniff_format(path, encoding)
    delimiter = eval(fmt["delimiter"])  # value was produced internally by repr
    parse_errors = []
    bad_width = []
    row_count = 0
    header = []
    counters = Counter()
    value_counts = defaultdict(Counter)
    duplicate_sets = {"record_id": set(), "text": set(), "user": set(), "parent": set()}
    duplicate_counts = Counter()
    split_by_text = defaultdict(set)
    split_by_user = defaultdict(set)
    parent_by_split = defaultdict(set)
    language = Counter()
    timestamps = Counter()
    text_examples = Counter()
    feature_counts = Counter()
    type_counts = defaultdict(Counter)
    split_conflicts = Counter()
    strict_error_count = 0

    with path.open("r", encoding=encoding, errors="replace", newline="") as fh:
        reader = csv.reader(fh, delimiter=delimiter, quotechar=fmt["quotechar"], strict=False)
        try:
            header = next(reader)
        except StopIteration:
            header = []
        header = [h.strip() for h in header]
        text_col, user_col, time_col = choose(header, TEXT_CANDIDATES), choose(header, USER_CANDIDATES), choose(header, TIME_CANDIDATES)
        label_cols = [c for c in header if c.lower() in LABEL_CANDIDATES or c.lower().startswith(("tier_", "prob_tier_"))]
        row_width = len(header)
        for fields in reader:
            line = reader.line_num
            if len(fields) == 0 or (len(fields) == 1 and not fields[0].strip()):
                continue
            row_count += 1
            if len(fields) != row_width:
                bad_width.append({"line": line, "fields": len(fields), "expected": row_width, "reason": "field_count_mismatch"})
            row = {header[i]: fields[i] if i < len(fields) else "" for i in range(len(header))}
            for c in header:
                type_counts[c][inferred_type(row[c])] += 1
            text = safe_value(row, text_col)
            user = safe_value(row, user_col)
            timestamp = safe_value(row, time_col)
            rec = safe_value(row, choose(header, ["record_id", "id"]))
            parent = safe_value(row, choose(header, ["parent_record_id", "parent_id"]))
            split = safe_value(row, choose(header, ["split", "model_split"]))
            split_value = safe_value(row, "split")
            model_split_value = safe_value(row, "model_split")
            if split_value and model_split_value:
                split_conflicts["rows_with_both"] += 1
                split_conflicts["split_model_split_disagreement"] += split_value != model_split_value
            counters["missing_text"] += not bool(text)
            counters["empty_text"] += text == ""
            counters["missing_user"] += not bool(user)
            counters["missing_timestamp"] += not bool(timestamp)
            counters["invalid_timestamp"] += bool(timestamp) and parse_time(timestamp) is None
            counters["missing_labels"] += not any(safe_value(row, c) for c in label_cols)
            if text:
                h = sha(text)
                if h in duplicate_sets["text"]: duplicate_counts["duplicate_text_rows"] += 1
                duplicate_sets["text"].add(h)
                if split: split_by_text[h].add(split)
                feature_counts["text_non_ascii"] += any(ord(ch) > 127 for ch in text)
                feature_counts["text_emoji_like"] += any(0x1F300 <= ord(ch) <= 0x1FAFF for ch in text)
                feature_counts["text_url"] += bool(re.search(r"https?://|www\.", text, re.I))
                feature_counts["text_username"] += bool(re.search(r"(?<!\w)@[A-Za-z0-9_]+", text))
                feature_counts["text_negation"] += bool(re.search(r"\b(no|not|never|dont|don't|can't|cannot|without|isn't|wasn't)\b", text, re.I))
            if rec:
                if rec in duplicate_sets["record_id"]: duplicate_counts["duplicate_record_id_rows"] += 1
                duplicate_sets["record_id"].add(rec)
            if user:
                if user in duplicate_sets["user"]: duplicate_counts["repeated_user_rows"] += 1
                duplicate_sets["user"].add(user)
                if split: split_by_user[sha(user)].add(split)
            if parent:
                duplicate_sets["parent"].add(parent)
                if split: parent_by_split[parent].add(split)
            language[safe_value(row, choose(header, ["lang", "language"])) or "<missing>"] += 1
            if timestamp:
                timestamps["valid"] += parse_time(timestamp) is not None
                timestamps["invalid"] += parse_time(timestamp) is None
            for c in label_cols:
                val = safe_value(row, c)
                if val: value_counts[c][val] += 1

    # A second strict pass diagnoses parser-level failures without affecting stats.
    with path.open("r", encoding=encoding, errors="replace", newline="") as fh:
        strict = csv.reader(fh, delimiter=delimiter, quotechar=fmt["quotechar"], strict=True)
        try: next(strict)
        except StopIteration: pass
        while True:
            try:
                next(strict)
            except StopIteration:
                break
            except csv.Error as exc:
                strict_error_count += 1
                if len(parse_errors) < 100:
                    parse_errors.append({"line": strict.line_num, "reason": "csv_parser_error", "detail": str(exc)})
                # strict csv cannot reliably resume after an unterminated quote;
                # the permissive pass above still records width anomalies.
                break

    conflicts = {
        "text_hashes_in_multiple_splits": sum(len(v) > 1 for v in split_by_text.values()),
        "users_in_multiple_splits": sum(len(v) > 1 for v in split_by_user.values()),
        "parent_ids_in_multiple_splits": sum(len(v) > 1 for v in parent_by_split.values()),
    }
    provenance = {}
    for c in label_cols:
        provenance[c] = {"distinct": len(value_counts[c]), "top_values": value_counts[c].most_common(20), "interpretation": "column name/value metadata only; ground-truth status is unverified"}
    return {
        "platform": platform, "file": path.name, "size_bytes": path.stat().st_size, "encoding": enc_info,
        "format": fmt, "columns": header, "row_count_exact": row_count, "column_count": len(header),
        "selected_columns": {"text": text_col, "user_id": user_col, "timestamp": time_col, "label_candidates": label_cols},
        "inferred_types_exact": {c: dict(v) for c, v in type_counts.items()},
        "missing_and_validity_exact": dict(counters), "language_counts_exact": dict(language),
        "timestamp_counts_exact": dict(timestamps), "text_content_flags_exact": dict(feature_counts),
        "split_consistency_exact": dict(split_conflicts),
        "duplicate_and_leakage_exact": {**dict(duplicate_counts), "unique_record_ids": len(duplicate_sets["record_id"]), "unique_text_hashes": len(duplicate_sets["text"]), "unique_users": len(duplicate_sets["user"]), "unique_parent_ids": len(duplicate_sets["parent"]), **conflicts},
        "label_columns": provenance, "malformed_rows": {"count": len(bad_width), "examples": bad_width[:100], "parser_error_count": strict_error_count, "parser_errors": parse_errors},
        "_user_hashes": duplicate_sets["user"], "_text_hashes": duplicate_sets["text"],
    }


def cross_file(results):
    pairs = {}
    for i, left in enumerate(results):
        for right in results[i + 1:]:
            pairs[f"{left['platform']}__{right['platform']}"] = {
                "user_hash_overlap": len(left["_user_hashes"] & right["_user_hashes"]),
                "text_hash_overlap": len(left["_text_hashes"] & right["_text_hashes"]),
            }
    return {"privacy_preserving_exact_hash_overlap": pairs, "note": "Counts are hash overlaps, not proof of identity; investigate provenance before combining datasets."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    ap.add_argument("--reports-dir", type=Path, default=Path("reports"))
    args = ap.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for platform, expected in EXPECTED_FILES.items():
        path = args.raw_dir / expected
        if not path.is_file():
            raise FileNotFoundError(f"Required current {platform} dataset not found: {path}")
        files.append((platform, path))
    results = [audit_file(path, platform) for platform, path in files]
    cross = cross_file(results)
    for r in results:
        r.pop("_user_hashes", None)
        r.pop("_text_hashes", None)
    bundle = {"audit_scope": "the three currently present project datasets only", "generated_utc": datetime.now().astimezone().isoformat(), "results": results, "cross_file": cross, "caveat": "This is dataset quality/provenance analysis, not clinical assessment and not model training."}
    (args.reports_dir / "dataset_audit.json").write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")
    reddit = next(r for r in results if r["platform"] == "reddit")
    reddit_report = {"scope": "reddit_dataSet.csv", "parsing": reddit["format"], "encoding": reddit["encoding"], "exact_rows": reddit["row_count_exact"], "columns": reddit["columns"], "selected_columns": reddit["selected_columns"], "malformed_rows": reddit["malformed_rows"], "label_provenance": reddit["label_columns"], "duplicates_and_leakage": reddit["duplicate_and_leakage_exact"], "unresolved_questions": ["Which labels are human annotations versus lexicon/model outputs?", "What do classes 0-3 mean, and who verified them?", "Why do split and model_split exist, and which is authoritative?", "Are synthetic/augmented rows allowed in evaluation?", "Are timestamps collection time or original-post time?"], "recommended_next_steps": ["Obtain dataset documentation and label-generation code.", "Freeze a leakage policy before any split or training.", "Manually review a small stratified sample with privacy safeguards.", "Do not treat tier as verified ground truth without provenance evidence."]}
    (args.reports_dir / "reddit_audit.json").write_text(json.dumps(reddit_report, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Initial dataset audit", "", "Scope: exactly the three current files in `data/raw/`; raw files were not modified.", "", "## Dataset summary", ""]
    for r in results:
        lines += [f"- **{r['file']}** ({r['platform']}): {r['size_bytes']:,} bytes; {r['row_count_exact']:,} exact data rows; {r['column_count']} columns; encoding `{r['encoding']['encoding']}`; delimiter `{r['format']['delimiter']}`.", f"  - Selected columns: text=`{r['selected_columns']['text']}`, user=`{r['selected_columns']['user_id']}`, timestamp=`{r['selected_columns']['timestamp']}`, labels={r['selected_columns']['label_candidates']}.", f"  - Missing/validity: {r['missing_and_validity_exact']}", f"  - Malformed: {r['malformed_rows']['count']} width mismatches; {r['malformed_rows']['parser_error_count']} strict parser errors.", f"  - Duplicates/leakage indicators: {r['duplicate_and_leakage_exact']}", ""]
    lines += ["## Interpretation cautions", "", "Label names and values are reported as observed metadata. No label is assumed to be human-annotated or clinically valid. `tier`, `tier_corrected`, `tier_model`, `tier_source`, confidence and probabilities must be traced to documentation/code before use.", "", "## Text preservation", "", "The audit counts non-ASCII characters, emoji-like code points, URLs, usernames and common negation forms. These are warnings against careless normalization, not language or clinical judgments.", "", "## Unresolved questions and recommended next steps", "", "See `reddit_audit.json` for the dedicated Reddit questions. Obtain provenance, define leakage policy, review labels, and only then design cleaning/splitting. Do not train yet.", ""]
    (args.reports_dir / "dataset_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Audited {len(results)} datasets. Reports written to {args.reports_dir.resolve()}")


if __name__ == "__main__":
    main()
