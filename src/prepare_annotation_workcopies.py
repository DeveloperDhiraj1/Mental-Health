"""Create and validate isolated A1/A2 annotation work copies.

The script reads only the already-created seed-42 pilot sample. It does not
read raw datasets or legacy metadata, does not assign labels, and refuses to
overwrite existing work copies or the source pilot file.

Run from the project root:
    python src/prepare_annotation_workcopies.py
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Data" / "processed" / "pilot_annotation_seed42.csv"
WORK_DIR = ROOT / "Data" / "processed" / "annotation_work"
README = WORK_DIR / "README.md"
WORKERS = ("A1", "A2")

SOURCE_COLUMNS = (
    "record_id", "platform", "post_text", "annotator1_label",
    "annotator1_confidence", "annotator1_needs_review",
    "annotator1_review_reason", "annotator2_label", "annotator2_confidence",
    "annotator2_needs_review", "annotator2_review_reason", "context_flags",
)
WORK_COLUMNS = (
    "record_id", "platform", "post_text", "annotator_label",
    "annotator_confidence", "needs_review", "review_reason", "context_flags",
)
ANNOTATION_COLUMNS = WORK_COLUMNS[3:]


def read_source() -> list[dict[str, str]]:
    if not SOURCE.is_file():
        raise RuntimeError(f"Missing required seed-42 source sample: {SOURCE}")
    with SOURCE.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if tuple(reader.fieldnames or ()) != SOURCE_COLUMNS:
            raise RuntimeError(
                "Seed-42 source schema mismatch. Expected "
                f"{SOURCE_COLUMNS}, found {reader.fieldnames}"
            )
        rows = list(reader)
    if len(rows) != 60:
        raise RuntimeError(f"Seed-42 source has {len(rows)} rows; expected 60")
    ids = [row["record_id"] for row in rows]
    if any(not value.strip() for value in ids):
        raise RuntimeError("Seed-42 source contains a missing record_id")
    if len(set(ids)) != len(ids):
        raise RuntimeError("Seed-42 source contains duplicate record_ids")
    if any(not row["platform"].strip() for row in rows):
        raise RuntimeError("Seed-42 source contains a missing platform")
    if any(not row["post_text"].strip() for row in rows):
        raise RuntimeError("Seed-42 source contains empty post_text")
    return rows


def write_readme() -> None:
    README.write_text(
        """# Manual Annotation Work Copies

## Status and purpose

These are separate local work copies of the approved 60-row seed-42 pilot.
`A1_annotation.csv` is for annotator A1 and `A2_annotation.csv` is for
annotator A2. The copies contain no prefilled labels or predictions.

The annotation describes observable linguistic signals in text. It is not a
diagnosis, clinical screening result, severity score, or assessment of the
author's personal condition.

## Approved signal labels

Use only these four labels:

- `none_other`: use alone only when none of the other three signals applies and the text is sufficiently clear.
- `distress_negative_affect`: explicit emotional strain, suffering, hopelessness, loneliness, fear, overwhelm, sadness, anger, or related negative affect.
- `mental_health_reference_or_support`: meaningful discussion of mental-health care, therapy, counselling, coping, recovery, wellbeing, support, or help-seeking.
- `self_harm_related`: explicit self-harm, suicide, wanting to die, attempts, planning, prevention, recovery, safety planning, or immediate safety support content.

The three substantive labels may co-occur. Serialize applicable labels in this
fixed order, separated by `|` with no spaces:

`distress_negative_affect|mental_health_reference_or_support|self_harm_related`

`none_other` must stand alone. Do not use legacy tiers, predictions,
probabilities, confidence metadata, keywords, or model fields as ground truth.

## Context and uncertainty

Enter context separately in `context_flags`, never as a signal label. Suggested
flags include `first_person_or_self_report`, `third_person`,
`quoted_or_reported`, `educational_or_information`, `fictional_or_hypothetical`,
`sarcastic_or_ironic`, `promotional_or_campaign`, and `context_insufficient`.

For quoted, educational, fictional, hypothetical, or third-person text, apply a
content label only when the topic is clearly present, add the context flag, and
do not infer that the author personally experienced it. Explicit prevention or
recovery content may receive `self_harm_related` as a content label; this does
not indicate current personal risk.

If the meaning is ambiguous, sarcastic, incomplete, unreadable, or dependent on
missing context, do not guess. Leave the label blank, set `needs_review=TRUE`,
and record a reason such as `insufficient_context`, `ambiguous`,
`sarcasm_or_irony`, `quoted_or_reported`, `fictional_or_hypothetical`,
`educational_context`, or `language_or_encoding`.

## Privacy and independence

Keep both files local and do not upload raw posts publicly. Use only the
pseudonymous ID assigned to the file: A1 or A2. Do not share one annotator's
file with the other. Do not modify `record_id`, `platform`, or `post_text`.
Preserve both completed files for later disagreement review.

""",
        encoding="utf-8",
    )


def write_copy(worker: str, rows: list[dict[str, str]]) -> Path:
    path = WORK_DIR / f"{worker}_annotation.csv"
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite existing work copy: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=WORK_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                "record_id": row["record_id"],
                "platform": row["platform"],
                "post_text": row["post_text"],
                **{column: "" for column in ANNOTATION_COLUMNS},
            })
    return path


def validate_copy(path: Path, source_rows: list[dict[str, str]]) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, strict=True)
        if tuple(reader.fieldnames or ()) != WORK_COLUMNS:
            raise RuntimeError(f"Schema mismatch in {path}: {reader.fieldnames}")
        rows = list(reader)
    if len(rows) != len(source_rows):
        raise RuntimeError(f"{path} has {len(rows)} rows; expected {len(source_rows)}")
    for index, (actual, source) in enumerate(zip(rows, source_rows), start=2):
        for column in ("record_id", "platform", "post_text"):
            if actual[column] != source[column]:
                raise RuntimeError(f"{path} differs from source at CSV line {index}, field {column}")
        if any(actual[column].strip() for column in ANNOTATION_COLUMNS):
            raise RuntimeError(f"{path} has a nonblank annotation field at CSV line {index}")


def main() -> int:
    source_rows = read_source()
    if WORK_DIR.exists() and any(WORK_DIR.iterdir()):
        raise RuntimeError(f"Refusing to write into non-empty work directory: {WORK_DIR}")
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    paths = [write_copy(worker, source_rows) for worker in WORKERS]
    write_readme()
    for path in paths:
        validate_copy(path, source_rows)
    print(f"Validated source and created: {', '.join(str(path) for path in paths)}")
    print(f"Created: {README}")


if __name__ == "__main__":
    main()
