This repository is a place where researchers can upload benchmark datasets for pharmacometrics.

The datasets will mostly be synthetic with some strong demands on how realistic and well crafted they are. Each benchmark PR will essentially constitute a peer reviewed paper with a DOI and the review process will be rigorous.


A core purpose is to enable the quantification of performance of different modelling methodology in a way that makes it easier to compar different methodology papers with each other. We will also be able to host competitions.

The benchmark datasets must 

- Be realistic (irregular sampling, confounding dropouts, realistic relationships)
- Be longitudinal 
- Be well described
  - Describing the generative process for synthetic data
  - Describing what realistic scenario they represents
- Have associated tasks to reflect the ways in which we would leverage such a dataset for informing decisions in the drug development pipeline
- Have a specified train/test split where the evaluation of performance will be on the test.


We need a GitHub Pages website describing

- The purpose of the repo
- The initiative itself
  - Governing body
  - Association with ISoP and publication venue
  - How to get in touch
- The submission process
- A header for all the benchmarks
  - subheaders for specific benchmark datasets (and benchmarking tasks) that are populated in each submission PR

