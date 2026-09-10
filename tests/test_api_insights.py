import unittest

from src.api import insights, stats


class ApiInsightTests(unittest.TestCase):
    def test_stats_reports_official_snapshot_metadata(self):
        result = stats()
        self.assertGreater(result["projects"], 0)
        self.assertEqual(result["source"]["combos"]["Maharashtra"], "21,0,0,2,7")
        self.assertTrue(result["snapshot_id"].startswith("official_multilocation_"))

    def test_insights_are_derived_from_snapshot(self):
        result = insights()
        self.assertGreater(result["scored_projects"], 0)
        self.assertEqual(result["coordinate_coverage"], 0)
        self.assertEqual(sum(location["works"] for location in result["locations"]), stats()["projects"])
        self.assertGreater(sum(category["recommended_amount"] for category in result["categories"]), 0)


if __name__ == "__main__":
    unittest.main()
