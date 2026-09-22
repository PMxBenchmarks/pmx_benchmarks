# Population PK/PD with Covariates and Informative Dropout

A general-purpose synthetic two-compartment oral **population PK/PD** benchmark that
mirrors real clinical-development data: allometric weight + renal-function
covariates, correlated IIV, **interoccasion variability**, combined residual error,
**BLQ data**, irregular sampling, **imperfect adherence**, **time-varying / noisy /
missing covariates**, an **indirect-response PD biomarker (exposure-response)**,
**assay outliers**, and **competing-risk multi-cause informative dropout** (AE ~
exposure, lack-of-efficacy ~ response, LTFU, admin).

See [`index.qmd`](index.qmd) for full documentation.

## Contents

```
population-pk-covariate-dropout/
├── index.qmd                 # full benchmark documentation (the "paper")
├── metadata.yml              # machine-readable metadata + task definitions (v2.0.0)
├── data/
│   ├── train.csv             # 280 subjects, 2205 observations (PK + PD)
│   ├── test.csv              # 120 subjects, 971 observations
│   └── data-dictionary.yml   # column definitions (yspec-style YAML)
├── tasks/
│   ├── cmin_2x_truth.yml     # held-out truth: Cmin,ss under 2x dose
│   └── pd_response_2x_truth.yml  # held-out truth: PD suppression under 2x dose
├── figures/                  # diagnostic figures used in index.qmd
└── src/
    ├── generate_data.py      # canonical seeded generator (produces the CSVs)
    ├── generate_data.R       # mrgsolve + tidyverse reference implementation
    ├── qa_check.py           # verification checks
    ├── fit_nlmixr2.R         # NLME parameter-recovery reference fit (FOCEI)
    └── make_figures.py       # figure generation
```

## Data schema (NONMEM-style)

`ID, TIME, TAD, DVID, AMT, DV, EVID, MDV, CMT, BLQ, DOSE, WT, EGFR, AGE, SEX,
DROPOUT, DROPOUT_REASON` — `DVID` 1 = PK (mg/L), 2 = PD biomarker (U); `DV="."` =
missing (dosing/BLQ); covariates `WT`/`EGFR` are time-varying and partly missing.

## Tasks

| # | Task | Type | Output | Metric |
|---|------|------|--------|--------|
| 1 | PK concentration prediction | regression | `[ID, TIME, DVID, PRED]` | RMSE |
| 2 | PD biomarker / exposure-response | regression | `[ID, TIME, DVID, PRED]` | RMSE |
| 3 | Multi-cause dropout prediction | classification | `[ID, P_DROPOUT]` | AUROC |
| 4 | Cmin,ss under 2× dose | counterfactual | quantiles `q10..q90` | quantile coverage |
| 5 | PD suppression under 2× dose | counterfactual | quantiles `q10..q90` | quantile coverage |

## Quick start

```python
import pandas as pd
train = pd.read_csv("data/train.csv")
pk = train[(train.DVID == 1) & (train.DV != ".")].assign(DV=lambda d: d.DV.astype(float))
```

## Reproduce

```bash
python3 src/generate_data.py     # -> data/{train,test}.csv, tasks/*_truth.yml
python3 src/qa_check.py          # verification
python3 src/make_figures.py      # figures
# or, with R (community reference): Rscript src/generate_data.R
```

Seed = 20260614. License: CC-BY-4.0.
