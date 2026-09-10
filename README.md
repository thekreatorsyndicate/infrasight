# InfraSight — MPLADS Investigation Priority Platform

> Proposed decision-support platform. This repository contains MVP proof of core data, scoring, and investigation flows.

> Flags guide human review. They never determine fraud, corruption, or illegality.

## 1. Project information

| Field | Detail |
| --- | --- |
| Project title | InfraSight — Explainable MPLADS Investigation Priority Platform |
| PS ID | SIH26102 |
| PS title | MPLADS works anomaly intelligence and review prioritisation |
| Category | Software |
| Theme | Governance and public-data intelligence |

## 2. Problem

Public-work records are hard to review at scale. Data often sits across reports, costs lack meaningful comparison groups, and incomplete source coverage can create misleading conclusions. Review teams need a traceable way to decide which records merit attention first.

## 3. Proposed platform

InfraSight is planned as end-to-end MPLADS investigation-priority system. It will ingest approved public-source snapshots, retain raw evidence, normalize and audit records, compare each work with appropriate peers, and give reviewers explainable investigation leads.

Platform flow:

```text
Official public sources
        |
        v
Scheduled/manual snapshots + immutable raw evidence
        |
        v
Validation, exact-ID joins, normalized project/expenditure records
        |
        v
Peer-aware anomaly scoring + confidence + evidence
        |
        v
Reviewer workspace / admin insights / geographic context
        |
        v
Human validation and feedback loop
```

### Planned capabilities

- Reproducible public-data ingestion with pagination, source metadata, raw files, hashes, and refresh history
- Exact work-ID joins, data-quality checks, and visible missing-data states
- Hierarchical peer groups: category + district + year, with broader fallbacks only when needed
- Cost, expenditure-utilisation, and duration signals, each tied to source fields and peer evidence
- Production scoring only where peer support is adequate (target: `n >= 20`), with score/config versioning
- Investigation workspace with filters, record evidence, review status, notes, and exportable case context
- Admin view for coverage, category/location patterns, data quality, and review workload
- Geographic work map only after reliable work-site coordinates are available
- Satellite-imagery comparison, where lawful imagery and verified work-site coordinates are available, so human reviewers can compare visible site progress with reported records
- Deployment path using FastAPI services, PostgreSQL, background ingestion jobs, and role-aware access controls

## 4. MVP proof in this repository

Current build proves platform core without pretending MVP limits are final product limits.

- Saved official MPLADS eSAKSHI multi-location validation slice: Maharashtra, Gujarat, and Delhi; Lok Sabha, 18th Lok Sabha
- Raw manifest with source metadata and SHA-256 hashes
- Exact `workId` normalization and join-integrity flags
- Robust median/MAD peer scoring with versioned config and evidence panel
- Dashboard, explorer, location context, and admin insight views
- Read-only FastAPI + SQLite demo store, stable for judging

Current validation slice uses up to 48 official recommended-work records per selected state across Maharashtra, Gujarat, and Delhi implementing districts. Spend signal stays unavailable when source rows are absent; map stays contextual because source slice has no reliable work-site coordinates. Small sample uses prototype peer minimum of four. Full platform will use expanded verified coverage and production peer threshold.

See [data source and MVP validation notes](docs/data-source.md).

## 5. Technology and deployment path

| Layer | MVP demonstration | Planned platform |
| --- | --- | --- |
| Frontend | HTML, CSS, JavaScript | Responsive reviewer/admin application |
| API | Python, FastAPI, Uvicorn | FastAPI services with role-aware access |
| Processing | Pandas, NumPy | Validated ingestion and scheduled processing workers |
| Storage | Read-only SQLite snapshot | PostgreSQL, snapshot history, review records |
| Source handling | One saved official eSAKSHI slice | Approved source coverage, pagination, refresh audit trail |
| Map | State/district context | Work-site map after coordinate verification |

## 6. Architecture

See [full architecture](docs/architecture.md).

```text
Approved public data sources
        |
        v
Ingestion service --> raw snapshot store + manifest
        |
        v
Validation / normalization / exact-ID audit
        |
        v
PostgreSQL project, expenditure, evidence, and review data
        |
        +--> versioned scoring service --> priority evidence
        |
        v
FastAPI --> reviewer dashboard / explorer / admin / verified map
```

MVP path tested here: saved official snapshot → SQLite → FastAPI → dashboard views.

## 7. Repository structure

```text
infrasight/
├── README.md
├── SUBMISSION_GUIDE.md
├── submission/              # PPT and demo-link guidance
├── src/                     # API, storage, scoring, static frontend
├── scripts/                 # snapshot and demo builders
├── docs/                    # architecture and data notes
├── assets/screenshots/      # final reviewer-facing screenshots
├── tests/
├── requirements.txt
└── data/                    # ignored local snapshots/databases
```

## 8. Screenshots

Add final reviewer-facing captures under [assets/screenshots/](assets/screenshots/README.md). Screens should demonstrate proposed platform story while labeling shown build as MVP proof.

## 9. Installation

```bash
git clone <YOUR_PUBLIC_REPOSITORY_URL>
cd infrasight
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Live MVP deployment

[Open InfraSight MVP](https://infrasight-ligs.onrender.com/)

## 10. Run MVP

Build or refresh saved source slice only when intentionally retrieving new data:

```bash
.venv/bin/python scripts/build_live_snapshot.py
.venv/bin/python -m uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000`. API docs: `http://127.0.0.1:8000/docs`.

For demo, use already-built local snapshot and start only Uvicorn. **Fetch snapshot entries** reloads saved local entries; it does not access portal or update database.

## 11. Team members and roles

Replace before submission.

| Member | Role |
| --- | --- |
| `Swastik Pal` | Reviewer workflow, Data/API and source-ingestion design |
| `Lavanya` | Frontend, communication, and presentation |
| `Sambhav Jain` | Frontend, communication, and presentation |
| `Aryaman Jain` | Backend, storage, and reviewer workflow |
| `Avyam Singhal` | Backend, storage, and reviewer workflow |


## 12. Presentation and demo

- [Presentation framing and final-link placeholder](submission/PRESENTATION.md)
- [Demo-video flow and public-link placeholder](submission/DEMO.md)
