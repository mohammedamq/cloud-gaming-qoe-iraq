#!/usr/bin/env python3
"""Regenerate every site-level and cross-scenario statistic reported in the
manuscript from data/per_scenario.csv. All aggregates are pooled from the
per-scenario sufficient statistics (n, mean, SD); because every scenario has
n = 30 this is identical to pooling the raw 480 input-lag samples.

Usage:  python scripts/aggregate.py
"""
import csv, math, json
import numpy as np
from scipy import stats

rows=list(csv.DictReader(open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','data','per_scenario.csv'))))
f=lambda k: np.array([float(r[k]) for r in rows])
n,mean,sd=f('n'),f('mean_lag_ms'),f('sd_lag_ms')
jit,retx,ooo,rtt=f('jitter_sd_ms'),f('retx_pct'),f('ooo_pct'),f('rtt_ms')
site=np.array([r['site'] for r in rows])

def pooled(mask):
    ni,mi,si=n[mask],mean[mask],sd[mask]
    N=ni.sum(); gm=(ni*mi).sum()/N
    ss=((ni-1)*si**2).sum()+(ni*(mi-gm)**2).sum()
    pv=ss/(N-1); psd=math.sqrt(pv); se=psd/math.sqrt(N)
    t=stats.t.ppf(0.975,N-1)
    return dict(scenarios=int(mask.sum()),samples=int(N),mean=round(gm,1),
               sd=round(psd,1),ci=[round(gm-t*se,1),round(gm+t*se,1)])

out={}
out['site_aggregates']={s:pooled(site==s) for s in ['Onsite','Ramadi','Sinaah']}
out['onsite_wired']=pooled(np.isin([r['uid'] for r in rows],['S01','S02','S03']))
out['onsite_wifi_pchigh']=pooled(np.isin([r['uid'] for r in rows],['S04','S05','S06']))
out['wired_wifi_gap_ms']=round(out['onsite_wifi_pchigh']['mean']-out['onsite_wired']['mean'],1)

out['correlations']={}
for nm,c in [('jitter_sd',jit),('retx_pct',retx),('mean_rtt',rtt)]:
    pr,pp=stats.pearsonr(mean,c); sr=stats.spearmanr(mean,c)
    out['correlations'][nm]=dict(pearson_r=round(pr,3),pearson_p=float(f"{pp:.2e}"),
                                 spearman_rho=round(sr.statistic,2),spearman_p=round(sr.pvalue,3))
# Site-stratified (well-provisioned only: Onsite+Ramadi)
wp=site!='Sinaah'
out['within_well_provisioned']={nm:round(stats.spearmanr(mean[wp],c[wp]).statistic,2)
    for nm,c in [('jitter_sd',jit),('retx_pct',retx),('mean_rtt',rtt)]}
out['jitter_retx_collinearity']=round(stats.spearmanr(jit,retx).statistic,2)
# Single-predictor descriptive fits
for nm,c in [('jitter_sd',jit),('retx_pct',retx)]:
    b1,b0=np.polyfit(c,mean,1); yh=b0+b1*c
    r2=1-((mean-yh)**2).sum()/((mean-mean.mean())**2).sum()
    out.setdefault('descriptive_ols',{})[nm]=dict(intercept=round(b0,1),slope=round(b1,2),r2=round(r2,3))
# Regime contrast
t,p=stats.ttest_ind(mean[site=='Sinaah'],mean[wp],equal_var=False)
out['regime_contrast']=dict(well_provisioned_mean=round(mean[wp].mean(),1),
    degraded_mean=round(mean[site=='Sinaah'].mean(),1),
    diff_ms=round(mean[site=='Sinaah'].mean()-mean[wp].mean(),0),welch_t=round(t,1),p=float(f"{p:.2e}"))

print(json.dumps(out,indent=2))
if __name__=='__main__':
    json.dump(out,open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','results','aggregates.json'),'w'),indent=2)
