# Pharmacometrics Benchmarks

A curated collection of benchmark datasets for evaluating pharmacometric modeling methodologies.

## 🎯 Purpose

This repository provides high-quality, peer-reviewed benchmark datasets that enable:

- Reproducible comparison of different modeling approaches
- Transparent evaluation of new methods
- Community-driven standards for pharmacometrics
- Competitive innovation through organized challenges

## 🌐 Website

Visit our [GitHub Pages site](https://pmxbenchmarks.github.io/pmx_benchmarks/) for:

- Complete documentation
- Browse available benchmarks
- Submission guidelines
- Contact information

## 📊 Available Benchmarks

Browse all benchmarks at [pmxbenchmarks.github.io/pmx_benchmarks/benchmarks](https://pmxbenchmarks.github.io/pmx_benchmarks/)

## 🚀 Quick Start

### Using Benchmarks

Benchmarks can be accessed directly from this repository or using helper packages:

```python
# Python example - direct access
import pandas as pd

# Load a benchmark dataset
train = pd.read_csv('benchmarks/example-pk-model-selection/data/train.csv')
test = pd.read_csv('benchmarks/example-pk-model-selection/data/test.csv')
```

```r
# R example - direct access
library(readr)

# Load a benchmark dataset
train <- read_csv('benchmarks/example-pk-model-selection/data/train.csv')
test <- read_csv('benchmarks/example-pk-model-selection/data/test.csv')
```

### Helper Packages

For easier programmatic access, see our companion repositories:

- **Python**: `pmx-benchmarks-py` (coming soon)
- **R**: `pmxbenchmarks` (coming soon)
- **Julia**: `PMXBenchmarks.jl` (coming soon)

### Submitting a Benchmark

1. Fork this repository
2. Create your benchmark in `benchmarks/<your-dataset-name>/`
3. Follow the structure in `benchmarks/example-pk-model-selection/`
4. Submit a Pull Request

See our [submission guide](https://pmxbenchmarks.github.io/pmx_benchmarks/submission-guide.html) for detailed instructions.

## 📁 Repository Structure

```
pmx_benchmarks/
├── benchmarks/              # Benchmark datasets
│   └── <dataset-name>/
│       ├── index.qmd        # Documentation
│       ├── metadata.yml     # Machine-readable metadata
│       ├── data/
│       │   ├── train.csv
│       │   ├── test.csv
│       │   └── data-dictionary.yml
│       └── README.md
├── .github/
│   ├── workflows/          # CI/CD workflows
│   ├── scripts/            # Validation scripts
│   └── PULL_REQUEST_TEMPLATE.md
├── _quarto.yml             # Quarto configuration
├── index.qmd               # Website homepage
├── about.qmd               # About the initiative
├── submission-guide.qmd    # Submission guidelines
├── benchmarks.qmd          # Benchmark listings
├── contact.qmd             # Contact information
└── README.md               # This file
```

## 🔍 Benchmark Goals

There are two submission tracks — see the [Scope & Eligibility](https://pmxbenchmarks.github.io/pmx_benchmarks/scope.html) page for details.

**Goal 1 — Generic Benchmarks:** Teaching cases, agentic datasets, unit-test style submissions. Moderate novelty bar. Receives a DOI.

**Goal 2 — Grand Challenges:** Highly realistic drug-development scenarios. High novelty bar. Receives a DOI and is eligible for fast-track consideration at Quantitative Medicine.

All benchmarks must:

- ✅ Be **pharmacometric in nature** (PK, PD, exposure-response, or related)
- ✅ Be **well documented** (generative process or scenario description, yspec YAML data dictionary)
- ✅ Have **associated tasks** with defined metrics
- ✅ Have a **specified train/test split**
- ✅ Include a **motivation section** (why this dataset, what's similar, what's different)

## 🤝 Contributing

We welcome contributions! Please see:

- [Scope & Eligibility](https://pmxbenchmarks.github.io/pmx_benchmarks/scope.html)
- [Submission Guide](https://pmxbenchmarks.github.io/pmx_benchmarks/submission-guide.html)
- [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md)

## 📝 License

- **Code and documentation:** MIT License
- **Individual benchmarks:** Licensed as specified in their metadata (typically CC-BY-4.0)

## 📧 Contact

- **GitHub Discussions:** [Start a discussion](https://github.com/pmxbenchmarks/pmx_benchmarks/discussions)
- **Issues:** [Report an issue](https://github.com/pmxbenchmarks/pmx_benchmarks/issues)

## 🏛️ Governance

This initiative is associated with the International Society of Pharmacometrics (ISoP).

For more information, see our [About page](https://pmxbenchmarks.github.io/pmx_benchmarks/about.html).
