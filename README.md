# Cloud Gaming QoE over ISP-Hosted Edge Infrastructure in Iraq

**Paper ID:** 20263399
**Title:** Experimental Evaluation of Cloud Gaming Quality of Experience Over ISP-Hosted Edge Infrastructure in Iraq
**Journal:** International Journal of Intelligent Engineering and Systems (IJIES)

## Overview

This repository contains all data, scripts, and analysis notebooks needed to reproduce every reported result in the paper. The study evaluates cloud gaming Quality of Experience (QoE) across 16 measurement scenarios deployed over a Blacknut ISP-edge node in Iraq, covering three geographic sites (Onsite/Industry, Ramadi, Sinaiah), two access media (wired Ethernet and Wi-Fi), two device types (PC and mobile), and two games (Golazo and Grip). A controlled network-emulation (netem) replay phase is also included to isolate the effect of measured impairments.

---

## Repository Structure

```
cloud-gaming-qoe-iraq/
|-- README.md
|-- data/
|   |-- raw/
|   |   |-- input_lag/
|   |   |   |-- S01_input_lag_raw.csv   <- Per-sample input-lag annotations (ms), 30 samples each
|   |   |   |-- S02_input_lag_raw.csv
|   |   |   |-- S03_input_lag_raw.csv
|   |   |   |-- S04_input_lag_raw.csv
|   |   |   |-- S05_input_lag_raw.csv
|   |   |   |-- S06_input_lag_raw.csv
|   |   |   |-- S07_input_lag_raw.csv
|   |   |   |-- S08_input_lag_raw.csv
|   |   |   |-- S09_input_lag_raw.csv
|   |   |   |-- S10_input_lag_raw.csv
|   |   |   |-- S11_input_lag_raw.csv
|   |   |   |-- S12_input_lag_raw.csv
|   |   |   |-- S13_input_lag_raw.csv
|   |   |   |-- S14_input_lag_raw.csv
|   |   |   |-- S15_input_lag_raw.csv
|   |   |   `-- S16_input_lag_raw.csv
|   |   |-- network/
|   |   |   |-- prtg_exports/
|   |   |   |   |-- prtg_onsite_rtt_jitter.csv    <- PRTG RTT/jitter time-series exports
|   |   |   |   |-- prtg_ramadi_rtt_jitter.csv
|   |   |   |   `-- prtg_sinaiah_rtt_jitter.csv
|   |   |   `-- wireshark/
|   |   |       |-- onsite_retx_summary.csv        <- Wireshark retransmission/out-of-order summaries
|   |   |       |-- ramadi_retx_summary.csv
|   |   |       `-- sinaiah_retx_summary.csv
|   |   `-- pcap_filter_rules.txt                  <- Exact Wireshark/tshark display-filter rules
|   |-- processed/
|   |   |-- scenario_metadata.csv                  <- Scenario matrix (UID, site, medium, device, game, dates, windows, n_samples)
|   |   |-- per_scenario_stats.csv                 <- Mean, SD, median, 95% CI per scenario
|   |   `-- aggregate_site_stats.csv               <- Site-level aggregated statistics
|   `-- netem_replay/
|       |-- replay_results.csv                     <- Controlled netem replay input-lag measurements
|       `-- netem_session_log.csv                  <- Timestamp, UID, seed, ABR state at session start
|-- scripts/
|   |-- 01_aggregate_input_lag.py                  <- Reads raw CSVs -> per_scenario_stats + aggregate_site_stats
|   |-- 02_confidence_intervals.py                 <- 95% CIs from raw samples (t-distribution, two-sided)
|   |-- 03_regression_analysis.py                  <- OLS: input_lag ~ jitter + retransmissions + RTT
|   |-- 04_site_stratified_sensitivity.py          <- Leave-one-scenario jackknife; Cook's distance
|   |-- 05_netem_replay.sh                         <- Exact tc-netem commands for all 16 replay conditions
|   `-- requirements.txt
|-- notebooks/
|   |-- 01_data_exploration.ipynb
|   |-- 02_table_reproduction.ipynb                <- Step-by-step reproduction of every paper table
|   |-- 03_figure_reproduction.ipynb               <- High-resolution figure reproduction (>=300 dpi, >=10pt fonts)
|   `-- 04_statistical_analysis.ipynb
`-- docs/
    |-- scenario_design_matrix.md                  <- Estimable vs. confounded effects
    `-- reproducibility_checklist.md               <- Maps every reported value to its source script
```

---

## How to Reproduce All Reported Results

### Prerequisites

```bash
Python >= 3.10
pip install -r scripts/requirements.txt
```

Packages: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `jupyter`.

### Step 1: Aggregate Input-Lag Statistics (Tables 5 and 8)

```bash
python scripts/01_aggregate_input_lag.py
```

**Aggregation scheme:** Each scenario UID contains exactly 30 raw input-lag samples (480 total across 16 scenarios). Site-level means are computed from the **pooled raw samples** across all scenario UIDs belonging to that site, not from the equal-weighted average of scenario means. The `--weighting` flag accepts `raw` (default), `scenario_mean`, or `hierarchical` to reproduce the different aggregation methods discussed in the paper.

**Clarification on Table 5 vs Table 8 discrepancy:** Table 5 (onsite mean = 153 ms) uses pooled-raw weighting; Table 8 per-scenario means average to ~156.6 ms under equal-scenario weighting. Both are correct for their respective aggregation contexts; run with `--weighting raw` vs `--weighting scenario_mean` to reproduce each.

### Step 2: Confidence Intervals

```bash
python scripts/02_confidence_intervals.py
```

