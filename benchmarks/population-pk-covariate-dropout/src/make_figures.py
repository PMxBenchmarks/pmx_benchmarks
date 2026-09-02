#!/usr/bin/env python3
"""Diagnostic figures for the v2 benchmark documentation."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)

train = pd.read_csv(os.path.join(DATA, "train.csv"))
test = pd.read_csv(os.path.join(DATA, "test.csv"))
sp = pd.read_csv(os.path.join(HERE, "qa", "subject_parameters.csv"))
alld = pd.concat([train, test], ignore_index=True)
alld["DVf"] = pd.to_numeric(alld.DV, errors="coerce")
pk = alld[(alld.EVID == 0) & (alld.DVID == 1)].dropna(subset=["DVf"])
pdo = alld[(alld.EVID == 0) & (alld.DVID == 2)].dropna(subset=["DVf"])

plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 120})
C0, C1, C2 = "#2c6fbb", "#c0392b", "#27ae60"
drop_ids = set(sp[sp.dropout == 1].ID)

# Fig 1: PK concentration-time
fig, ax = plt.subplots(figsize=(7, 4.2))
for sid, g in pk.groupby("ID"):
    if sid % 4:
        continue
    g = g.sort_values("TIME")
    ax.plot(g.TIME, g.DVf, "-o", ms=2.5, lw=0.6, alpha=0.5,
            color=(C1 if sid in drop_ids else C0))
ax.set_yscale("log"); ax.set_xlabel("Time (h)"); ax.set_ylabel("Concentration (mg/L)")
ax.set_title("PK concentration-time (every 4th subject)")
ax.plot([], [], color=C0, label="completer"); ax.plot([], [], color=C1, label="dropout")
ax.legend(frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig1_conc_time.png")); plt.close(fig)

# Fig 2: multi-cause dropout
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
rmap = {0: "completed", 1: "AE", 2: "LoE", 3: "LTFU", 4: "admin"}
sp["rname"] = sp.reason.map(rmap)
order = ["AE", "LoE", "LTFU", "admin"]
cnt = sp[sp.reason > 0].rname.value_counts().reindex(order)
axes[0].bar(order, cnt.values, color=[C1, "#e67e22", "#7f8fa6", "#95a5a6"])
axes[0].set_ylabel("Subjects"); axes[0].set_title("Dropout by cause (competing risks)")
mc = sp.groupby("rname", observed=True).cavg.mean().reindex(["AE", "completed", "LoE"])
axes[1].bar(["AE", "completed", "LoE"], mc.values, color=[C1, C2, "#e67e22"])
axes[1].axhline(sp.cavg.median(), ls="--", c="k", lw=0.8, label="population median")
axes[1].set_ylabel("Mean Cavg,ss (mg/L)")
axes[1].set_title("AE = high exposure, LoE = low exposure"); axes[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig2_dropout_causes.png")); plt.close(fig)

# Fig 3: covariates
fig, axes = plt.subplots(1, 3, figsize=(10, 3.2))
axes[0].hist(sp.wt0, bins=25, color=C0); axes[0].set_xlabel("Baseline weight (kg)")
axes[1].hist(sp.egfr0, bins=25, color=C0); axes[1].set_xlabel("Baseline eGFR")
axes[2].scatter(sp.age, sp.egfr0, s=8, alpha=0.4, color=C0)
axes[2].set_xlabel("Age (years)"); axes[2].set_ylabel("eGFR"); axes[2].set_title("eGFR declines with age")
for a in axes[:2]:
    a.set_ylabel("Subjects")
fig.suptitle("Covariate distributions", y=1.02)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig3_covariates.png"), bbox_inches="tight"); plt.close(fig)

# Fig 4: sampling design
fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
axes[0].hist(pk.TIME, bins=40, color=C0, alpha=0.8, label="PK")
axes[0].hist(pdo.TIME, bins=40, color=C2, alpha=0.7, label="PD")
axes[0].set_xlabel("Observation time (h)"); axes[0].set_ylabel("Count")
axes[0].set_title("Irregular sampling times"); axes[0].legend(frameon=False)
per = pk.groupby("ID").size()
axes[1].hist(per, bins=range(1, 13), color=C0, align="left", rwidth=0.85)
axes[1].set_xlabel("PK samples per subject"); axes[1].set_ylabel("Subjects")
axes[1].set_title("Sparse + rich mix")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig4_sampling.png")); plt.close(fig)

# Fig 5: PD exposure-response
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
for sid, g in pdo.groupby("ID"):
    if sid % 5:
        continue
    g = g.sort_values("TIME")
    axes[0].plot(g.TIME, g.DVf, "-o", ms=2.5, lw=0.6, alpha=0.4,
                 color=(C1 if sid in drop_ids else C0))
axes[0].set_xlabel("Time (h)"); axes[0].set_ylabel("PD biomarker (U)")
axes[0].set_title("PD biomarker over time (every 5th subject)")
bio14 = pdo[pdo.TIME > 300].groupby("ID").DVf.mean().rename("bio14")
m = pd.merge(bio14, sp[["ID", "cavg", "R0"]], on="ID")
m["supp"] = 100 * (1 - m.bio14 / m.R0)
axes[1].scatter(m.cavg, m.supp, s=10, alpha=0.4, color=C0)
axes[1].set_xlabel("Individual Cavg,ss (mg/L)"); axes[1].set_ylabel("Day-14 suppression (%)")
axes[1].set_title("Exposure-response (r=+0.49)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_exposure_response.png")); plt.close(fig)

# Fig 6: adherence
fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
doses = alld[alld.EVID == 1]
per = doses.groupby("ID").size()
axes[0].hist(per, bins=range(1, 16), color=C0, align="left", rwidth=0.85)
axes[0].set_xlabel("Doses administered (of 14)"); axes[0].set_ylabel("Subjects")
axes[0].set_title("Imperfect adherence")
dev = doses.TIME.values - np.round(doses.TIME.values / 24) * 24
axes[1].hist(dev, bins=40, color=C0)
axes[1].set_xlabel("Dose time − nominal (h)"); axes[1].set_ylabel("Doses")
axes[1].set_title("Dose-timing variability")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig6_adherence.png")); plt.close(fig)

print("figures written:", sorted(os.listdir(FIG)))
