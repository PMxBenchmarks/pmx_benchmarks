This repository is a place where researchers can upload benchmark datasets for pharmacometrics.

A core purpose is to enable the quantification of performance of different modelling
methodology in a way that makes it easier to compare different methodology papers with each
other. We will also be able to host competitions.

The datasets are mostly synthetic. Each accepted submission receives a DOI and is permanently
hosted.

## Two submission tracks

Submissions fall into one of two goals, which determine the requirements and the depth of
review. `scope.qmd` is the authoritative statement of this; the summary below is orientation
only.

- **Goal 1 — Generic Benchmarks.** Teaching cases, datasets intended for use in agentic or
  automated workflow evaluations, and unit-test style submissions that isolate a single
  modelling phenomenon. Moderate complexity, limited novelty bar. Review is structural, plus
  a light assessment of the motivation.

- **Goal 2 — Grand Challenges.** Highly realistic datasets built around a specific
  drug-development problem that current methods do not address well. Review is editorial
  triage followed by full scientific peer review, so these submissions do amount to a
  peer-reviewed paper.

Note that the repository provides datasets only. Building an agentic evaluation framework is
out of scope here and is better suited to the Agentic WG, which may still make heavy use of
these datasets in its evaluations.

## What every submission needs

- Be pharmacometric in nature
- Be well described
  - Describing the generative process for synthetic data
  - Describing what realistic scenario they represent
  - A yspec-style YAML data dictionary (`data-dictionary.yml`) covering every column
- Have associated tasks, typed and with a declared metric and output format, reflecting the
  ways in which we would leverage such a dataset for informing decisions in the drug
  development pipeline
- Have a specified train/test split where the evaluation of performance will be on the test
- Declare its track via the `goal` field in `metadata.yml` (`generic` or `grand_challenge`)
- Include a "letter to the editor" style motivation section stating why the dataset belongs
  here, which existing datasets are most similar, and how this one differs

## Additional requirements for Goal 2

- Be realistic (irregular sampling, confounding dropouts, realistic relationships)
- Be longitudinal — non-longitudinal modalities (DXA, PET imaging) are considered
  case-by-case with explicit justification

These two were originally demanded of every dataset. They are now Goal 2 requirements, so
that unit-test style datasets isolating a single phenomenon, and more exotic modalities, are
not excluded outright.

## Licensing

Everything in the repository — data, code, documentation — is MIT licensed. We use one
permissive licence rather than asking each submitter to choose, and ask politely for citation
rather than relying on a licence to compel attribution.

## Website

The repository publishes a GitHub Pages website (Quarto) describing

- The purpose of the repo
- The scope and eligibility criteria, and the two goals
- The initiative itself
  - Governing body
  - Association with ISoP and publication venue
  - How to get in touch
- The submission process
- A header for all the benchmarks
  - subheaders for specific benchmark datasets (and benchmarking tasks) that are populated in
    each submission PR
