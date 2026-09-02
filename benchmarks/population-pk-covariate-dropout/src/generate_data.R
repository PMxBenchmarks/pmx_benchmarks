# =============================================================================
# Population PK/PD with Covariates and Informative Dropout  (v2)
# Community-standard REFERENCE generator  (mrgsolve + tidyverse)
# -----------------------------------------------------------------------------
# Implements the same model as the canonical src/generate_data.py. RNG streams
# differ across languages, so this reproduces a STATISTICALLY EQUIVALENT dataset,
# not a bit-identical one; the CSVs in data/ are produced by the Python script
# (seed = 20260614). Validated model structure; run locally to confirm in your
# mrgsolve version.   Requires: mrgsolve (>=1.0), dplyr, tidyr, readr, yaml
# =============================================================================
library(mrgsolve); library(dplyr); library(tidyr); library(readr); library(yaml)
set.seed(20260614)

N <- 400; DOSE <- 100; TAU <- 24; NDOSE <- 14; TEND <- NDOSE * TAU; BREAK <- 168
LLOQ <- 0.10

# ---- PK (2-cmt oral) + PD (indirect response) model, with IIV and IOV --------
code <- '
$PARAM TVCL=5, TVVC=30, TVQ=4, TVVP=50, TVKA=1,
       R0=100, KOUT=0.05, IMAX=0.8, IC50=1.0, WT=70, EGFR=100, OCC=1
$CMT GUT CENT PERIPH RESP
$MAIN
double KCL = (OCC < 1.5) ? KCL1 : KCL2;     // interoccasion variability
double KKA = (OCC < 1.5) ? KKA1 : KKA2;
double CL = TVCL*pow(WT/70.0,0.75)*pow(EGFR/100.0,0.70)*exp(ECL + KCL);
double VC = TVVC*(WT/70.0)*exp(EVC);
double Q  = TVQ *pow(WT/70.0,0.75)*exp(EQ);
double VP = TVVP*(WT/70.0)*exp(EVP);
double KA = TVKA*exp(EKA + KKA);
double R0i = R0*exp(ER0);
double ICi = IC50*exp(EIC);
RESP_0 = R0i;                               // PD baseline initial condition
double KIN = KOUT*R0i;
$OMEGA @block @correlation @labels ECL EVC
0.30
0.40 0.25
$OMEGA @labels EQ EVP EKA ER0 EIC
0.1225 0.09 0.25 0.0625 0.16
$OMEGA @labels KCL1 KKA1
0.0289 0.09
$OMEGA @labels KCL2 KKA2
0.0289 0.09
$ODE
double conc = CENT/VC;
dxdt_GUT    = -KA*GUT;
dxdt_CENT   =  KA*GUT - (CL/VC + Q/VC)*CENT + (Q/VP)*PERIPH;
dxdt_PERIPH =  (Q/VC)*CENT - (Q/VP)*PERIPH;
dxdt_RESP   =  KIN*(1.0 - IMAX*conc/(ICi + conc)) - KOUT*RESP;
$TABLE
capture IPRED_PK = CENT/VC;
capture IPRED_PD = RESP;
capture CLi = CL;
'
mod <- mcode("poppkpd", code)

# ---- covariates --------------------------------------------------------------
make_pop <- function(n) {
  age  <- pmin(pmax(rnorm(n, 52, 15), 18), 85)
  sex  <- rbinom(n, 1, 0.5)
  wt0  <- pmin(pmax(exp(rnorm(n, log(72), 0.18)), 42), 120)
  egfr0 <- pmin(pmax((110 - 0.6*(age-40) + 4*sex)*exp(rnorm(n, 0, 0.17)), 20), 150)
  wt2   <- pmin(pmax(wt0*exp(rnorm(n, 0, 0.03)), 42), 130)
  egfr2 <- pmin(pmax(egfr0*exp(rnorm(n, 0, 0.12)), 18, 160), 160)
  tibble(ID=1:n, AGE=round(age), SEX=sex, wt0, egfr0, wt2, egfr2,
         adherence=rbeta(n, 9, 1))
}

