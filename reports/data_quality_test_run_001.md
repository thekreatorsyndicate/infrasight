# Data Quality Report — Run test_run_001

Generated: 2026-09-09T18:56:45.361591Z

## Dataset: recommended

- **Records**: 3
- **Columns**: 7

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 1, 2, 3

#### state
- Type: str
- Nulls: 0 (0.0%)
- Unique: 2
- Samples: Maharashtra, Maharashtra, Delhi

#### district
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Mumbai, Pune, New Delhi

#### workName
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Road 1, School 1, Hospital 1

#### workCategory
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Roads, Education, Health

#### recommendedAmount
- Type: int64
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 1000000, 500000, 2000000

#### recommendedDate
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 01-01-2023, 01-02-2023, 01-03-2023

## Dataset: completed

- **Records**: 3
- **Columns**: 7

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 1, 2, 4

#### state
- Type: str
- Nulls: 0 (0.0%)
- Unique: 2
- Samples: Maharashtra, Maharashtra, Karnataka

#### district
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Mumbai, Pune, Bangalore

#### workName
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Road 1, School 1, Park 1

#### workCategory
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: Roads, Education, Environment

#### completionDate
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 01-06-2023, 01-07-2023, 01-08-2023

#### workStatus
- Type: str
- Nulls: 0 (0.0%)
- Unique: 1
- Samples: Completed, Completed, Completed

## Dataset: expenditure

- **Records**: 4
- **Columns**: 3

### Field Dictionary

#### workId
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 1, 1, 2

#### expenditureAmount
- Type: int64
- Nulls: 0 (0.0%)
- Unique: 4
- Samples: 800000, 200000, 450000

#### expenditureDate
- Type: str
- Nulls: 0 (0.0%)
- Unique: 3
- Samples: 01-05-2023, 01-06-2023, 01-06-2023

## WorkID Join Analysis

### Recommended
- count: 3
- in_completed: 2
- in_expenditure: 2
- in_both: 2
- only_in_recommended: 1

### Completed
- count: 3
- in_recommended: 2
- in_expenditure: 2
- in_both: 2
- only_in_completed: 1

### Expenditure
- count: 3
- in_recommended: 2
- in_completed: 2
- in_both: 2
- only_in_expenditure: 1

### Overall
- total_unique_workids: 5
- in_all_three: 2
- in_two_or_more: 2