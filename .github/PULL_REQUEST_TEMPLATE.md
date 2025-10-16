# Benchmark Submission

## Benchmark Information

**Dataset Name:** 
**Authors:** 
**Brief Description:** 

## Submission Checklist

Please ensure all items are completed before requesting review:

### Required Files

- [ ] `benchmarks/<dataset-name>/index.qmd` with all required sections
- [ ] `benchmarks/<dataset-name>/data/train.csv`
- [ ] `benchmarks/<dataset-name>/data/test.csv`
- [ ] `benchmarks/<dataset-name>/data/data-dictionary.csv`
- [ ] `benchmarks/<dataset-name>/metadata.yml`

### Documentation Requirements

- [ ] Abstract clearly describes the benchmark
- [ ] Background and motivation are provided
- [ ] Data generation process is documented (for synthetic data)
- [ ] All variables are described with units
- [ ] Associated tasks are clearly defined with evaluation metrics
- [ ] Train/test split rationale is explained
- [ ] References are included where appropriate

### Data Quality Requirements

- [ ] Data is realistic (irregular sampling, confounding dropouts, realistic relationships)
- [ ] Data is longitudinal
- [ ] Train and test files use consistent column structure
- [ ] Data dictionary covers all columns in data files
- [ ] No personally identifiable information (PII) is included

### Task Requirements

- [ ] At least one task is defined
- [ ] Tasks reflect real-world drug development decisions
- [ ] Evaluation metrics are specified
- [ ] Evaluation will be performed on test set

### Metadata Requirements

- [ ] All required metadata fields are completed
- [ ] YAML syntax is valid
- [ ] Authors and affiliations are accurate
- [ ] License is specified

### Technical Validation

- [ ] Quarto builds successfully without errors
- [ ] All links in documentation work correctly
- [ ] Data files load correctly (no parsing errors)
- [ ] File naming follows conventions (lowercase-with-dashes)

## Additional Information

### Data Generation (if synthetic)

<!-- Briefly describe how the synthetic data was generated -->

### Expected Use Cases

<!-- Describe the intended use cases for this benchmark -->

### Related Publications

<!-- List any related publications or preprints -->

## Reviewer Notes

<!-- Optional: Add any notes or context for reviewers -->

---

## For Maintainers

- [ ] Technical validation passed (automated checks)
- [ ] Scientific review completed
- [ ] Documentation quality approved
- [ ] DOI requested/assigned
- [ ] Benchmark listing updated
