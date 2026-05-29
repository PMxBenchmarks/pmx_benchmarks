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
│   └── data-dictionary.yml     # Column descriptions, yspec-style YAML (required)
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

## Motivation

*Required for all submissions. See [Scope & Eligibility](../../scope.qmd) for details.*

**Why should this dataset be added to this repository?**

...

**Which existing datasets (in this repo or elsewhere) are most similar?**

...

**How is this submission concretely different enough to warrant inclusion?**

...

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

Key variables with brief descriptions. Reference data-dictionary.yml.

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
goal: generic          # generic | grand_challenge
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
  # Regression example — predict a continuous outcome on the test set
  - name: prediction-accuracy
    type: regression
    description: Predict <outcome> in the test set
    target: DV           # column name in test.csv containing ground truth
    output_format: {type: individual_predictions, columns: [ID, TIME, PRED]}
    metric: rmse         # rmse | mae | nrmse

  # Classification example — predict a binary or multi-class outcome
  # - name: event-prediction
  #   type: classification
  #   description: Predict probability of <event>
  #   output_format: {type: probabilities, columns: [ID, P_EVENT]}
  #   metric: auroc      # auroc requires output_format.type: probabilities
  #   # output_format: {type: class_predictions, columns: [ID, CLASS]}
  #   # metric: accuracy | f1   (use these with class_predictions)

  # Counterfactual example — aggregate distribution under an intervention
  # - name: cmax-exceedance-2x-dose
  #   type: counterfactual
  #   description: Cmax distribution under 2x observed dose
  #   scenario: "2x observed dose, same schedule"
  #   output_format: {type: summary_stats, stats: [q10, q25, q50, q75, q90]}
  #   truth_file: tasks/cmax_truth.yml   # pre-computed from generative model
  #   metric: quantile_coverage
license: CC-BY-4.0
doi: TBD  # Will be assigned upon acceptance
```

## data-dictionary.yml Template

[yspec](https://github.com/metrumresearchgroup/yspec)-style YAML. Top-level
keys are column names (one per data column); reserved keys ending in `__`
(e.g. `SETUP__`) are not treated as columns.

```yaml
SETUP__:
  description: Brief description of this data dictionary
  glue:
    - "{{ short }}"

ID:
  short: Subject identifier
  type: integer
  values: 1 to N

TIME:
  short: Time since first dose
  type: numeric
  unit: hours
  range: [0, ]

DV:
  short: Dependent variable (plasma concentration)
  type: numeric
  unit: mg/L
  comment: Observation rows only; dose-event rows have DV missing.

DROPOUT:
  short: Dropout indicator
  type: integer
  values:
    0: completed
    1: dropped out
```

New submissions must use yspec-style YAML for the data dictionary.

## Tips

1. **Be thorough**: Complete documentation speeds up review
2. **Use the example**: `benchmarks/example-pk-model-selection/` is a good reference
3. **Test locally**: Render with Quarto before submitting
4. **Validate data**: Run validation scripts locally
5. **Clear naming**: Use lowercase-with-dashes for directory names