dose_rows <- function(id, adh) {                 # imperfect adherence + timing
  out <- list()
  for (d in 0:(NDOSE-1)) {
    if (runif(1) > adh) next
    sd <- if (runif(1) < 0.10) 4 else 1
    t  <- max(0, d*TAU + rnorm(1, 0, sd))
    out[[length(out)+1]] <- tibble(time=round(t,2), evid=1, amt=DOSE, cmt=1, DVID=0)
  }
  if (!length(out)) out[[1]] <- tibble(time=0, evid=1, amt=DOSE, cmt=1, DVID=0)
  bind_rows(out)
}
pk_times <- function() {
  if (runif(1) < 0.25) base <- c(.5,1,2,4,6,8,12,24,167.5,335.5)
  else { base <- c(runif(1,.5,4), runif(1,5,14))
    for (d in sample(c(4,7,11,14), sample(1:3,1)))
      base <- c(base, if (runif(1)<.5) d*24-runif(1,.2,1) else (d-1)*24+runif(1,1,12)) }
  sort(unique(round(pmin(pmax(base*runif(length(base),.92,1.08),.25),335.9),2)))
}
pd_times <- function() {
  base <- c(0,168,336); if (runif(1)<.5) base <- c(base,72)
  sort(unique(round(pmin(pmax(base+rnorm(length(base),0,1.5),0),336),2)))
}

pop <- make_pop(N)

# ---- build input data set (dose + PK + PD obs), with time-varying covariates -
build_input <- function(pop) {
  rows <- lapply(seq_len(nrow(pop)), function(i) {
    s <- pop[i,]
    d <- dose_rows(s$ID, s$adherence)
    pk <- tibble(time=pk_times(), evid=0, amt=0, cmt=2, DVID=1)
    pd <- tibble(time=pd_times(), evid=0, amt=0, cmt=3, DVID=2)
    r  <- bind_rows(d, pk, pd) %>% mutate(ID=s$ID,
            OCC = if_else(time < BREAK, 1, 2),
            WTt = if_else(time < BREAK, s$wt0, s$wt2),
            EGFRt = if_else(time < BREAK, s$egfr0, s$egfr2))
    r
  })
  bind_rows(rows) %>% arrange(ID, time, desc(evid)) %>%
    rename(WT=WTt, EGFR=EGFRt)
}
input <- build_input(pop)

sim <- mod %>% data_set(input) %>% mrgsim(obsonly=FALSE, recover="DVID,OCC") %>% as_tibble()

# ---- competing-risk multi-cause dropout (uses individual CL and PD response) -
ind <- sim %>% group_by(ID) %>% summarise(CL=first(CLi[CLi>0]),
          resp7=approx(time, IPRED_PD, xout=168)$y,
          R0=first(IPRED_PD), .groups="drop") %>%
  mutate(cavg=DOSE/(CL*TAU),
         suppr=1-resp7/R0,
         z_expo=(log(cavg)-mean(log(cavg)))/sd(log(cavg)),
         z_poor=(-suppr-mean(-suppr))/sd(-suppr)) %>%
  left_join(pop %>% select(ID,AGE), by="ID") %>%
  mutate(z_age=(AGE-50)/15,
         hAE=0.009*exp(0.9*z_expo+0.4*z_age), hLoE=0.006*exp(1.1*z_poor),
         hLTFU=0.003, hAdmin=0.0015)

draw_drop <- function(h) {                       # returns c(time, reason)
  H <- c(h$hAE, h$hLoE, h$hLTFU, h$hAdmin); tot <- sum(H)
  for (day in 1:NDOSE) if (runif(1) < 1-exp(-tot))
    return(c(day*TAU, sample(1:4, 1, prob=H/tot)))
  c(1e9, 0)
}
dd <- t(sapply(seq_len(nrow(ind)), function(i) draw_drop(ind[i,])))
ind$dropout_time <- dd[,1]; ind$reason <- dd[,2]; ind$DROPOUT <- as.integer(dd[,1] < 1e9)

