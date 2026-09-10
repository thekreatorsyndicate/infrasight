"""Small, traceable normalization layer for the prototype dataset."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


PROJECT_COLUMNS = [
    "work_id", "state", "district", "work_category", "work_name",
    "recommended_amount", "recommended_date", "completion_date", "work_status",
]


@dataclass
class TransformResult:
    projects: pd.DataFrame
    expenditures: pd.DataFrame
    cleaning_log: list[dict[str, Any]]


def _date(value: Any, field: str, work_id: str, log: list[dict[str, Any]]) -> date | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    parsed = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce") if len(text) == 10 and text[4:5] == "-" else pd.to_datetime(text, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        log.append({"work_id": work_id, "field": field, "raw_value": value,
                    "normalized_value": None, "reason": "invalid_date_preserved_as_null"})
        return None
    return parsed.date()


def normalize_records(recommended: list[dict[str, Any]], completed: list[dict[str, Any]],
                      expenditure: list[dict[str, Any]]) -> TransformResult:
    """Join only exact workId values. Keep integrity problems as flags, never discard."""
    log: list[dict[str, Any]] = []
    has_expenditure_data = bool(expenditure)
    completed_by_id = {str(row.get("workId")).strip(): row for row in completed if row.get("workId")}
    expenditure_by_id: dict[str, list[dict[str, Any]]] = {}
    for row in expenditure:
        work_id = str(row.get("workId", "")).strip()
        if work_id:
            expenditure_by_id.setdefault(work_id, []).append(row)

    duplicate_ids = pd.Series([str(row.get("workId", "")).strip() for row in recommended]).value_counts()
    project_rows: list[dict[str, Any]] = []
    expenditure_rows: list[dict[str, Any]] = []
    for raw in recommended:
        work_id = str(raw.get("workId", "")).strip()
        if not work_id:
            log.append({"work_id": None, "field": "workId", "raw_value": raw.get("workId"),
                        "normalized_value": None, "reason": "missing_work_id_row_excluded"})
            continue
        completed_row = completed_by_id.get(work_id, {})
        amount = pd.to_numeric(raw.get("recommendedAmount"), errors="coerce")
        amount = None if pd.isna(amount) else float(amount)
        flags: list[str] = []
        if duplicate_ids.get(work_id, 0) > 1:
            flags.append("duplicate_work_id")
        if amount is None:
            flags.append("missing_recommended_amount")
        elif amount < 0:
            flags.append("negative_recommended_amount")
        rec_date = _date(raw.get("recommendedDate"), "recommendedDate", work_id, log)
        completion_date = _date(completed_row.get("completionDate"), "completionDate", work_id, log)
        if raw.get("recommendedDate") and rec_date is None:
            flags.append("invalid_recommended_date")
        if completed_row.get("completionDate") and completion_date is None:
            flags.append("invalid_completion_date")
        if rec_date and completion_date and completion_date < rec_date:
            flags.append("completion_before_recommendation")
        rows = expenditure_by_id.get(work_id, [])
        spend = 0.0
        for item in rows:
            value = pd.to_numeric(item.get("expenditureAmount"), errors="coerce")
            if pd.isna(value):
                flags.append("invalid_expenditure_amount")
                continue
            value = float(value)
            if value < 0:
                flags.append("negative_expenditure")
            spend += value
            expenditure_rows.append({"work_id": work_id, "expenditure_amount": value,
                                     "expenditure_date": _date(item.get("expenditureDate"), "expenditureDate", work_id, log)})
        if amount is not None and amount > 0 and spend > amount:
            flags.append("expenditure_over_recommended_amount")
        project_rows.append({
            "work_id": work_id, "state": raw.get("state"), "district": raw.get("district"),
            "work_category": raw.get("workCategory"), "work_name": raw.get("workName"),
            "recommended_amount": amount, "recommended_date": rec_date,
            "completion_date": completion_date, "work_status": completed_row.get("workStatus") or raw.get("workStatus"),
            "total_expenditure": spend, "has_expenditure_data": has_expenditure_data,
            "integrity_flags": sorted(set(flags)),
        })
    return TransformResult(
        pd.DataFrame(project_rows),
        pd.DataFrame(expenditure_rows, columns=["work_id", "expenditure_amount", "expenditure_date"]),
        log,
    )