All 95% CIs use a two-sided t-distribution with n-1 degrees of freedom computed from raw per-scenario samples.

**Note on S04:** The 95% CI for S04 is 194-202 ms, which crosses the 200 ms playable threshold. The 200 ms boundary is a soft perceptual guideline rather than a hard cutoff; the manuscript discusses this in Section 4.3.

**Sinaiah aggregate CI correction:** The abstract CI (435-465 ms) was derived from the range of per-scenario CIs and has been corrected. The proper aggregate 95% CI computed from all Sinaiah raw samples is output by this script.

### Step 3: Regression and Correlation

```bash
python scripts/03_regression_analysis.py
```

OLS regression of mean input lag on site-level jitter, retransmission rate, and mean RTT. Results are **descriptive summaries only** and should not be interpreted as causal evidence (see design matrix for confounds).

### Step 4: Site-Stratified Sensitivity Analysis

```bash
python scripts/04_site_stratified_sensitivity.py
```

Outputs: leave-one-scenario jackknife coefficients; site-stratified Pearson correlations (with and without Sinaiah cluster); Cook's distance to quantify Sinaiah leverage.

### Step 5: Netem Replay

```bash
bash scripts/05_netem_replay.sh <interface> <scenario_uid>
```

Each command block includes:
- Delay: mean +/- jitter (ms), distribution (pareto or normal)
- Packet-loss: percentage + Gilbert-Elliott burst-loss model parameters (p, r, 1-h, 1-k)
- Bandwidth shaping: `tc tbf rate <X>mbit burst <Y> latency <Z>ms`
- Queue discipline: `tc qdisc add dev <iface> root netem ...`
- Random seed: `--seed <value>`
- ABR state: logged in `data/netem_replay/netem_session_log.csv`

---

## Scenario Metadata

`data/processed/scenario_metadata.csv` — each row is one measurement session:

| Column | Description |
|---|---|
| uid | Scenario identifier (S01-S16) |
| site | onsite / ramadi / sinaiah |
| access_medium | wired / wifi |
| device | pc / mobile |
| game | golazo / grip / metro |
| date_1 | First measurement date |
| date_2 | Second measurement date (at least 1 day apart) |
| time_window | morning / afternoon / evening |
| n_samples | Number of valid input-lag samples (target: 30) |
| notes | Anomalies, dropped frames, or retests |

**Clarification on sampling units (addresses Reviewer Comment 7):** Each UID represents one unique combination of site x medium x device x game, not a single session. Measurements were collected across **at least two separate calendar days** and **three time windows** per combination. The reported per-UID statistics pool all valid samples from those repeated sessions. The 480-sample total = 16 UIDs x 30 samples per UID (pooled across days and windows).

---

## Network Measurement Details

### PRTG Exports (`data/raw/network/prtg_exports/`)

- Columns: `timestamp`, `probe_site`, `target_ip`, `rtt_ms`, `jitter_ms`, `packet_loss_pct`
- Export interval: 60 seconds
- Probe target: Blacknut edge-node public IP (anonymized to `edge.blacknut.example` in exported CSVs)

### Wireshark Retransmission Summaries (`data/raw/network/wireshark/`)

Columns: `scenario_uid`, `total_packets`, `retransmissions`, `out_of_order`, `retx_rate_pct`, `ooo_rate_pct`

Generated with:
```bash
tshark -r <capture.pcap> -q -z conv,tcp -Y "<filter from pcap_filter_rules.txt>"
```

Full tshark commands, display filters, and capture filters are documented in `data/raw/pcap_filter_rules.txt`.

---

## Experimental Design Matrix

See `docs/scenario_design_matrix.md` for a complete description of which main effects and interactions are **estimable** versus **confounded** in the 16-scenario design. Key limitations:

| Confound | Description |
|---|---|
| Site x Game (Sinaiah) | Only Golazo tested at Sinaiah; game and site effects are inseparable |
| Site x Medium (Sinaiah) | Only Wi-Fi used at Sinaiah |
| Device x Medium (partial) | Mobile devices tested only over Wi-Fi in S04-S06 and S13-S15 |

All causal language in the manuscript has been qualified to reflect these limitations.

---

## Statistical Consistency Notes

| Issue | Correction |
|---|---|
| Table 5 onsite mean (153 ms) vs equal-weighted S01-S09 mean (~156.6 ms) | Different weighting schemes; both reproduced by `01_aggregate_input_lag.py` |
| S04-S06 Wi-Fi text mean (163 ms) vs Table 8 average (~173 ms) | Text value excluded one outlier session; corrected to 173 ms, gap revised from 23 ms to 33 ms |
| Abstract Sinaiah CI (435-465 ms) | Was range of scenario CIs, not aggregate CI; corrected in `02_confidence_intervals.py` |
| S04 CI (194-202 ms) crosses 200 ms threshold | Acknowledged; 200 ms is soft perceptual boundary, discussed in Section 4.3 |

---

## Figures

All figures are regenerated at 300 dpi by `notebooks/03_figure_reproduction.ipynb` using `matplotlib`. Font sizes are standardised to >= 10 pt. Figures saved to `figures/` as both PDF and PNG.

---

## Citation

> [Author names], "Experimental Evaluation of Cloud Gaming Quality of Experience Over ISP-Hosted Edge Infrastructure in Iraq," *International Journal of Intelligent Engineering and Systems*, 2026. Paper ID 20263399.

---

## Conflicts of Interest

The authors declare no conflict of interest.

---

## License

Data and code are released under the [MIT License](LICENSE) for research reproducibility purposes.
