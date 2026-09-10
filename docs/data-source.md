# Data Source and MVP Validation Notes

## Platform data approach

InfraSight is designed to use approved public MPLADS sources through documented retrievals. Each platform snapshot will retain source endpoint, selected filters, retrieval time, record counts, raw response, and SHA-256 hashes. Snapshot history will make every score reproducible against source state available at time of review.

Production ingestion will expand verified source coverage and pagination before enabling production peer thresholds, expenditure signals, or geographic work-site representation.

## MVP validation source

MVP uses public [MPLADS eSAKSHI dashboard](https://mplads.mospi.gov.in/digigov/dashboard.html), retrieved using documented 18th Lok Sabha filters for Maharashtra, Gujarat, and Delhi. A bounded round-robin selection across implementing districts keeps local demo responsive while retaining source coverage notes.

Each local retrieval creates `data/raw/official_multilocation_<timestamp>/` with raw recommendation, completion, expenditure, and manifest files. Manifest records source endpoints, filter combinations, retrieval time, record counts, selection rule, and SHA-256 hashes.

## Honest boundaries demonstrated

- Selected slice returned no expenditure rows; spend component stays unavailable.
- Slice has no reliable work-site coordinates; map shows state/district context only.
- Small sample uses prototype peer minimum of four; platform target is at least 20 verified peers.
- Scores prioritize human review. They are not findings of fraud, corruption, or illegality.
