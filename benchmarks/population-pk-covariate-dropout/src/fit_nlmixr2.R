# =============================================================================
# NLME parameter-recovery check for the population-pk-covariate-dropout
# benchmark: FOCEI fit (nlmixr2) of the true structural model to train.csv,
# followed by an estimated-vs-true comparison table.
# Output: recovery_table.csv + a markdown table on stdout.
# Run:  Rscript fit_nlmixr2.R                (from src/)
# =============================================================================
suppressMessages({library(nlmixr2); library(dplyr); library(readr)})

path <- "../data/train.csv"

d <- read_csv(path, show_col_types = FALSE) %>%
  mutate(DV = suppressWarnings(as.numeric(DV)),
         WT = suppressWarnings(as.numeric(WT)),
         EGFR = suppressWarnings(as.numeric(EGFR))) %>%
  filter(DVID %in% c(0, 1)) %>%
  filter(!(EVID == 0 & (BLQ == 1 | is.na(DV)))) %>%      # M1: drop BLQ
  group_by(ID) %>%
  mutate(WT0 = first(na.omit(WT)), EGFR0 = first(na.omit(EGFR))) %>%
  ungroup() %>%
  filter(!is.na(WT0), !is.na(EGFR0)) %>%                 # subjects w/ baseline covs
  transmute(ID, TIME, DV, AMT, EVID, CMT, WT0, EGFR0)

cat(sprintf("Fitting %d subjects, %d PK observations\n",
            n_distinct(d$ID), sum(d$EVID == 0)))

pk2 <- function() {
  ini({
    tcl <- log(5); tvc <- log(30); tq <- log(4); tvp <- log(50); tka <- log(1)
    wt_cl   <- 0.75
    egfr_cl <- 0.70
    eta.cl ~ 0.09
    eta.vc ~ 0.0625
    eta.ka ~ 0.25
    prop.sd <- 0.20
    add.sd  <- 0.02
  })
  model({
    CL <- exp(tcl + wt_cl * log(WT0/70) + egfr_cl * log(EGFR0/100) + eta.cl)
    Vc <- exp(tvc + log(WT0/70) + eta.vc)
    Q  <- exp(tq  + 0.75 * log(WT0/70))
    Vp <- exp(tvp + log(WT0/70))
    ka <- exp(tka + eta.ka)
    k10 <- CL/Vc; k12 <- Q/Vc; k21 <- Q/Vp
    d/dt(depot) = -ka * depot
    d/dt(cent)  =  ka * depot - (k10 + k12) * cent + k21 * peri
    d/dt(peri)  =  k12 * cent - k21 * peri
    cp = cent / Vc
    cp ~ prop(prop.sd) + add(add.sd)
  })
}
# Note: IIV kept on CL/Vc/ka only (Q, Vp fixed-effect allometric) -- with sparse
# sampling in 75% of subjects, IIV on peripheral parameters is weakly identified;
# this mirrors common practice. IOV is deliberately NOT modeled, so omega(CL)
# is expected to absorb part of the true IOV (kappa_CL SD 0.17).

fit <- nlmixr2(pk2, d, est = "focei",
               control = foceiControl(print = 0, eval.max = 400))

tf <- fit$parFixedDf
g <- function(nm, exp_scale = FALSE) {
  est <- tf[nm, "Estimate"]; se <- tf[nm, "SE"]
  if (exp_scale) c(exp(est), exp(est) * se) else c(est, se)
}
om <- sqrt(diag(fit$omega))

truth <- tibble::tribble(
  ~parameter,            ~true,  ~est,                 ~se,
  "CL (L/h)",             5.0,   g("tcl",  TRUE)[1],   g("tcl",  TRUE)[2],
  "Vc (L)",              30.0,   g("tvc",  TRUE)[1],   g("tvc",  TRUE)[2],
  "Q (L/h)",              4.0,   g("tq",   TRUE)[1],   g("tq",   TRUE)[2],
  "Vp (L)",              50.0,   g("tvp",  TRUE)[1],   g("tvp",  TRUE)[2],
  "ka (1/h)",             1.0,   g("tka",  TRUE)[1],   g("tka",  TRUE)[2],
  "WT exponent on CL",    0.75,  g("wt_cl")[1],        g("wt_cl")[2],
  "eGFR exponent on CL",  0.70,  g("egfr_cl")[1],      g("egfr_cl")[2],
  "omega CL (SD)",        0.30,  om[["eta.cl"]],       NA,
  "omega Vc (SD)",        0.25,  om[["eta.vc"]],       NA,
  "omega ka (SD)",        0.50,  om[["eta.ka"]],       NA,
  "prop. error (SD)",     0.20,  tf["prop.sd","Estimate"], NA,
  "add. error (mg/L)",    0.02,  tf["add.sd","Estimate"],  NA
) %>% mutate(rel_bias_pct = 100 * (est - true) / true)

dir.create("qa", showWarnings = FALSE); write_csv(truth, "qa/recovery_table.csv")
cat("\n| Parameter | True | Estimated (SE) | Rel. bias % |\n|---|---|---|---|\n")
for (i in seq_len(nrow(truth))) {
  r <- truth[i, ]
  se_txt <- if (is.na(r$se)) "" else sprintf(" (%.3g)", r$se)
  cat(sprintf("| %s | %.3g | %.3g%s | %+.1f |\n",
              r$parameter, r$true, r$est, se_txt, r$rel_bias_pct))
}
cat(sprintf("\nOFV: %.1f | condition number: %s\n",
            fit$objective, format(fit$conditionNumberCor, digits = 3)))
