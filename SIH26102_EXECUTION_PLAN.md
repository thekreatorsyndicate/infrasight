# SIH26102 — Executable Plan and TODO

## Goal

Build reproducible MPLADS anomaly intelligence that prioritizes works for human review. It must not claim fraud, corruption, or illegality.

## Phase 0 — Data feasibility gate

- [ ] Check MPLADS portal terms, robots, rate limits, and public-data policy.
- [ ] Inspect Empowered Indian MPLADS client implementation.
- [ ] Capture official dashboard request as cURL.
- [ ] Document method, URL, headers, cookies, request body, dataset parameters, and pagination.
- [x] Reproduce exact request in Python using `requests.Session()`.
- [ ] Fetch same small sample twice.
- [x] Store fetch timestamp, parameters, response hash, and source URL. HTTP status capture remains open.

**Pass condition:** repeatable official or approved response; known access/legal constraints.

## Phase 1 — Repository and raw ingestion

- [x] Create project structure.
- [x] Add `.gitignore` for `.env`, session cookies, raw private captures, Python/Node artifacts.
- [ ] Add `.env.example`; never commit real credentials or session data.
- [ ] Build `ingestion/mplads_client.py` for sessions, timeouts, retry/backoff, pagination, and dataset retrieval only.
- [ ] Build `ingestion/fetch_data.py` for recommended, completed, and expenditure datasets.
- [x] Save immutable snapshots:

```text
data/raw/<run_id>/
├── recommended.json
├── completed.json
├── expenditure.json
└── manifest.json
```

- [ ] Fetch 100–1,000 records and prove pagination plus rerun path.

**Pass condition:** repeatable raw data retrieval.

## Phase 2 — Data audit

- [x] Build actual field dictionary from returned JSON.
- [ ] Confirm amount units, null formats, date formats, and date semantics.
- [x] Measure record counts, unique IDs, duplicate IDs, missing fields.
- [x] Measure exact `workId` join rate across datasets.
- [x] Report unmatched and duplicate records.
- [x] Do not use fallback joins unless separately documented and labeled.
- [x] Publish `reports/data_quality_<run_id>.md`.

**Pass condition:** fields, coverage, and joinability known before modeling.

## Phase 3 — Normalize and validate

- [ ] Build `ingestion/transform.py`.
- [x] Normalize projects and aggregate expenditure only by exact `workId`.
- [ ] Output `data/processed/projects.csv` and `expenditures.csv`.
- [x] Preserve suspicious values; do not silently delete them.
- [ ] Add data-integrity flags:
- [x] Duplicate work ID
- [x] Negative amount
- [x] Invalid date
- [x] Completion before recommendation
- [x] Expenditure over recommended amount
  - [ ] Missing critical field
  - [ ] Extreme amount
- [ ] Write cleaning log: raw value, normalized value, transformation reason.
- [ ] Trace one real project from raw API response to unified project row.

**Pass condition:** every normalized value traceable to raw source.

## Phase 4 — Comparable-project logic

- [ ] Define comparison hierarchy:

```text
category + district + year
→ category + state + year
→ category + region + year
→ category + national + year
```

- [ ] Require minimum peer group size; initial default: `n >= 20`.
- [x] Store peer group definition, hierarchy level, and peer count for each score.
- [x] If no valid peer group exists, mark score component unavailable; do not force a score.

**Pass condition:** every anomaly shows valid comparison context.

## Phase 5 — Explainable anomaly engine

- [x] Implement cost anomaly using actual confirmed amount field and robust statistics.
- [x] Implement expenditure anomaly relative to comparable-project utilization.
- [x] Do not flag near-100% expenditure alone.
- [x] Implement unusual completion-time anomaly from recommendation to completion date.
- [x] Never call duration an “official delay” without official expected-completion field.
- [x] Keep data-integrity flags separate from statistical anomaly scores.
- [x] Store evidence for every component.
- [x] Add `confidence_score`, `data_coverage`, `peer_count`, and `scoring_version`.
- [x] Store weights/thresholds in versioned `scoring_config_v1.json`, not code.

**Output:** `risk_scores.csv` with score, component scores, confidence, peer metadata, and evidence.

## Phase 6 — Validate scoring

- [ ] Hand-review 20–50 normal and flagged projects with a domain mentor.
- [ ] Record false-positive reasons.
- [ ] Tune only versioned score configuration.
- [ ] Preserve previous score outputs and configuration versions.
- [ ] Use product language: “Investigation Priority,” “Statistical Anomaly Signals,” “Requires Human Review.”

**Pass condition:** top flags are evidence-backed and not obvious data artifacts.

## Phase 7 — Database and backend

- [ ] Define CSV/JSON contracts before database implementation.
- [ ] Create PostgreSQL tables: `projects`, `expenditures`, `risk_scores`, `pipeline_runs`.
- [x] Store `run_id`, `source_snapshot_id`, `pipeline_version`, `scoring_version`, `generated_at`.
- [x] Build FastAPI endpoints:

```text
GET /projects
GET /projects/{work_id}
GET /projects/high-risk
GET /stats
```

- [x] Add filters after base endpoints work.

**Pass condition:** API returns score, confidence, integrity flags, and evidence.

## Phase 8 — Frontend

- [x] Build dashboard: totals, risk distribution, project explorer entry.
- [x] Build explorer: filters, sortable results, project table.
- [x] Build investigation page: score, confidence, peer group, evidence, integrity flags.
- [x] Display disclaimer on relevant pages:

> Flagged for human review. This system does not determine fraud or illegality.

**Pass condition:** evidence visible; score never appears alone.

## Phase 9 — Later only

- [ ] LLM explanation from structured evidence only.
- [ ] Duplicate or overlapping project detection.
- [ ] Agency/district systemic anomaly analysis.
- [ ] Map only if reliable coordinates exist.
- [ ] Advanced ML only after statistical baseline validation.

## First milestone

- [x] Take one real MPLADS work through full chain:

```text
Official API
→ raw JSON
→ workId join
→ unified project
→ anomaly signals
→ risk score
→ evidence
```

## Team split

| Owner | Scope | First deliverable |
|---|---|---|
| Data/API | API, sessions, extraction, raw snapshots, cleaning | `projects.csv` |
| Analytics | Peer groups, signals, scoring, evidence | `risk_scores.csv` |
| Backend | PostgreSQL, FastAPI, contracts | Evidence API |
| Frontend | Dashboard, explorer, investigation view | Three screens |

## MVP definition of done

- [ ] Official or approved source is reproducibly fetched.
- [x] Raw snapshots and manifests are preserved.
- [x] Field dictionary and join audit exist.
- [x] Suspicious data is preserved and flagged.
- [x] Scores include evidence, peer count, confidence, and version.
- [x] One real work is traced end to end.
- [x] Dashboard exposes evidence.
- [x] No copy claims fraud, corruption, or illegality.
