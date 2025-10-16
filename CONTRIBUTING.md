# Contributing to PMX Benchmarks

Thank you for your interest in contributing to the Pharmacometrics Benchmarks Initiative! This document provides guidelines for contributing.

## Ways to Contribute

### 1. Submit a Benchmark Dataset

The primary way to contribute is by submitting a high-quality benchmark dataset. See our [Submission Guide](https://korsbo.github.io/pmx_benchmarks/submission-guide.html) for detailed instructions.

**Quick steps:**

1. Fork this repository
2. Create your benchmark in `benchmarks/<your-dataset-name>/`
3. Follow the [BENCHMARK_TEMPLATE.md](BENCHMARK_TEMPLATE.md)
4. Submit a Pull Request using the PR template

### 2. Improve Documentation

Help us improve our documentation by:

- Fixing typos or clarifying instructions
- Adding examples or tutorials
- Improving the submission guide
- Translating documentation

### 3. Develop Helper Packages

Contribute to our companion data loading packages in separate repositories:

- **Python**: `pmx-benchmarks-py` (coming soon)
- **R**: `pmxbenchmarks` (coming soon)
- **Julia**: `PMXBenchmarks.jl` (coming soon)

These packages provide programmatic access to benchmarks with convenient APIs.

### 4. Review Benchmarks

Become a reviewer! Help evaluate submitted benchmarks for:

- Scientific rigor
- Documentation quality
- Data quality
- Adherence to requirements

Contact the maintainers to express interest in reviewing.

### 5. Report Issues

Found a bug or have a suggestion? [Open an issue](https://github.com/korsbo/pmx_benchmarks/issues).

## Development Setup

### Prerequisites

- [Quarto](https://quarto.org/) (for building the website)
- Python 3.8+ (for validation scripts)
- Git

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/pmx_benchmarks.git
cd pmx_benchmarks

# Install Python dependencies for validation
pip install pandas pyyaml jsonschema

# Install Quarto
# See https://quarto.org/docs/get-started/

# Preview the website locally
quarto preview
```

### Testing Your Changes

Before submitting a PR:

```bash
# Test Quarto rendering
quarto render

# Run validation scripts (if adding/modifying benchmarks)
python .github/scripts/validate_benchmark.py
python .github/scripts/validate_data.py
```

## Submission Guidelines

### Benchmark Submissions

- **One benchmark per PR**: Submit each benchmark separately
- **Complete documentation**: Include all required sections in `index.qmd`
- **Valid data**: Ensure CSV files load correctly
- **Follow structure**: Use the template and example as guides
- **Test locally**: Render with Quarto before submitting

### Code Contributions

- **Clear commit messages**: Describe what and why
- **Small, focused changes**: Easier to review
- **Test your code**: Ensure it works as expected
- **Document your changes**: Update relevant documentation

### Pull Request Process

1. **Create a descriptive PR title**
   - For benchmarks: "Add [benchmark-name] benchmark"
   - For fixes: "Fix [issue]"
   - For features: "Add [feature]"

2. **Fill out the PR template** completely

3. **Respond to reviews** promptly and professionally

4. **Update your PR** based on feedback

5. **Be patient**: Reviews may take time, especially for benchmarks

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior

- Be respectful and professional
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy toward others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting/derogatory comments
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Violations may result in temporary or permanent ban from the project. Report concerns to [contact information TBD].

## Attribution

Contributors will be acknowledged in:

- Benchmark authorship (for benchmark submissions)
- Repository contributors list
- Release notes (for significant contributions)

## Questions?

- Check our [FAQ](https://korsbo.github.io/pmx_benchmarks/submission-guide.html)
- [Open a discussion](https://github.com/korsbo/pmx_benchmarks/discussions)
- [Contact us](https://korsbo.github.io/pmx_benchmarks/contact.html)

## License

By contributing, you agree that your contributions will be licensed under:

- MIT License (for code and documentation)
- CC-BY-4.0 (recommended for benchmark data)

---

Thank you for contributing to pharmacometrics research! 🎯
