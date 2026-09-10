"""Explainable, configuration-driven anomaly scoring for official snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


CONFIG_PATH = Path(__file__).with_name("scoring_config_v1.json")


def load_scoring_config() -> dict[str, Any]:
    """Load versioned thresholds and weights; never embed policy in score code."""
    return json.loads(CONFIG_PATH.read_text())


SCORING_VERSION = load_scoring_config()["scoring_version"]


def _robust_score(value: float, values: pd.Series, denominator: float) -> float | None:
    values = pd.to_numeric(values, errors="coerce").dropna()
    if len(values) < 2 or pd.isna(value):
        return None
    median = float(values.median())
    mad = float((values - median).abs().median())
    if mad == 0:
        return 0.0 if value == median else 1.0
    return min(1.0, abs(value - median) / (denominator * 1.4826 * mad))


def _peer_group(row: pd.Series, projects: pd.DataFrame, minimum_peers: int) -> tuple[pd.DataFrame, str, dict[str, Any]]:
    year = row["recommended_date"].year if pd.notna(row["recommended_date"]) else None
    candidates = [
        ("district", (projects.work_category == row.work_category) & (projects.district == row.district)),
        ("state", (projects.work_category == row.work_category) & (projects.state == row.state)),
        ("national", projects.work_category == row.work_category),
    ]
    if year:
        candidates = [(level, mask & (projects.recommended_date.map(lambda d: d.year if pd.notna(d) else None) == year)) for level, mask in candidates]
    for level, mask in candidates:
        peers = projects[mask & (projects.work_id != row.work_id)]
        if len(peers) >= minimum_peers:
            return peers, level, {"category": row.work_category, "year": year, "level": level}
    return projects.iloc[0:0], "unavailable", {"category": row.work_category, "year": year, "level": "unavailable"}


def score_projects(projects: pd.DataFrame, config: dict[str, Any] | None = None) -> pd.DataFrame:
    """Return independent signals plus evidence. Scores mean review priority, not wrongdoing."""
    config = config or load_scoring_config()
    minimum_peers = int(config["minimum_peer_count"])
    denominator = float(config["robust_z_denominator"])
    weights = config["weights"]
    rows: list[dict[str, Any]] = []
    for _, project in projects.iterrows():
        peers, level, definition = _peer_group(project, projects, minimum_peers)
        cost = _robust_score(project.recommended_amount, peers.recommended_amount, denominator) if len(peers) else None
        has_expenditure_data = bool(project.get("has_expenditure_data", True))
        utilization = project.total_expenditure / project.recommended_amount if has_expenditure_data and project.recommended_amount and project.recommended_amount > 0 else np.nan
        peer_utilization = peers.apply(lambda p: p.total_expenditure / p.recommended_amount if p.get("has_expenditure_data", True) and p.recommended_amount and p.recommended_amount > 0 else np.nan, axis=1) if len(peers) else pd.Series(dtype=float)
        spend = _robust_score(utilization, peer_utilization, denominator) if has_expenditure_data and len(peers) else None
        duration = (project.completion_date - project.recommended_date).days if pd.notna(project.completion_date) and pd.notna(project.recommended_date) else np.nan
        peer_durations = peers.apply(lambda p: (p.completion_date - p.recommended_date).days if pd.notna(p.completion_date) and pd.notna(p.recommended_date) else np.nan, axis=1) if len(peers) else pd.Series(dtype=float)
        duration_score = _robust_score(duration, peer_durations, denominator) if len(peers) else None
        components = {"cost": cost, "expenditure": spend, "duration": duration_score}
        available = {name: value for name, value in components.items() if value is not None}
        available_weight = sum(weights[name] for name in available)
        composite = round(sum(available[name] * weights[name] for name in available) / available_weight * 100, 1) if available_weight else None
        coverage = round(len(available) / len(components), 2)
        confidence = round(min(1.0, len(peers) / int(config["confidence_full_peer_count"])) * coverage, 2)
        evidence = {
            "disclaimer": "Flagged for human review. This system does not determine fraud or illegality.",
            "cost": {"score": cost, "project_amount": project.recommended_amount,
                     "peer_median": float(peers.recommended_amount.median()) if len(peers) else None},
            "expenditure": {"score": spend, "available": has_expenditure_data,
                            "utilization": None if pd.isna(utilization) else round(float(utilization), 3),
                            "peer_median": float(peer_utilization.median()) if len(peer_utilization.dropna()) else None},
            "duration": {"score": duration_score, "days": None if pd.isna(duration) else int(duration),
                         "peer_median_days": float(peer_durations.median()) if len(peer_durations.dropna()) else None},
        }
        rows.append({"work_id": project.work_id, "cost_anomaly_score": cost, "expenditure_anomaly_score": spend,
                     "duration_anomaly_score": duration_score, "composite_score": composite,
                     "confidence_score": confidence, "data_coverage": coverage, "peer_count": len(peers),
                     "peer_group_level": level, "peer_group_definition": definition,
                     "integrity_flags": project.integrity_flags, "evidence": evidence,
                     "scoring_version": config["scoring_version"]})
    return pd.DataFrame(rows)
