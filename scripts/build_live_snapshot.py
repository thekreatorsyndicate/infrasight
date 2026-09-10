"""Create one local, static dashboard database from official public MPLADS data."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis.anomalies import SCORING_VERSION, load_scoring_config, score_projects
from src.database.connection import init_database, session_scope
from src.database.models import Expenditure, PipelineRun, Project, RiskScore
from src.ingestion.mplads_api import MPLADSClient, REPORT_URL
from src.processing.data_audit import run_data_audit
from src.processing.transform import normalize_records


COMBO = "21,245,0,2,7"  # Maharashtra / Raver / Lok Sabha / 18th Lok Sabha
SOURCE_LABEL = "Official MPLADS eSAKSHI public dashboard — Raver, Maharashtra; 18th Lok Sabha"
DATASETS = ("Works Recommended", "Works Completed", "Expenditure Incurred")


def unpack(response: dict, expected_key: str) -> list[dict]:
    """Dashboard returns list data JSON-encoded under a display-key."""
    for value in response.values():
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, list):
                    return decoded
            except json.JSONDecodeError:
                pass
    return []


def adapt_recommended(rows: list[dict]) -> list[dict]:
    return [{"workId": str(row.get("WORK_RECOMMENDATION_DTL_ID", "")), "state": row.get("STATE_NAME"),
             "district": row.get("IDA_NAME"), "workCategory": row.get("WORK_CATEGORY"),
             "workName": row.get("ACTIVITY_NAME"), "recommendedAmount": row.get("RECOMMENDED_AMOUNT"),
             "recommendedDate": row.get("RECOMMENDATION_DATE"), "workStatus": row.get("WORK_STAGE")} for row in rows]


def adapt_completed(rows: list[dict]) -> list[dict]:
    return [{"workId": str(row.get("WORK_RECOMMENDATION_DTL_ID", "")), "completionDate": row.get("ACTUAL_END_DATE"),
             "workStatus": "Completed"} for row in rows]


def store(result, scores, run_id: str, snapshot_id: str) -> None:
    database = Path("data/live_infrasight.db")
    if database.exists():
        database.unlink()
    init_database("sqlite:///data/live_infrasight.db")
    by_work_id = scores.set_index("work_id").to_dict("index")
    with session_scope() as session:
        session.add(PipelineRun(run_id=run_id, pipeline_version="official-snapshot-v1", scoring_version=SCORING_VERSION,
                                source_snapshot_id=snapshot_id, status="completed",
                                run_metadata={"source": SOURCE_LABEL, "combo": COMBO}))
        for _, row in result.projects.iterrows():
            project = Project(run_id=run_id, work_id=row.work_id, state=row.state, district=row.district,
                              work_category=row.work_category, work_name=row.work_name, recommended_amount=row.recommended_amount,
                              recommended_date=row.recommended_date, completion_date=row.completion_date, work_status=row.work_status,
                              raw_data={"source_snapshot_id": snapshot_id})
            session.add(project); session.flush()
            for _, spend in result.expenditures[result.expenditures.work_id == row.work_id].iterrows():
                session.add(Expenditure(run_id=run_id, project_id=project.id, work_id=row.work_id,
                    expenditure_amount=spend.expenditure_amount, expenditure_date=spend.expenditure_date,
                    expenditure_year=spend.expenditure_date.year if spend.expenditure_date else None, raw_data={"source_snapshot_id": snapshot_id}))
            score = by_work_id[row.work_id]
            session.add(RiskScore(run_id=run_id, project_id=project.id, work_id=row.work_id,
                cost_anomaly_score=score["cost_anomaly_score"], expenditure_anomaly_score=score["expenditure_anomaly_score"],
                duration_anomaly_score=score["duration_anomaly_score"], composite_score=score["composite_score"],
                confidence_score=score["confidence_score"], data_coverage=score["data_coverage"], peer_count=score["peer_count"],
                scoring_version=SCORING_VERSION, peer_group_level=score["peer_group_level"],
                peer_group_definition=score["peer_group_definition"], integrity_flags=score["integrity_flags"], evidence=score["evidence"]))


def main() -> None:
    client = MPLADSClient(COMBO); client.initialize_session()
    # Client extracts dashboard's JSON-encoded list response. Preserve this exact
    # retrieved list as the immutable local raw snapshot.
    raw = {name: client.fetch_report(name) for name in DATASETS}
    received_at = datetime.now(timezone.utc)
    snapshot_id = f"official_raver_{received_at.strftime('%Y%m%d_%H%M%S')}"
    raw_dir = Path("data/raw") / snapshot_id; raw_dir.mkdir(parents=True, exist_ok=True)
    for name, records in raw.items():
        (raw_dir / f"{name.lower().replace(' ', '_')}.json").write_text(json.dumps(records, indent=2))
    manifest = {"snapshot_id": snapshot_id, "retrieved_at": received_at.isoformat(), "source_url": REPORT_URL,
                "source": SOURCE_LABEL, "combo": COMBO, "counts": {key: len(value) for key, value in raw.items()},
                "sha256": {key: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest() for key, value in raw.items()}}
    (raw_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    result = normalize_records(adapt_recommended(raw["Works Recommended"]), adapt_completed(raw["Works Completed"]), [])
    scores = score_projects(result.projects, load_scoring_config())
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    result.projects.to_csv("data/processed/live_projects.csv", index=False)
    scores.to_csv("data/processed/live_risk_scores.csv", index=False)
    run_data_audit(snapshot_id, {
        "recommended": adapt_recommended(raw["Works Recommended"]),
        "completed": adapt_completed(raw["Works Completed"]),
        "expenditure": [],
    })
    store(result, scores, snapshot_id, snapshot_id)
    print(f"Official snapshot ready: {snapshot_id}; projects={len(result.projects)}; completed={len(raw['Works Completed'])}; expenditure={len(raw['Expenditure Incurred'])}")


if __name__ == "__main__":
    main()
