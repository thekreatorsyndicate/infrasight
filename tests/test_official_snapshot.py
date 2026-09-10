import unittest

from scripts.build_live_snapshot import adapt_completed, adapt_recommended
from src.analysis.anomalies import SCORING_VERSION, load_scoring_config, score_projects
from src.processing.transform import normalize_records


class OfficialSnapshotPipelineTests(unittest.TestCase):
    def test_source_records_join_by_exact_work_id(self):
        recommended = adapt_recommended([{
            "WORK_RECOMMENDATION_DTL_ID": 101, "STATE_NAME": "Maharashtra", "IDA_NAME": "Pune",
            "WORK_CATEGORY": "Roads", "ACTIVITY_NAME": "Road repair", "RECOMMENDED_AMOUNT": "1000",
            "RECOMMENDATION_DATE": "2025-01-01", "WORK_STAGE": "Recommended",
        }])
        completed = adapt_completed([{"WORK_RECOMMENDATION_DTL_ID": 101, "ACTUAL_END_DATE": "2025-02-01"}])
        result = normalize_records(recommended, completed, [])
        self.assertEqual(result.projects.iloc[0].work_id, "101")
        self.assertEqual(str(result.projects.iloc[0].completion_date), "2025-02-01")

    def test_missing_expenditure_stays_unavailable(self):
        rows = []
        for index in range(5):
            rows.append({"workId": str(index), "state": "Maharashtra", "district": "Pune", "workCategory": "Roads",
                         "workName": f"Road {index}", "recommendedAmount": 1000 + index,
                         "recommendedDate": "2025-01-01", "workStatus": "Recommended"})
        result = normalize_records(rows, [], [])
        scores = score_projects(result.projects)
        self.assertTrue(scores.expenditure_anomaly_score.isna().all())

    def test_config_controls_version_and_minimum_peers(self):
        config = load_scoring_config()
        self.assertEqual(config["scoring_version"], "official-snapshot-v1")
        self.assertEqual(SCORING_VERSION, "official-snapshot-v1")
        self.assertEqual(config["minimum_peer_count"], 4)


if __name__ == "__main__":
    unittest.main()
