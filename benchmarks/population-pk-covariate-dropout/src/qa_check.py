#!/usr/bin/env python3
"""QA / verification checks for the v2 benchmark."""
import os, numpy as np, pandas as pd, yaml
import generate_data as G

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
TASKS = os.path.join(HERE, "..", "tasks")
sp = pd.read_csv(os.path.join(HERE, "qa", "subject_parameters.csv"))
train = pd.read_csv(os.path.join(DATA, "train.csv"))
test = pd.read_csv(os.path.join(DATA, "test.csv"))
both = pd.concat([train, test], ignore_index=True)
def line(s): print("\n"+"="*70+f"\n{s}\n"+"="*70)

line("1. SPLIT INTEGRITY")
print("train/test subj:", train.ID.nunique(), test.ID.nunique(),
      "| overlap:", len(set(train.ID)&set(test.ID)),
      "| identical cols:", list(train.columns)==list(test.columns))
print("columns:", list(train.columns))

line("2. SAMPLING (PK=DVID1, PD=DVID2)")
for dvid, name in [(1,"PK"),(2,"PD")]:
    o = both[(both.EVID==0)&(both.DVID==dvid)]
    per = o.groupby("ID").size()
    print(f"  {name}: n_obs={len(o)}  subj_with_data={o.ID.nunique()}  "
          f"samples/subj min/med/max={per.min()}/{int(per.median())}/{per.max()}  "
          f"distinct_times={o.TIME.round(2).nunique()}")

line("3. DATA QUALITY: BLQ + outliers + missing covariates")
pk = both[(both.EVID==0)&(both.DVID==1)]
print("BLQ % (PK):", round(100*(pk.BLQ==1).mean(),2))
print("EGFR missing rows %:", round(100*(both.EGFR.astype(str)==".").mean(),2),
      "| WT missing rows %:", round(100*(both.WT.astype(str)==".").mean(),2))

line("4. ADHERENCE")
dose = both[both.EVID==1]
doses_per = dose.groupby("ID").size()
print("mean doses administered/subj:", round(doses_per.mean(),2), "of 14",
      "| min:", doses_per.min(), "| mean adherence:", round(sp.adherence.mean(),3))
# dose-time deviation from nominal grid
dev = dose.TIME.values - np.round(dose.TIME.values/24)*24
print("dose-time SD from nominal (h):", round(dev.std(),2))

line("5. TIME-VARYING COVARIATES + IOV")
print("subjects whose recorded EGFR changes over time:",
      int((both[both.EGFR.astype(str)!="."].assign(e=lambda d:d.EGFR.astype(float))
           .groupby("ID").e.nunique()>1).sum()), "of 400")
print("IOV: SD of within-subject log(CL2/CL1) =",
      round(np.std(np.log(sp.CL2/sp.CL1)),3), "(includes covariate drift + IOV)")

line("6. PD EXPOSURE-RESPONSE (higher exposure -> lower biomarker)")
pdrows = both[(both.DVID==2)&(both.TIME>300)].copy()
pdrows["DV"] = pd.to_numeric(pdrows.DV, errors="coerce")
pd14 = pdrows.groupby("ID").DV.mean().rename("bio14")
m = pd.merge(pd14, sp[["ID","cavg","R0"]], on="ID")
m["supp"] = 100*(1 - m.bio14/m.R0)
print("corr(Cavg, day14 biomarker):  %.3f (should be negative)"%np.corrcoef(m.cavg,m.bio14)[0,1])
print("corr(Cavg, %% suppression):    %.3f (should be positive)"%np.corrcoef(m.cavg,m.supp)[0,1])

line("7. MULTI-CAUSE INFORMATIVE DROPOUT")
rmap={0:"completed",1:"AE",2:"LoE",3:"LTFU",4:"admin"}
g=sp.assign(reason=sp.reason.map(rmap)).groupby("reason").agg(
    n=("ID","size"), mean_cavg=("cavg","mean"))
print(g.round(3))
print("(AE should have HIGH mean Cavg; LoE LOW; LTFU/admin ~ average)")
sp["expo_tertile"]=pd.qcut(sp.cavg,3,labels=["low","mid","high"])
print("\nAE-dropout rate by exposure tertile:")
print((sp.assign(ae=(sp.reason==1)).groupby("expo_tertile",observed=True).ae.mean()*100).round(1))

line("8. COVARIATE RECOVERY (true CL period1 vs baseline covariates)")
y=np.log(sp.CL1.values)
X=np.column_stack([np.ones(len(y)),np.log(sp.wt0/70),np.log(sp.egfr0/100)])
b=np.linalg.lstsq(X,y,rcond=None)[0]
print("  WT exponent: %.3f (true 0.75) | eGFR exponent: %.3f (true 0.70)"%(b[1],b[2]))

line("9. TRAIN/TEST BALANCE")
for nm,d in [("train",sp[sp.split=="train"]),("test",sp[sp.split=="test"])]:
    print(" %-5s n=%d WT0=%.1f eGFR0=%.1f AGE=%.1f %%male=%.0f dropout%%=%.1f"%(
        nm,len(d),d.wt0.mean(),d.egfr0.mean(),d.age.mean(),100*d.sex.mean(),100*d.dropout.mean()))

line("10. COUNTERFACTUAL TRUTH FILES")
for f in ["cmin_2x_truth.yml","pd_response_2x_truth.yml"]:
    t=yaml.safe_load(open(os.path.join(TASKS,f)))
    print(f, "->", t["estimates"])
print("\n(typical-subject Cmin,ss at 200 mg independently computed = 0.606 mg/L; "
      "population median should be near this)")
print("\nALL QA CHECKS COMPLETE.")
