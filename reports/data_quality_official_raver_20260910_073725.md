# Data Quality Report — Run official_raver_20260910_073725

Generated: 2026-09-10T07:37:25.175517Z

## Dataset: recommended

- **Records**: 11
- **Columns**: 8

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 11
- Samples: 140096, 175514, 227843

#### state
- Type: str
- Nulls: 1 (9.1%)
- Unique: 1
- Samples: Maharashtra, Maharashtra, Maharashtra

#### district
- Type: str
- Nulls: 1 (9.1%)
- Unique: 1
- Samples: JALGAON(DISTRICT COLLECTOR JALGAON_IDA), JALGAON(DISTRICT COLLECTOR JALGAON_IDA), JALGAON(DISTRICT COLLECTOR JALGAON_IDA)

#### workCategory
- Type: str
- Nulls: 1 (9.1%)
- Unique: 2
- Samples: Normal/Others, Normal/Others, Trust and Society

#### workName
- Type: str
- Nulls: 1 (9.1%)
- Unique: 10
- Samples: WS/MP691/2024-2025/140096-Fitting of Sitting RCC Benches in Public Places, WS/MP691/2025-2026/175514-Purchase of furniture and fixtures for educational purposes, WS/MP691/2025-2026/227843-Construction of rooms and halls in school and colleges

#### recommendedAmount
- Type: float64
- Nulls: 1 (9.1%)
- Unique: 6
- Samples: 2999928.0, 914736.0, 2000000.0

#### recommendedDate
- Type: str
- Nulls: 1 (9.1%)
- Unique: 6
- Samples: 09-Sep-2024, 13-Feb-2025, 20-Aug-2025

#### workStatus
- Type: str
- Nulls: 1 (9.1%)
- Unique: 3
- Samples: Physical Inspection, Physical Inspection, Pending for Sanction

## Dataset: completed

- **Records**: 4
- **Columns**: 3

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 4
- Samples: 140096, 175514, 237152

#### completionDate
- Type: str
- Nulls: 1 (25.0%)
- Unique: 3
- Samples: 11-Sep-2024, 10-Dec-2025, 07-Jan-2026

#### workStatus
- Type: str
- Nulls: 0 (0.0%)
- Unique: 1
- Samples: Completed, Completed, Completed

## Dataset: expenditure

- **Records**: 0
- **Columns**: 0

### Field Dictionary

## WorkID Join Analysis

### Recommended
- count: 11
- in_completed: 4
- in_expenditure: 0
- in_both: 0
- only_in_recommended: 7

### Completed
- count: 4
- in_recommended: 4
- in_expenditure: 0
- in_both: 0
- only_in_completed: 0

### Expenditure
- count: 0
- in_recommended: 0
- in_completed: 0
- in_both: 0
- only_in_expenditure: 0

### Overall
- total_unique_workids: 11
- in_all_three: 0
- in_two_or_more: 4