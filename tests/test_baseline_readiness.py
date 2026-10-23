import unittest
from src.baseline_readiness import no_group_leakage, valid_label, assess

class BaselineReadinessTests(unittest.TestCase):
    def test_label_validation(self):
        self.assertTrue(valid_label("none_other"))
        self.assertTrue(valid_label("distress_negative_affect|self_harm_related"))
        self.assertFalse(valid_label("none_other|self_harm_related"))
        self.assertFalse(valid_label("legacy_label"))

    def test_group_cannot_cross_splits(self):
        self.assertTrue(no_group_leakage({"a":"train", "b":"train"}, {"a":"g1", "b":"g1"}))
        self.assertFalse(no_group_leakage({"a":"train", "b":"test"}, {"a":"g1", "b":"g1"}))

    def test_readiness_is_deterministic_and_unlabeled_rows_remain_unlabeled(self):
        rows = [{"reviewed_join_status":"matched_validated", "reviewed_label":"none_other", "platform":"youtube", "stable_record_key":"youtube:a"}, {"reviewed_join_status":"unreviewed", "reviewed_label":"", "platform":"reddit", "stable_record_key":"reddit:b"}]
        self.assertEqual(assess(rows), assess(rows))
        self.assertEqual(assess(rows)["unlabeled_rows"], 1)

if __name__ == "__main__": unittest.main()
