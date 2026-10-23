import csv
import tempfile
import unittest
from pathlib import Path

from src.phase1_pipeline import normalize_text, synthetic_status, run

class Phase1Tests(unittest.TestCase):
    def test_normalization(self):
        self.assertEqual(normalize_text("  A\n B  "), "a b")
        self.assertEqual(normalize_text("é"), "é")

    def test_synthetic_flags(self):
        self.assertEqual(synthetic_status({"is_synthetic": "TRUE", "parent_record_id": "", "aug_method": "original"}), "synthetic_or_augmented")
        self.assertEqual(synthetic_status({"is_synthetic": "FALSE", "parent_record_id": "", "aug_method": "original"}), "original_or_unspecified")
        self.assertEqual(synthetic_status({"is_synthetic": "FALSE", "parent_record_id": "abc", "aug_method": "original"}), "synthetic_or_augmented")

    def test_full_pipeline(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / "derived"
            quality = run(output_dir=out)
            self.assertEqual(quality["row_count"], 4739)
            self.assertEqual(quality["reviewed_rows_available"], 60)
            self.assertEqual(quality["reviewed_rows_joined"], 60)
            self.assertEqual(quality["unreviewed_rows"], 4679)
            with (out / "canonical_corpus.csv").open(encoding="utf-8", newline="") as f:
                self.assertEqual(sum(1 for _ in csv.DictReader(f)), 4739)
            self.assertTrue((out / "quality_summary.json").exists())

if __name__ == "__main__": unittest.main()