# ---- assemble released data set (RUV, outliers, BLQ, covariate noise/missing)-
miss_egfr_subj <- pop$ID[runif(N) < 0.05]
final <- sim %>% left_join(ind %>% select(ID,dropout_time,DROPOUT,reason), by="ID") %>%
  filter((evid==1 & time < dropout_time) | (evid==0 & time <= dropout_time)) %>%
  rowwise() %>%
  mutate(
    Y = case_when(
      DVID==1 ~ IPRED_PK*(1+rnorm(1,0,0.20)) + rnorm(1,0,0.02),
      DVID==2 ~ IPRED_PD*(1+rnorm(1,0,0.15)),
      TRUE ~ NA_real_),
    Y = if_else(evid==0 & runif(1) < 0.02,          # assay outliers
                Y * if_else(DVID==1, sample(c(runif(1,2.5,5),runif(1,.2,.4)),1),
                                     sample(c(runif(1,1.5,2.5),runif(1,.4,.7)),1)), Y),
    BLQ = as.integer(DVID==1 & Y < LLOQ),
    MDV = as.integer(evid==1 | BLQ==1),
    DV  = case_when(evid==1 ~ ".", BLQ==1 ~ ".",
                    DVID==1 ~ sprintf("%.4f", Y), DVID==2 ~ sprintf("%.3f", max(Y,0))),
    WTr = if_else(runif(1) < 0.03, NA_real_, WT*exp(rnorm(1,0,0.01))),
    EGFRr = if_else(runif(1) < 0.03 | ID %in% miss_egfr_subj, NA_real_, EGFR*exp(rnorm(1,0,0.08)))
  ) %>% ungroup() %>%
  group_by(ID) %>% arrange(time, .by_group=TRUE) %>%
  mutate(TAD = time - cummax(if_else(evid==1, time, -Inf)),
         TAD = if_else(is.finite(TAD) & TAD>=0, TAD, time)) %>% ungroup() %>%
  left_join(pop %>% select(ID,AGE,SEX), by="ID") %>%
  transmute(ID, TIME=round(time,2), TAD=round(TAD,2), DVID, AMT=amt, DV,
            EVID=evid, MDV, CMT=cmt, BLQ=if_else(is.na(BLQ),0L,BLQ), DOSE=DOSE,
            WT=if_else(is.na(WTr),".",sprintf("%.1f",WTr)),
            EGFR=if_else(is.na(EGFRr),".",sprintf("%.1f",EGFRr)),
            AGE, SEX, DROPOUT, DROPOUT_REASON=reason) %>%
  arrange(ID, TIME, desc(EVID), DVID)

train_ids <- ind %>% left_join(pop,by="ID") %>%
  mutate(b=findInterval(egfr0, quantile(egfr0,c(.25,.5,.75))), s=b*2+DROPOUT) %>%
  group_by(s) %>% slice_sample(prop=0.70) %>% pull(ID)
write_csv(final %>% filter(ID %in% train_ids), "../data/train.csv")
write_csv(final %>% filter(!ID %in% train_ids), "../data/test.csv")

# ---- counterfactual truth files ---------------------------------------------
# The held-out truth (tasks/cmin_2x_truth.yml, tasks/pd_response_2x_truth.yml) is
# defined as the true individual Cmin,ss and PD suppression under 200 mg QD with
# IIV but NO interoccasion variability and NO residual error. That specification
# is produced by the canonical Python reference (src/generate_data.py); regenerate
# the truth there to keep it identical to the distributed files.
message("R reference complete: data/train.csv and data/test.csv written.")
message("Run src/generate_data.py to (re)generate the canonical truth files.")
