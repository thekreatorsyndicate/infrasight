# InfraSight MVP

InfraSight is a local, read-only prototype for reviewing statistical anomaly signals in MPLADS works. It ranks records for human review; it does not determine fraud, corruption, or illegality.

## Current data

Dashboard uses a static snapshot retrieved from official public [MPLADS eSAKSHI dashboard](https://mplads.mospi.gov.in/digigov/dashboard.html): Raver constituency, Maharashtra, Lok Sabha, 18th Lok Sabha.

- 10 recommended works retrieved
- 4 completed works retrieved
- 0 expenditure records returned for this filter

The raw response, timestamp, request filter, source URL, record counts, and SHA-256 hashes live in `data/raw/official_raver_<timestamp>/manifest.json`. Data is static after retrieval; app does not update database or call API at runtime.

Each snapshot also produces `reports/data_quality_official_raver_<timestamp>.md`, with field dictionary and exact `workId` join audit.

## Run

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/build_live_snapshot.py
.venv/bin/python -m uvicorn src.api:app --reload
```

Open [dashboard](http://127.0.0.1:8000). API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

`build_live_snapshot.py` makes one new official snapshot and replaces only local `data/live_infrasight.db`. Do not run it during presentation unless you deliberately want a new dataset.

## Dashboard

- Ranked project queue with priority threshold filter
- Inspectable cost, duration, peer-count, confidence, and integrity evidence
- Explicit unavailable signal when source dataset has no field/data, rather than fake data
- Keyboard-selectable table rows and reduced-motion support

## Scoring

1. Exact `workId` joins recommended and completed records.
2. Integrity flags preserved: negative values, invalid dates, completion-before-recommendation, overspend, duplicate ID.
3. Cost, spend utilization, completion duration compare with category + district + year peers, with state then national fallback. This prototype requires at least four peers.
4. Median/MAD robust deviation creates separate component signals and composite investigation priority. Weights, peer minimum, and version are in [`src/analysis/scoring_config_v1.json`](src/analysis/scoring_config_v1.json). If peer context or a source field is unavailable, component stays unavailable.

## API

- `GET /projects`
- `GET /projects/{work_id}`
- `GET /projects/high-risk?min_score=50`
- `GET /stats` — project count, snapshot metadata, source information

## Local artifacts

- `data/live_infrasight.db`
- `data/raw/official_raver_<timestamp>/`
- `data/processed/live_projects.csv`
- `data/processed/live_risk_scores.csv`

`scripts/build_demo.py` remains only as a deterministic development fixture; dashboard defaults to official snapshot database.
