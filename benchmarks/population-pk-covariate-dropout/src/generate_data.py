#!/usr/bin/env python3
"""
Reference data generator (v2) for the benchmark:
  "Population PK/PD with Covariates and Informative Dropout"

This is the implementation that produced the DISTRIBUTED CSV files and the
counterfactual ground-truth files. It is fully seeded and reproducible.

v2 adds clinical-development realism on top of the v1 popPK core:
  * imperfect adherence (missed doses) + dose-timing variability;
  * time-varying, noisy, and partly MISSING covariates (WT, eGFR);
  * interoccasion variability (IOV) on CL and ka;
  * a pharmacodynamic (PD) biomarker via an indirect-response (turnover) model
    -> a true exposure-response relationship;
  * competing-risk MULTI-CAUSE informative dropout
    (adverse event ~ exposure; lack of efficacy ~ poor response; LTFU; admin);
  * data-quality noise (assay outliers).

Model: 2-compartment first-order oral PK + indirect-response PD.
Run:   python3 generate_data.py
Deps:  numpy, pandas, pyyaml
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
import yaml

# --------------------------------------------------------------------------- #
SEED = 20260614
N_SUBJECTS = 400
TRAIN_FRAC = 0.70

DOSE = 100.0
TAU = 24.0
N_DOSES = 14
TEND = N_DOSES * TAU                       # 336 h
DT = 0.1
GRID = np.arange(0, TEND + DT, DT)
BREAK = 168.0                              # occasion / covariate-period boundary (day 7)

# PK typical values
TVCL, TVVC, TVQ, TVVP, TVKA = 5.0, 30.0, 4.0, 50.0, 1.0
WT_REF, EGFR_REF = 70.0, 100.0
EXP_WT_CL, EXP_EGFR_CL, EXP_WT_V, EXP_WT_Q = 0.75, 0.70, 1.00, 0.75

# IIV (SD of log-normal random effects): CL, Vc, Q, Vp, ka
OMEGA = np.array([0.30, 0.25, 0.35, 0.30, 0.50])
CORR_CL_VC = 0.40
OMEGA_IOV_CL = 0.17                        # interoccasion variability
OMEGA_IOV_KA = 0.30

# Residual error (PK) + LLOQ
SIGMA_PROP, SIGMA_ADD, LLOQ = 0.20, 0.02, 0.10

# PD indirect-response (inhibition of production) model
PD_R0 = 100.0                              # baseline biomarker (U)
PD_KOUT = 0.05                             # 1/h  (turnover, t1/2 ~ 14 h)
PD_IMAX = 0.80
PD_IC50 = 1.0                              # mg/L
OMEGA_R0 = 0.25
OMEGA_IC50 = 0.40
PD_SIGMA_PROP = 0.15                       # PD residual error
PD_LLOQ = None

# Adherence / dosing
ADH_A, ADH_B = 9.0, 1.0                    # Beta(9,1): mostly-adherent population
DOSE_TIME_SD = 1.0                         # h, day-to-day timing variability
DOSE_TIME_SD_BIG = 4.0                     # occasional larger deviation
DOSE_TIME_BIG_P = 0.10

# Covariate time-variation + measurement / missingness
WT_DRIFT_SD = 0.03                         # between-period proportional drift
EGFR_DRIFT_SD = 0.12
WT_MEAS_CV = 0.01
EGFR_MEAS_CV = 0.08
P_SUBJ_EGFR_MISSING = 0.05                 # subjects missing eGFR entirely
P_ROW_COV_MISSING = 0.03                   # sporadic per-row covariate missingness

# Multi-cause dropout daily baseline hazards + effect sizes
H_AE, BETA_AE_EXPO, BETA_AE_AGE = 0.009, 0.90, 0.40
H_LOE, BETA_LOE_RESP = 0.006, 1.10
H_LTFU = 0.003
H_ADMIN = 0.0015

# Data-quality noise
P_OUTLIER = 0.02                           # fraction of observations that are gross outliers

# Counterfactual
CF_DOSE, CF_N, CF_TEND = 200.0, 20000, TEND

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
DATA_DIR = os.path.join(BENCH, "data")
TASKS_DIR = os.path.join(BENCH, "tasks")
QA_DIR = os.path.join(HERE, "qa")
for d in (DATA_DIR, TASKS_DIR, QA_DIR):
    os.makedirs(d, exist_ok=True)

DOSE_REASON = {0: "completed", 1: "adverse_event", 2: "lack_of_efficacy",
               3: "lost_to_followup", 4: "administrative"}


# --------------------------------------------------------------------------- #
def make_population(n, rng, tv_covariates=True, iov=True):
    """Sample covariates, PK/PD individual parameters (with IOV), adherence."""
    age = np.clip(rng.normal(52, 15, n), 18, 85)
    sex = rng.integers(0, 2, n)
    wt0 = np.clip(np.exp(rng.normal(np.log(72.0), 0.18, n)), 42, 120)
    egfr0 = np.clip((110 - 0.60 * (age - 40) + 4 * sex) * np.exp(rng.normal(0, 0.17, n)),
                    20, 150)

    # period-specific (time-varying) TRUE covariates: period 1 (0-7 d), period 2 (7-14 d)
    if tv_covariates:
        wt = np.stack([wt0, np.clip(wt0 * np.exp(rng.normal(0, WT_DRIFT_SD, n)), 42, 130)], 1)
        egfr = np.stack([egfr0,
                         np.clip(egfr0 * np.exp(rng.normal(0, EGFR_DRIFT_SD, n)), 18, 160)], 1)
    else:
        wt = np.stack([wt0, wt0], 1)
        egfr = np.stack([egfr0, egfr0], 1)

    # IIV (CL,Vc correlated) + remaining diagonal
    R = np.eye(5); R[0, 1] = R[1, 0] = CORR_CL_VC
    eta = rng.multivariate_normal(np.zeros(5), np.outer(OMEGA, OMEGA) * R, n)
    # IOV per occasion (2)
    if iov:
        iov_cl = rng.normal(0, OMEGA_IOV_CL, (n, 2))
        iov_ka = rng.normal(0, OMEGA_IOV_KA, (n, 2))
    else:
        iov_cl = np.zeros((n, 2)); iov_ka = np.zeros((n, 2))

    CL = np.stack([
        TVCL * (wt[:, p]/WT_REF)**EXP_WT_CL * (egfr[:, p]/EGFR_REF)**EXP_EGFR_CL
        * np.exp(eta[:, 0] + iov_cl[:, p]) for p in (0, 1)], 1)
    Vc = np.stack([TVVC * (wt[:, p]/WT_REF)**EXP_WT_V * np.exp(eta[:, 1]) for p in (0, 1)], 1)
    Q = np.stack([TVQ * (wt[:, p]/WT_REF)**EXP_WT_Q * np.exp(eta[:, 2]) for p in (0, 1)], 1)
    Vp = np.stack([TVVP * (wt[:, p]/WT_REF)**EXP_WT_V * np.exp(eta[:, 3]) for p in (0, 1)], 1)
    ka = np.stack([TVKA * np.exp(eta[:, 4] + iov_ka[:, p]) for p in (0, 1)], 1)

    # PD individual parameters
    R0 = PD_R0 * np.exp(rng.normal(0, OMEGA_R0, n))
    ic50 = PD_IC50 * np.exp(rng.normal(0, OMEGA_IC50, n))

    cl_avg = CL.mean(1)
    cavg = DOSE / (cl_avg * TAU)
    adherence = rng.beta(ADH_A, ADH_B, n)
    return dict(age=age, sex=sex, wt0=wt0, egfr0=egfr0, wt=wt, egfr=egfr,
                CL=CL, Vc=Vc, Q=Q, Vp=Vp, ka=ka, R0=R0, ic50=ic50,
                cavg=cavg, adherence=adherence)


# --------------------------------------------------------------------------- #
def simulate(p, dose_steps, dose_amt, store=True):
    """Vectorised RK4 of PK (3 cmt) + PD (1 cmt) with period-switching params.

    dose_steps: dict {grid_index: subject_idx_array}; dose_amt: mg per dose.
    Returns (conc, resp) trajectories if store, else (Cmin_last, R_last).
    """
    n = p["CL"].shape[0]
    ng = len(GRID)
    Ad = np.zeros(n); Ac = np.zeros(n); Ap = np.zeros(n)
    R = p["R0"].copy()                       # PD starts at baseline
    kin = PD_KOUT * p["R0"]
    imax, ic50, kout = PD_IMAX, p["ic50"], PD_KOUT

    def rates(period):
        return (p["ka"][:, period], p["CL"][:, period] / p["Vc"][:, period],
                p["Q"][:, period] / p["Vc"][:, period],
                p["Q"][:, period] / p["Vp"][:, period], p["Vc"][:, period])

    ka, k10, k12, k21, Vc = rates(0)
    conc = np.zeros((n, ng)) if store else None
    resp = np.zeros((n, ng)) if store else None

    def deriv(ad, ac, ap, r):
        C = ac / Vc
        prod = kin * (1.0 - imax * C / (ic50 + C))
        return (-ka * ad,
                ka * ad - (k10 + k12) * ac + k21 * ap,
                k12 * ac - k21 * ap,
                prod - kout * r)

    for i in range(ng):
        t = GRID[i]
        if abs(t - BREAK) < DT / 2:          # switch to period-2 parameters
            ka, k10, k12, k21, Vc = rates(1)
        if i in dose_steps:
            Ad[dose_steps[i]] += dose_amt
        if store:
            conc[:, i] = Ac / Vc
            resp[:, i] = R
        if i < ng - 1:
            k1 = deriv(Ad, Ac, Ap, R)
            k2 = deriv(Ad+DT/2*k1[0], Ac+DT/2*k1[1], Ap+DT/2*k1[2], R+DT/2*k1[3])
            k3 = deriv(Ad+DT/2*k2[0], Ac+DT/2*k2[1], Ap+DT/2*k2[2], R+DT/2*k2[3])
            k4 = deriv(Ad+DT*k3[0], Ac+DT*k3[1], Ap+DT*k3[2], R+DT*k3[3])
            Ad = Ad + DT/6*(k1[0]+2*k2[0]+2*k3[0]+k4[0])
            Ac = Ac + DT/6*(k1[1]+2*k2[1]+2*k3[1]+k4[1])
            Ap = Ap + DT/6*(k1[2]+2*k2[2]+2*k3[2]+k4[2])
            R = R + DT/6*(k1[3]+2*k2[3]+2*k3[3]+k4[3])
    if store:
        return conc, resp
    return Ac / Vc, R


def dose_schedule(rng, adherence):
    """Return list of (time, amt) actually-administered doses for one subject."""
    doses = []
    for d in range(N_DOSES):
        if rng.random() > adherence:          # missed dose (non-adherence)
            continue
        sd = DOSE_TIME_SD_BIG if rng.random() < DOSE_TIME_BIG_P else DOSE_TIME_SD
        t = max(0.0, d * TAU + rng.normal(0, sd))
        doses.append((round(t, 2), DOSE))
    if not doses:                              # guarantee at least the first dose
        doses = [(0.0, DOSE)]
    return doses


def build_dose_steps(per_subject_doses):
    steps = {}
    for sidx, doses in enumerate(per_subject_doses):
        for t, amt in doses:
            i = int(round(t / DT))
            steps.setdefault(i, []).append(sidx)
    return {i: np.array(idx) for i, idx in steps.items()}


# --------------------------------------------------------------------------- #
def pk_sample_times(rng):
    if rng.random() < 0.25:
        base = np.array([0.5, 1, 2, 4, 6, 8, 12, 24, 167.5, 335.5])
    else:
        times = [rng.uniform(0.5, 4), rng.uniform(5, 14)]
        for d in rng.choice([4, 7, 11, 14], size=int(rng.integers(1, 4)), replace=False):
            times.append(d*24 - rng.uniform(0.2, 1.0) if rng.random() < 0.5
                         else (d-1)*24 + rng.uniform(1, 12))
        base = np.array(times)
    t = base * rng.uniform(0.92, 1.08, len(base))
    return np.sort(np.unique(np.round(np.clip(t, 0.25, 335.9), 2)))


def pd_sample_times(rng):
    # baseline + day-7 + day-14 troughs (+ optional day-3), jittered
    base = [0.0, 168.0, 336.0]
    if rng.random() < 0.5:
        base.append(72.0)
    t = np.array(base) + rng.normal(0, 1.5, len(base))
    return np.sort(np.unique(np.round(np.clip(t, 0.0, 336.0), 2)))


def tad(t, dtimes):
    prior = dtimes[dtimes <= t]
    return round(float(t - prior.max()), 2) if len(prior) else round(float(t), 2)


# --------------------------------------------------------------------------- #
def simulate_dropout(p, resp, rng):
    """Competing-risk multi-cause dropout using exposure and PD response."""
    n = p["CL"].shape[0]
    z = lambda x: (x - np.mean(x)) / np.std(x)
    z_expo = z(np.log(p["cavg"]))
    z_age = (p["age"] - 50) / 15
    # response driver: suppression at day 7 (low suppression -> lack of efficacy)
    idx7 = int(round(168.0 / DT))
    suppression = 1.0 - resp[:, idx7] / p["R0"]
    z_poor = z(-suppression)

    h_ae = H_AE * np.exp(BETA_AE_EXPO * z_expo + BETA_AE_AGE * z_age)
    h_loe = H_LOE * np.exp(BETA_LOE_RESP * z_poor)
    h_ltfu = np.full(n, H_LTFU)
    h_admin = np.full(n, H_ADMIN)
    H = np.stack([h_ae, h_loe, h_ltfu, h_admin], 1)
    h_tot = H.sum(1)
    p_event = 1.0 - np.exp(-h_tot)

    drop_day = np.full(n, np.inf)
    reason = np.zeros(n, dtype=int)
    for day in range(1, N_DOSES + 1):
        u = rng.random(n)
        newly = (u < p_event) & np.isinf(drop_day)
        if newly.any():
            probs = H[newly] / h_tot[newly][:, None]
            picks = np.array([rng.choice(4, p=pr) for pr in probs]) + 1
            drop_day[newly] = day
            reason[newly] = picks
    dtime = np.where(np.isinf(drop_day), 1e9, drop_day * TAU)
    flag = np.where(np.isinf(drop_day), 0, 1)
    return dtime, flag, reason


# --------------------------------------------------------------------------- #
def recorded_cov(true_val, cv, rng, missing):
    if missing:
        return "."
    return round(float(true_val * np.exp(rng.normal(0, cv))), 1)


def build_dataset(p, per_doses, conc, resp, dtime, flag, reason, rng):
    rows = []
    n = p["CL"].shape[0]
    n_obs_pk = n_obs_pd = n_blq = n_out = 0
    egfr_missing_subj = rng.random(n) < P_SUBJ_EGFR_MISSING

    for i in range(n):
        sid = i + 1
        dtimes = np.array([t for t, _ in per_doses[i]])
        base = dict(AGE=int(round(p["age"][i])), SEX=int(p["sex"][i]),
                    DROPOUT=int(flag[i]), DROPOUT_REASON=int(reason[i]))

        def cov_at(t, col, missing_row):
            period = 0 if t < BREAK else 1
            if col == "WT":
                return recorded_cov(p["wt"][i, period], WT_MEAS_CV, rng, missing_row)
            val_missing = missing_row or egfr_missing_subj[i]
            return recorded_cov(p["egfr"][i, period], EGFR_MEAS_CV, rng, val_missing)

        # dose rows (administered before dropout)
        for t, amt in per_doses[i]:
            if t < dtime[i]:
                mr = rng.random() < P_ROW_COV_MISSING
                rows.append(dict(ID=sid, TIME=round(t, 2), TAD=0.0, DVID=0, AMT=amt,
                                 DV=".", EVID=1, MDV=1, CMT=1, BLQ=0, DOSE=DOSE,
                                 WT=cov_at(t, "WT", mr), EGFR=cov_at(t, "EGFR", mr), **base))

        # PK observations
        tpk = pk_sample_times(rng); tpk = tpk[tpk <= dtime[i]]
        if len(tpk) == 0:
            tpk = np.array([round(float(rng.uniform(1, 12)), 2)])
        ipred = np.interp(tpk, GRID, conc[i])
        for tt, ip in zip(tpk, ipred):
            y = ip * (1 + rng.normal(0, SIGMA_PROP)) + rng.normal(0, SIGMA_ADD)
            if rng.random() < P_OUTLIER:                    # assay outlier
                y *= rng.choice([rng.uniform(2.5, 5), rng.uniform(0.2, 0.4)]); n_out += 1
            n_obs_pk += 1
            mr = rng.random() < P_ROW_COV_MISSING
            blq = int(y < LLOQ)
            n_blq += blq
            rows.append(dict(ID=sid, TIME=round(float(tt), 2), TAD=tad(tt, dtimes),
                             DVID=1, AMT=0, DV="." if blq else round(float(y), 4),
                             EVID=0, MDV=blq, CMT=2, BLQ=blq, DOSE=DOSE,
                             WT=cov_at(tt, "WT", mr), EGFR=cov_at(tt, "EGFR", mr), **base))

        # PD observations
        tpd = pd_sample_times(rng); tpd = tpd[tpd <= dtime[i]]
        rpred = np.interp(tpd, GRID, resp[i])
        for tt, rp in zip(tpd, rpred):
            y = rp * (1 + rng.normal(0, PD_SIGMA_PROP))
            if rng.random() < P_OUTLIER:
                y *= rng.choice([rng.uniform(1.5, 2.5), rng.uniform(0.4, 0.7)]); n_out += 1
            n_obs_pd += 1
            mr = rng.random() < P_ROW_COV_MISSING
            rows.append(dict(ID=sid, TIME=round(float(tt), 2), TAD=tad(tt, dtimes),
                             DVID=2, AMT=0, DV=round(float(max(y, 0)), 3),
                             EVID=0, MDV=0, CMT=3, BLQ=0, DOSE=DOSE,
                             WT=cov_at(tt, "WT", mr), EGFR=cov_at(tt, "EGFR", mr), **base))

    df = pd.DataFrame(rows)
    df["_o"] = -df["EVID"]
    df = df.sort_values(["ID", "TIME", "_o", "DVID"]).drop(columns="_o").reset_index(drop=True)
    cols = ["ID", "TIME", "TAD", "DVID", "AMT", "DV", "EVID", "MDV", "CMT", "BLQ",
            "DOSE", "WT", "EGFR", "AGE", "SEX", "DROPOUT", "DROPOUT_REASON"]
    return df[cols], dict(pk=n_obs_pk, pd=n_obs_pd, blq=n_blq, outliers=n_out)


# --------------------------------------------------------------------------- #
def split_subjects(p, flag, rng):
    egfr = p["egfr0"]
    qb = np.digitize(egfr, np.quantile(egfr, [.25, .5, .75]))
    strata = qb * 2 + flag
    train = []
    for s in np.unique(strata):
        idx = np.where(strata == s)[0]; rng.shuffle(idx)
        train += list(idx[:int(round(TRAIN_FRAC*len(idx)))] + 1)
    train = set(train)
    return sorted(train), sorted(set(range(1, len(flag)+1)) - train)


def counterfactual_truth(rng):
    """Cmin,ss (PK) and steady-state biomarker suppression (PD) under 2x dose.

    Ideal regimen: full adherence, no IOV, no RUV, baseline covariates."""
    p = make_population(CF_N, rng, tv_covariates=False, iov=False)
    doses = [[(d*TAU, CF_DOSE) for d in range(N_DOSES)] for _ in range(CF_N)]
    steps = build_dose_steps(doses)
    cmin, rlast = simulate(p, steps, CF_DOSE, store=False)
    suppression = 100.0 * (1.0 - rlast / p["R0"])      # % suppression from baseline
    qs = [.10, .25, .50, .75, .90]
    pk = {f"q{int(v*100)}": round(float(np.quantile(cmin, v)), 4) for v in qs}
    pd_ = {f"q{int(v*100)}": round(float(np.quantile(suppression, v)), 2) for v in qs}
    return pk, pd_


# --------------------------------------------------------------------------- #
def main():
    rng = np.random.default_rng(SEED)
    p = make_population(N_SUBJECTS, rng)
    per_doses = [dose_schedule(rng, p["adherence"][i]) for i in range(N_SUBJECTS)]
    steps = build_dose_steps(per_doses)
    conc, resp = simulate(p, steps, DOSE, store=True)
    dtime, flag, reason = simulate_dropout(p, resp, rng)
    df, counts = build_dataset(p, per_doses, conc, resp, dtime, flag, reason, rng)

    train_ids, test_ids = split_subjects(p, flag, rng)
    train = df[df.ID.isin(train_ids)].reset_index(drop=True)
    test = df[df.ID.isin(test_ids)].reset_index(drop=True)
    train.to_csv(os.path.join(DATA_DIR, "train.csv"), index=False)
    test.to_csv(os.path.join(DATA_DIR, "test.csv"), index=False)

    pk_truth, pd_truth = counterfactual_truth(np.random.default_rng(SEED + 1))
    with open(os.path.join(TASKS_DIR, "cmin_2x_truth.yml"), "w") as f:
        yaml.safe_dump({
            "scenario": "200 mg once daily (2x observed dose), full adherence, same 14-day schedule",
            "endpoint": "Steady-state trough Cmin,ss (mg/L) at 24 h after the day-14 dose; "
                        "true individual values (structural model + IIV, no IOV/RUV).",
            "population": "Data-generating population (baseline covariates); dropout not applied.",
            "n_sim": CF_N, "estimates": pk_truth}, f, sort_keys=False)
    with open(os.path.join(TASKS_DIR, "pd_response_2x_truth.yml"), "w") as f:
        yaml.safe_dump({
            "scenario": "200 mg once daily (2x observed dose), full adherence, same 14-day schedule",
            "endpoint": "Steady-state PD biomarker suppression (% reduction from baseline) "
                        "at day 14; true individual values (structural model + IIV, no RUV).",
            "population": "Data-generating population (baseline covariates); dropout not applied.",
            "n_sim": CF_N, "estimates": pd_truth}, f, sort_keys=False)

    # QA provenance (NOT distributed; see .gitignore)
    qa = pd.DataFrame(dict(ID=np.arange(1, N_SUBJECTS+1), age=p["age"], sex=p["sex"],
                           wt0=p["wt0"], egfr0=p["egfr0"], CL1=p["CL"][:, 0],
                           CL2=p["CL"][:, 1], R0=p["R0"], ic50=p["ic50"],
                           cavg=p["cavg"], adherence=p["adherence"],
                           dropout=flag, reason=reason, dropout_time=dtime))
    qa["split"] = np.where(qa.ID.isin(train_ids), "train", "test")
    qa.to_csv(os.path.join(QA_DIR, "subject_parameters.csv"), index=False)

    md5 = lambda f: hashlib.md5(open(f, "rb").read()).hexdigest()
    reason_counts = {DOSE_REASON[k]: int((reason == k).sum()) for k in DOSE_REASON}
    doses_taken = [len(d) for d in per_doses]
    summary = dict(
        seed=SEED, version="2.0.0", n_subjects=N_SUBJECTS,
        n_subjects_train=len(train_ids), n_subjects_test=len(test_ids),
        n_rows_total=len(df), n_obs_pk=counts["pk"], n_obs_pd=counts["pd"],
        n_obs_total=counts["pk"]+counts["pd"],
        n_obs_train=int((train.EVID == 0).sum()), n_obs_test=int((test.EVID == 0).sum()),
        blq_pct=round(100*counts["blq"]/counts["pk"], 2),
        outlier_pct=round(100*counts["outliers"]/(counts["pk"]+counts["pd"]), 2),
        dropout_pct=round(100*flag.mean(), 2), dropout_reasons=reason_counts,
        mean_adherence=round(float(np.mean(doses_taken)/N_DOSES), 3),
        cf_pk=pk_truth, cf_pd=pd_truth,
        md5_train=md5(os.path.join(DATA_DIR, "train.csv")),
        md5_test=md5(os.path.join(DATA_DIR, "test.csv")))
    with open(os.path.join(QA_DIR, "generation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
