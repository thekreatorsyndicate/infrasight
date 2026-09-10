# Data Quality Report — Run official_maharashtra_20260910_094029

Generated: 2026-09-10T09:40:29.593874Z

## Dataset: recommended

- **Records**: 144
- **Columns**: 8

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 142
- Samples: 143961, 136520, 1055

#### state
- Type: str
- Nulls: 3 (2.1%)
- Unique: 3
- Samples: Maharashtra, Maharashtra, Maharashtra

#### district
- Type: str
- Nulls: 3 (2.1%)
- Unique: 83
- Samples: AKOLA(DISTRICT COLLECTOR AKOLA_IDA), AMRAVATI(DISTRICT COLLECTOR AMRAVATI_IDA), AZAMGARH(DISTRICT MAGISTRATE AZAMGARH_IDA)

#### workCategory
- Type: str
- Nulls: 3 (2.1%)
- Unique: 3
- Samples: Normal/Others, Normal/Others, Trust and Society

#### workName
- Type: str
- Nulls: 3 (2.1%)
- Unique: 126
- Samples: WS/MP18111/2026-2027/143961-Construction of community centers and community halls, WS/MP18112/2024-2025/136520-Construction of community centers and community halls, NA-Construction of rooms and halls in school and colleges

#### recommendedAmount
- Type: float64
- Nulls: 3 (2.1%)
- Unique: 95
- Samples: 1000000.0, 2000000.0, 1000000.0

#### recommendedDate
- Type: str
- Nulls: 3 (2.1%)
- Unique: 84
- Samples: 31-Mar-2025, 20-Aug-2024, 18-Jan-2025

#### workStatus
- Type: str
- Nulls: 3 (2.1%)
- Unique: 7
- Samples: Pending for Sanction, Work Completed, NA

## Dataset: completed

- **Records**: 3999
- **Columns**: 3

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3997
- Samples: 167291, 209773, 209775

#### completionDate
- Type: str
- Nulls: 3 (0.1%)
- Unique: 403
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
- count: 142
- in_completed: 75
- in_expenditure: 0
- in_both: 0
- only_in_recommended: 67

### Completed
- count: 3997
- in_recommended: 75
- in_expenditure: 0
- in_both: 0
- only_in_completed: 3922

### Expenditure
- count: 0
- in_recommended: 0
- in_completed: 0
- in_both: 0
- only_in_expenditure: 0

### Overall
- total_unique_workids: 4064
- in_all_three: 0
- in_two_or_more: 75