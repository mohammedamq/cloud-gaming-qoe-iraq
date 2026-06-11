# Cloud Gaming QoE over ISP-Hosted Edge Infrastructure in Iraq — Reproducibility Package

This repository accompanies the paper *"Experimental Evaluation of Cloud Gaming
Quality of Experience Over ISP-Hosted Edge Infrastructure in Iraq"* (IJIES).
It contains the per-scenario measurement data, the exact aggregation and
statistical-analysis scripts that regenerate **every numerical value reported in
the tables and text**, the controlled-impairment (`tc-netem`) replay configuration,
the packet-capture filtering rules, and the scripts that redraw the figures.

> Replace the placeholder repository URL in the manuscript
> (`https://github.com/<author>/cloud-gaming-qoe-iraq`) with the real URL once this
> package is pushed to GitHub.

## Repository layout

```
.
├── README.md
├── requirements.txt
├── data/
│   └── per_scenario.csv        # 16 scenarios × {n, mean, SD, 95% CI, jitter SD, retx%, OoO%}
├── scripts/
│   ├── aggregate.py            # regenerates all site-level aggregates + correlations + sensitivity
│   ├── figure1.py              # redraws Figure 1 (network topology)
│   ├── figure2.py              # redraws Figure 2 (methodology workflow)
│   └── netem_replay.sh         # exact tc-netem / HTB commands for Profiles A, B, C
└── results/
    ├── aggregates.json         # machine-readable output of aggregate.py
    ├── Figure1.png
    └── Figure2.png
```

## Quick start

```bash
pip install -r requirements.txt
python scripts/aggregate.py          # prints + writes results/aggregates.json
python scripts/figure1.py            # writes results/Figure1.png
python scripts/figure2.py            # writes results/Figure2.png
```

## How each reported value is regenerated

All site-level aggregates are **pooled from the per-scenario sufficient statistics**
in `data/per_scenario.csv`. Because every scenario has *n* = 30, the pooled mean is
identical to the mean of the scenario means, and the pooled SD / 95% CI are computed
as if the raw 480 samples were pooled (within-group + between-group sum of squares,
t-interval). Running `scripts/aggregate.py` reproduces:

| Manuscript location | Value | Source field in `aggregates.json` |
|---|---|---|
| Table 7 / Abstract — Onsite | 156.6 ms, SD 25.3, 95% CI 153.5–159.6 (n = 270) | `site_aggregates.Onsite` |
| Table 7 — Ramadi | 149.0 ms, SD 19.0, 95% CI 145.0–153.0 (n = 90) | `site_aggregates.Ramadi` |
| Table 7 / Abstract — Sina'ah | 451.0 ms, SD 30.1, 95% CI 445.6–456.4 (n = 120) | `site_aggregates.Sinaah` |
| §5.4 — wired vs Wi-Fi onsite | 139.3 vs 173.0 ms, gap 33.7 ms | `onsite_wired`, `onsite_wifi_pchigh`, `wired_wifi_gap_ms` |
| §5.9 — correlations | jitter r = 0.97 / ρ = 0.58; retx r = 0.99 / ρ = 0.59; RTT r = 0.50 / ρ = 0.05 | `correlations` |
| §5.9 — site-stratified | within well-provisioned sites ρ ≈ 0 | `within_well_provisioned` |
| §5.9 — collinearity | jitter–retx ρ = 0.98 | `jitter_retx_collinearity` |
| §5.9 — descriptive fits (Eq. 1–2) | lag = 144.2 + 134.7·retx (R² = 0.99); lag = 128.0 + 25.7·jitter (R² = 0.94) | `descriptive_ols` |
| §5.9 — regime contrast | 154.7 vs 451.0 ms, Welch t = 50.5, p < 1e-16 | `regime_contrast` |

## Controlled impairment replay (`tc-netem`)

`scripts/netem_replay.sh` contains the exact queue-discipline configuration used in
Section 4.7. Downlink shaping is applied on an IFB device fed from the client-facing
interface; an HTB class caps the rate at 60 Mbit/s and a `netem` child qdisc applies
delay, normal-distribution jitter, and **Gilbert–Elliott burst loss** (`gemodel`).
Profile C (Sina'ah) parameters: `delay 4ms 12ms distribution normal`,
`loss gemodel 3.5% 50% 92% 0%` (mean ≈ 1.0% loss, mean burst ≈ 2 packets), `rate 60mbit`.

`tc-netem` does not expose a deterministic PRNG seed across kernel versions; for
reproducibility we therefore release (i) the realized per-run packet captures, (ii) the
exact qdisc scripts and kernel build (Linux 6.8), and (iii) the across-realization
variability (five Profile C realizations were within 14 ms of one another).

## Packet-capture filtering

Wireshark/`tshark` capture filter (Section 4.2):

```
host <edge_subnet> and (tcp or udp)
```

Per-scenario covariates were derived from the captures as: jitter SD from the packet
inter-arrival series; TCP retransmission rate from `tcp.analysis.retransmission`;
out-of-order rate from `tcp.analysis.out_of_order`.

## Data dictionary — `data/per_scenario.csv`

`uid, site, rtt_ms, media, device, game, window, date, n, mean_lag_ms, sd_lag_ms,
ci_lo, ci_hi, jitter_sd_ms, retx_pct, ooo_pct`. One row per measurement session;
each session contributes `n = 30` input-lag samples (16 × 30 = 480 total).

## License

Released for academic reproducibility. Cite the IJIES paper if you use this material.
