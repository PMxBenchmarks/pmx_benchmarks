# Benchmark Submission Template

Use this template when creating a new benchmark submission.

## Directory Structure

```
benchmarks/<your-dataset-name>/
├── index.qmd                    # Main documentation (required)
├── metadata.yml                 # Machine-readable metadata (required)
├── data/
│   ├── train.csv               # Training dataset (required)
│   ├── test.csv                # Test dataset (required)
│   └── data-dictionary.csv     # Column descriptions (required)
└── README.md                   # Quick reference (optional, auto-generated)
```

## index.qmd Template

```markdown
---
title: "Your Benchmark Title"
subtitle: "Brief subtitle"
author:
  - name: Your Name
    affiliation: Your Institution
  - name: Co-author Name
    affiliation: Their Institution
date: YYYY-MM-DD
---

## Abstract

Brief overview of the benchmark (2-3 sentences).

## Background

Context and motivation for this benchmark.

## Data Generation

### True Model Structure

Mathematical description of the data-generating model.

### Parameter Values

List of parameters used.

### Variability

Description of random effects and error models.

### Study Design

Sample size, dosing regimen, sampling schedule, dropout.

## Dataset Description

### Variables

Key variables with brief descriptions. Reference data-dictionary.csv.

### Sample Size

Training and test set sizes.

## Tasks

### Task 1: [Name]

**Objective:** Clear description

**Evaluation Metric:** Specific metric(s)

### Task 2: [Name]

...

## Train/Test Split

Description and rationale for the split.

## Usage Example

```python
import pandas as pd
train = pd.read_csv('data/train.csv')
```

## References

Relevant citations.

## License

License information (typically CC-BY-4.0).

## Citation

How to cite this benchmark.
```

## metadata.yml Template

```yaml
name: your-dataset-name
title: Your Full Benchmark Title
version: 1.0.0
date: 2025-10-16
authors:
  - name: Your Name
    affiliation: Your Institution
    email: your.email@institution.edu
description: Brief description of the benchmark
keywords:
  - keyword1
  - keyword2
data_type: synthetic  # or semi-synthetic, real
therapeutic_area: general  # or specific area
n_subjects: 100
n_subjects_train: 70
n_subjects_test: 30
n_observations: 500
n_observations_train: 350
n_observations_test: 150
tasks:
  - name: task1
    description: Task description
    metric: RMSE
license: CC-BY-4.0
doi: TBD  # Will be assigned upon acceptance
```

## data-dictionary.csv Template

```csv
column_name,description,units,type,coding
ID,Subject identifier,-,integer,1-N
TIME,Time since first dose,hours,numeric,>=0
...
```

## Tips

1. **Be thorough**: Complete documentation speeds up review
2. **Use the example**: `benchmarks/example-pk-model-selection/` is a good reference
3. **Test locally**: Render with Quarto before submitting
4. **Validate data**: Run validation scripts locally
5. **Clear naming**: Use lowercase-with-dashes for directory names
