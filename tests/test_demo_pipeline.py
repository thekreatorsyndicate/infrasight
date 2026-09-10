import unittest

from scripts.build_demo import demo_records
from src.analysis.anomalies import score_projects
from src.processing.transform import normalize_records


class DemoPipelineTests(unittest.TestCase):
    def test_outlier_is_ranked_and_explained(self):
        result = normalize_records(*demo_records())
        scores = score_projects(result.projects).set_index("work_id")
        outlier = scores.loc["ROAD-OUTLIER"]
        self.assertGreaterEqual(outlier.composite_score, 90)
        self.assertEqual(outlier.peer_group_level, "district")
        self.assertIn("expenditure_over_recommended_amount", outlier.integrity_flags)
        self.assertEqual(outlier.evidence["disclaimer"], "Flagged for human review. This system does not determine fraud or illegality.")


if __name__ == "__main__":
    unittest.main()
