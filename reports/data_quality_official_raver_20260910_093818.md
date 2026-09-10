# Data Quality Report — Run official_raver_20260910_093818

Generated: 2026-09-10T09:38:19.217260Z

## Dataset: recommended

- **Records**: 96
- **Columns**: 8

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 96
- Samples: 143961, 136520, 1055

#### state
- Type: str
- Nulls: 1 (1.0%)
- Unique: 1
- Samples: Maharashtra, Maharashtra, Maharashtra

#### district
- Type: str
- Nulls: 1 (1.0%)
- Unique: 39
- Samples: AKOLA(DISTRICT COLLECTOR AKOLA_IDA), AMRAVATI(DISTRICT COLLECTOR AMRAVATI_IDA), AZAMGARH(DISTRICT MAGISTRATE AZAMGARH_IDA)

#### workCategory
- Type: str
- Nulls: 1 (1.0%)
- Unique: 3
- Samples: Normal/Others, Normal/Others, Trust and Society

#### workName
- Type: str
- Nulls: 1 (1.0%)
- Unique: 77
- Samples: WS/MP18111/2026-2027/143961-Construction of community centers and community halls, WS/MP18112/2024-2025/136520-Construction of community centers and community halls, NA-Construction of rooms and halls in school and colleges

#### recommendedAmount
- Type: float64
- Nulls: 1 (1.0%)
- Unique: 47
- Samples: 1000000.0, 2000000.0, 1000000.0

#### recommendedDate
- Type: str
- Nulls: 1 (1.0%)
- Unique: 50
- Samples: 31-Mar-2025, 20-Aug-2024, 18-Jan-2025

#### workStatus
- Type: str
- Nulls: 1 (1.0%)
- Unique: 6
- Samples: Pending for Sanction, Work Completed, NA

## Dataset: completed

- **Records**: 939
- **Columns**: 3

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 939
- Samples: 167291, 209773, 209775

#### completionDate
- Type: str
- Nulls: 1 (0.1%)
- Unique: 265
- Samples: 10-Jun-2025, 17-Oct-2025, 17-Oct-2025

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
- count: 96
- in_completed: 45
- in_expenditure: 0
- in_both: 0
- only_in_recommended: 51

### Completed
- count: 939
- in_recommended: 45
- in_expenditure: 0
- in_both: 0
- only_in_completed: 894

### Expenditure
- count: 0
- in_recommended: 0
- in_completed: 0
- in_both: 0
- only_in_expenditure: 0

### Overall
- total_unique_workids: 990
- in_all_three: 0
- in_two_or_more: 45