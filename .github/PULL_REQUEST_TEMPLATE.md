# Benchmark Submission

## Submission Track

Which goal does this submission target? (check one)

- [ ] **Goal 1 — Generic Benchmark** (teaching case, agentic dataset, unit-test style, moderate novelty)
- [ ] **Goal 2 — Grand Challenge** (highly realistic, field-level problem, QM publication eligible)

Not sure? See [Scope & Eligibility](https://pmxbenchmarks.github.io/pmx_benchmarks/scope.html).

---

## Benchmark Information

**Dataset Name:**
**Authors:**
**Brief Description:**

---

## Motivation *(required for all submissions)*

> Why should this dataset be added to this repository?

<!-- Your answer here -->

> Which existing datasets (in this repo or elsewhere) are most similar?

<!-- Your answer here -->

> How is this submission concretely different enough to warrant inclusion?

<!-- Your answer here -->

---

## Submission Checklist

### Required Files

- [ ] `benchmarks/<dataset-name>/index.qmd` with all required sections (including Motivation)
- [ ] `benchmarks/<dataset-name>/data/train.csv`
- [ ] `benchmarks/<dataset-name>/data/test.csv`
- [ ] `benchmarks/<dataset-name>/data/data-dictionary.yml` (yspec-style YAML)
- [ ] `benchmarks/<dataset-name>/metadata.yml` with `goal` field set

### Documentation

- [ ] Abstract clearly describes the benchmark
- [ ] Motivation section is present (see above)
- [ ] Background and context are provided
- [ ] Data generation process is documented (for synthetic data)
- [ ] All variables described with units in the data dictionary
- [ ] Tasks clearly defined with metrics and output formats
- [ ] Train/test split rationale is explained
- [ ] References included where appropriate

### Data Quality

- [ ] Train and test files use consistent column structure
- [ ] Data dictionary covers all columns
- [ ] No personally identifiable information (PII) included
- [ ] Data is longitudinal *(Goal 2 required; Goal 1 typical)*
- [ ] Realistic sampling, dropouts, and relationships *(Goal 2 required)*

### Task Requirements

- [ ] At least one task defined with `type`, `output_format`, and `metric`
- [ ] Evaluation performed on the test set
- [ ] Tasks reflect real or plausible drug-development decisions

### Metadata

- [ ] All required fields completed
- [ ] `goal` field set (`generic` or `grand_challenge`)
- [ ] YAML syntax is valid
- [ ] Authors and affiliations are accurate
- [ ] License is specified

### Technical

- [ ] Quarto builds successfully: `quarto render benchmarks/<dataset-name>/index.qmd`
- [ ] Validation scripts pass: `python .github/scripts/validate_benchmark.py`
- [ ] All links in documentation work
- [ ] File naming follows conventions (lowercase-with-dashes)

---

## Additional Information

### Related Publications or Preprints

<!-- List any related publications or preprints -->

### Notes for Reviewers

<!-- Optional: context, known limitations, or open questions -->

---

## For Maintainers

- [ ] Automated validation passed
- [ ] Scientific review completed
- [ ] Documentation quality approved
- [ ] DOI requested / assigned
- [ ] Benchmark listing updated on website
