"""Build deterministic, local-only demo data and scores for a presentation."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.anomalies import SCORING_VERSION, score_projects
from src.database.connection import init_database, session_scope
from src.database.models import Expenditure, PipelineRun, Project, RiskScore
from src.processing.transform import normalize_records


RUN_ID = "demo_2026_v1"


def demo_records():
    recommended, completed, expenditure = [], [], []
    start = date(2024, 1, 1)
    amounts = [940000, 980000, 1010000, 970000, 1030000, 990000, 1020000, 960000, 1000000, 1050000, 930000, 1080000]
    for index, amount in enumerate(amounts, start=1):
        work_id = f"ROAD-{index:03d}"
        recommended.append({"workId": work_id, "state": "Maharashtra", "district": "Pune", "workCategory": "Roads",
                            "workName": f"Village road improvement {index}", "recommendedAmount": amount,
                            "recommendedDate": (start + timedelta(days=index * 4)).isoformat()})
        completed.append({"workId": work_id, "completionDate": (start + timedelta(days=118 + index * 3)).isoformat(), "workStatus": "Completed"})
        expenditure.append({"workId": work_id, "expenditureAmount": round(amount * (0.87 + (index % 4) * 0.02)),
                            "expenditureDate": (start + timedelta(days=100)).isoformat()})
    # Purposeful demo outlier. Evidence tells viewer why it ranks, not a claim of wrongdoing.
    recommended.append({"workId": "ROAD-OUTLIER", "state": "Maharashtra", "district": "Pune", "workCategory": "Roads",
                        "workName": "Hill access road resurfacing", "recommendedAmount": 3200000, "recommendedDate": "2024-02-01"})
    completed.append({"workId": "ROAD-OUTLIER", "completionDate": "2025-08-01", "workStatus": "Completed"})
    expenditure.append({"workId": "ROAD-OUTLIER", "expenditureAmount": 3550000, "expenditureDate": "2025-07-20"})
    return recommended, completed, expenditure


def main() -> None:
    recommended, completed, expenditure = demo_records()
    result = normalize_records(recommended, completed, expenditure)
    scores = score_projects(result.projects)

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    result.projects.to_csv(output_dir / "demo_projects.csv", index=False)
    result.expenditures.to_csv(output_dir / "demo_expenditures.csv", index=False)
    scores.to_csv(output_dir / "demo_risk_scores.csv", index=False)
    (output_dir / "demo_cleaning_log.json").write_text(json.dumps(result.cleaning_log, indent=2, default=str))

    demo_db = Path("data/demo_infrasight.db")
    if demo_db.exists():
        demo_db.unlink()
    init_database("sqlite:///data/demo_infrasight.db")
    score_by_work_id = scores.set_index("work_id").to_dict("index")
    with session_scope() as session:
        session.add(PipelineRun(run_id=RUN_ID, pipeline_version="demo-v1", scoring_version=SCORING_VERSION,
                                source_snapshot_id="synthetic-demo-v1", status="completed"))
        for _, row in result.projects.iterrows():
            project = Project(run_id=RUN_ID, work_id=row.work_id, state=row.state, district=row.district,
                              work_category=row.work_category, work_name=row.work_name,
                              recommended_amount=row.recommended_amount, recommended_date=row.recommended_date,
                              completion_date=row.completion_date, work_status=row.work_status,
                              raw_data={"demo": True})
            session.add(project)
            session.flush()
            for _, spend in result.expenditures[result.expenditures.work_id == row.work_id].iterrows():
                session.add(Expenditure(run_id=RUN_ID, project_id=project.id, work_id=row.work_id,
                                        expenditure_amount=spend.expenditure_amount, expenditure_date=spend.expenditure_date,
                                        expenditure_year=spend.expenditure_date.year if spend.expenditure_date else None,
                                        raw_data={"demo": True}))
            score = score_by_work_id[row.work_id]
            session.add(RiskScore(run_id=RUN_ID, project_id=project.id, work_id=row.work_id,
                                  cost_anomaly_score=score["cost_anomaly_score"], expenditure_anomaly_score=score["expenditure_anomaly_score"],
                                  duration_anomaly_score=score["duration_anomaly_score"], composite_score=score["composite_score"],
                                  confidence_score=score["confidence_score"], data_coverage=score["data_coverage"], peer_count=score["peer_count"],
                                  scoring_version=SCORING_VERSION, peer_group_level=score["peer_group_level"],
                                  peer_group_definition=score["peer_group_definition"], integrity_flags=score["integrity_flags"], evidence=score["evidence"]))
    print("Demo ready: data/demo_infrasight.db")
    print("CSV output: data/processed/demo_{projects,expenditures,risk_scores}.csv")


if __name__ == "__main__":
    main()
