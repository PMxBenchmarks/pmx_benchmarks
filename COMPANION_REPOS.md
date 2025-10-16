# Companion Repositories

This document lists the companion repositories for programmatic access to PMX Benchmarks.

## Python Package: pmx-benchmarks-py

**Repository**: `korsbo/pmx-benchmarks-py` (to be created)

**Purpose**: Python package for easy loading and management of PMX benchmark datasets.

**Features**:
- List available benchmarks
- Download and cache benchmark data
- Load train/test splits
- Access metadata
- Validate local benchmark structure

**Installation** (planned):
```bash
pip install pmx-benchmarks
```

**Usage** (planned):
```python
from pmx_benchmarks import BenchmarkLoader

loader = BenchmarkLoader()
benchmarks = loader.list()

# Load a benchmark
train, test = loader.load('example-pk-model-selection')
metadata = loader.get_metadata('example-pk-model-selection')
```

## R Package: pmxbenchmarks

**Repository**: `korsbo/pmxbenchmarks` (to be created)

**Purpose**: R package for easy loading and management of PMX benchmark datasets.

**Features**:
- List available benchmarks
- Download and cache benchmark data
- Load train/test splits as tibbles
- Access metadata
- Validate local benchmark structure

**Installation** (planned):
```r
# From GitHub
devtools::install_github("korsbo/pmxbenchmarks")
```

**Usage** (planned):
```r
library(pmxbenchmarks)

benchmarks <- list_benchmarks()

# Load a benchmark
data <- load_benchmark("example-pk-model-selection")
train <- data$train
test <- data$test

metadata <- get_metadata("example-pk-model-selection")
```

## Julia Package: PMXBenchmarks.jl

**Repository**: `korsbo/PMXBenchmarks.jl` (to be created)

**Purpose**: Julia package for easy loading and management of PMX benchmark datasets.

**Features**:
- List available benchmarks
- Download and cache benchmark data
- Load train/test splits as DataFrames
- Access metadata
- Validate local benchmark structure

**Installation** (planned):
```julia
using Pkg
Pkg.add("PMXBenchmarks")
```

**Usage** (planned):
```julia
using PMXBenchmarks

benchmarks = list_benchmarks()

# Load a benchmark
train, test = load_benchmark("example-pk-model-selection")
metadata = get_metadata("example-pk-model-selection")
```

## Implementation Notes

### Common Features

All packages should:
1. Fetch benchmarks from the main `pmx_benchmarks` repository
2. Cache data locally to avoid repeated downloads
3. Validate data integrity (checksums)
4. Parse `metadata.yml` consistently
5. Handle data dictionary files
6. Support version pinning (load specific benchmark versions)

### API Consistency

Where possible, maintain similar function names and behaviors across languages:
- `list_benchmarks()` / `list()`
- `load_benchmark(name)` / `load(name)`
- `get_metadata(name)`
- `load_data_dictionary(name)`

### Testing

Each package should include:
- Unit tests for all core functions
- Integration tests using actual benchmark data
- CI/CD for automated testing

### Documentation

Each package should have:
- Clear README with installation and usage examples
- API documentation
- Vignettes/tutorials showing real-world usage
- Links back to the main repository

## Timeline

These companion repositories will be created as needed based on community interest and contribution capacity.

## Contributing

Interested in creating or maintaining one of these packages? Please [contact us](https://korsbo.github.io/pmx_benchmarks/contact.html) or open an issue in the main repository.
