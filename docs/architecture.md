# InfraSight Architecture

## Proposed production platform

```text
Approved MPLADS public sources
        |
        v
Ingestion scheduler / manual retrieval
        |
        +--> immutable raw files, source metadata, hashes, retrieval history
        |
        v
Validation and normalization
        |
        +--> exact work-ID joins, field contracts, missing-data flags
        |
        v
PostgreSQL
  projects | costs | expenditures | source evidence | review state
        |
        +-----------------------------+
        |                             |
        v                             v
Versioned scoring service       Admin coverage analytics
  peer hierarchy                  data quality / workload / patterns
  confidence / component proof
        |
        v
FastAPI
        |
        v
Reviewer dashboard | work explorer | evidence view | verified work-site map
        |
        v
Human validation, notes, disposition, feedback
```

## Design principles

- Source evidence stays traceable from review screen to raw retrieval.
- Exact IDs drive joins; unmatched records become visible integrity conditions.
- Signals compare relevant peers and show peer count, confidence, component scores, and unavailable fields.
- Missing or inadequate data disables signal. It never becomes invented zero or unsupported delay.
- Reviewers make final decision. Platform prioritizes work, not wrongdoing.

## MVP demonstrated in repository

```text
One saved official eSAKSHI source slice
        |
        v
Raw manifest + hashes
        |
        v
Exact-ID normalization + prototype peer scoring
        |
        v
SQLite snapshot --> read-only FastAPI --> dashboard / explorer / context map / admin
```

MVP uses static SQLite and small validated slice for reliable presentation. Production architecture replaces this with expanded source coverage, scheduled snapshots, PostgreSQL, verified coordinates, and reviewer feedback records.
