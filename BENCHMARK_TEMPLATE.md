# Benchmark Submission Template

Use this template when creating a new benchmark submission.

## Directory Structure

```
benchmarks/<your-dataset-name>/
├── index.qmd                    # Main documentation (required)
├── data/
│   ├── train.csv               # Training dataset (required)
│   ├── test.csv                # Test dataset (required)
│   └── data-dictionary.csv     # Column descriptions (required)
├── scripts/                    # Data generation code (if synthetic)
│   └── generate_data.jl        # or .py, .R, etc.
└── assets/                     # Figures, tables (optional)
```

## index.qmd Frontmatter

The frontmatter is the single source of metadata. Keep it minimal:

```yaml
---
# Required
title: "Your Benchmark Title"
subtitle: "Brief one-line description"
description: "2-3 sentence summary for the listing page."
author:
  - name: Your Name
    affiliation: Your Institution
date: YYYY-MM-DD
categories:          # For filtering on the website
  - synthetic        # or: real-world, semi-synthetic
  - pk               # or: pd, pk-pd
  - your-task-type   # e.g., model-selection, predictive-modeling

# Optional but recommended
n-subjects: 100
n-train: 70
n-test: 30
task: "Brief task name"
metric: "Primary evaluation metric"
---
```

## index.qmd Content Sections

```markdown
## Abstract

Brief overview of the benchmark (2-3 sentences).

## Background

Context and motivation for this benchmark.

## Data Generation

Description of how the data was generated (for synthetic) or collected (for real).
Include model equations, parameter values, variability, study design.

## Dataset Description

Key variables with brief descriptions. Reference data-dictionary.csv.
Include sample sizes and any important notes about the data structure.

## Task

Clear description of the primary task.
- **Objective:** What should the model do?
- **Evaluation Metric:** How is performance measured?

## Train/Test Split

Description and rationale for the split.

## Reproducibility

How to regenerate the data (if synthetic). Software requirements.

## References

Relevant citations.

## License

License information (typically CC-BY-4.0).

## Citation

How to cite this benchmark.
```

How to cite this benchmark.
```

## data-dictionary.csv Template

```csv
column_name,description,units,type
ID,Subject identifier,NA,integer
TIME,Time since first dose,hours,numeric
DV,Dependent variable,mg/L,numeric
...
```

## Tips

1. **Keep it simple**: The frontmatter is your metadata — no separate metadata.yml needed
2. **Use the example**: `benchmarks/example-pk-model-selection/` and `benchmarks/idr-covariate-discovery/` are good references
3. **Test locally**: Run `quarto preview index.qmd` in your benchmark folder
4. **Clear naming**: Use lowercase_with_underscores for directory names
