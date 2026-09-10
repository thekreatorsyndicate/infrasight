"""Read-only API for static prototype database."""

from __future__ import annotations

from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.database.connection import get_session
from src.database.models import PipelineRun, Project, RiskScore


app = FastAPI(title="InfraSight MVP API", version="0.1.0")
DISCLAIMER = "Flagged for human review. This system does not determine fraud or illegality."
STATIC_DIR = Path(__file__).with_name("static")
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


def serialize(project: Project) -> dict:
    score = project.risk_score
    return {"work_id": project.work_id, "work_name": project.work_name, "state": project.state,
            "district": project.district, "category": project.work_category,
            "recommended_amount": project.recommended_amount, "status": project.work_status,
            "investigation_priority": score.composite_score if score else None,
            "confidence_score": score.confidence_score if score else None,
            "peer_count": score.peer_count if score else None,
            "peer_group_level": score.peer_group_level if score else None,
            "integrity_flags": score.integrity_flags if score else [], "evidence": score.evidence if score else {},
            "disclaimer": DISCLAIMER}


def query_projects(session):
    return session.execute(select(Project).options(joinedload(Project.risk_score))).scalars()


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/projects")
def projects(limit: int = Query(default=250, ge=1, le=500)):
    with get_session() as session:
        rows = query_projects(session).all()
        rows.sort(key=lambda project: project.risk_score.composite_score if project.risk_score and project.risk_score.composite_score is not None else -1, reverse=True)
        return {"items": [serialize(row) for row in rows[:limit]], "count": len(rows), "disclaimer": DISCLAIMER}


@app.get("/projects/high-risk")
def high_risk(min_score: float = Query(default=50, ge=0, le=100)):
    with get_session() as session:
        rows = session.execute(select(Project).join(RiskScore).options(joinedload(Project.risk_score)).where(RiskScore.composite_score >= min_score).order_by(RiskScore.composite_score.desc())).scalars().all()
        return {"items": [serialize(row) for row in rows], "disclaimer": DISCLAIMER}


@app.get("/projects/{work_id}")
def project(work_id: str):
    with get_session() as session:
        row = session.execute(select(Project).options(joinedload(Project.risk_score)).where(Project.work_id == work_id)).scalar_one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return serialize(row)


@app.get("/stats")
def stats():
    with get_session() as session:
        total = session.scalar(select(func.count(Project.id))) or 0
        flagged = session.scalar(select(func.count(RiskScore.id)).where(RiskScore.composite_score >= 50)) or 0
        run = session.execute(select(PipelineRun).order_by(PipelineRun.started_at.desc())).scalars().first()
        return {"projects": total, "investigation_priority_50_plus": flagged, "source": run.run_metadata if run else None,
                "snapshot_id": run.source_snapshot_id if run else None, "disclaimer": DISCLAIMER}


@app.get("/insights")
def insights():
    """Small, read-only aggregates for dashboard map and administrator views."""
    with get_session() as session:
        rows = query_projects(session).all()
        categories: dict[str, dict] = {}
        locations: dict[tuple[str | None, str | None], int] = {}
        states: dict[str | None, int] = {}
        scored = 0
        unavailable_expenditure = 0
        for project in rows:
            score = project.risk_score
            category = project.work_category or "Unclassified"
            bucket = categories.setdefault(category, {"category": category, "works": 0, "recommended_amount": 0, "priority_50_plus": 0})
            bucket["works"] += 1
            bucket["recommended_amount"] += project.recommended_amount or 0
            if score and score.composite_score is not None:
                scored += 1
                if score.composite_score >= 50:
                    bucket["priority_50_plus"] += 1
                if not score.evidence.get("expenditure", {}).get("available", True):
                    unavailable_expenditure += 1
            location = (project.state, project.district)
            locations[location] = locations.get(location, 0) + 1
            states[project.state] = states.get(project.state, 0) + 1
        return {
            "categories": sorted(categories.values(), key=lambda item: item["works"], reverse=True),
            "locations": [{"state": state, "district": district, "works": works} for (state, district), works in locations.items()],
            "state_coverage": [{"state": state, "works": works} for state, works in sorted(states.items(), key=lambda item: item[1], reverse=True)],
            "scored_projects": scored,
            "unavailable_expenditure_signals": unavailable_expenditure,
            "coordinate_coverage": 0,
            "map_embed_url": "https://www.google.com/maps?q=India&z=5&output=embed",
            "map_note": "Map shows multi-state source context. Records provide state and implementing-district fields, not verified work-site coordinates.",
        }
