# Prediction Market–Augmented Risk Modelling — Case Studies

Supplementary code and data for the KU Leuven Master's Thesis:
**"Prediction Market–Augmented Scenario Analysis for Tail-Risk Hedging"**

Three self-contained Jupyter notebooks implement the full empirical methodology — factor model, VAR/SVAR/ML backtesting, bootstrap CVaR, and hedge sizing — across three distinct case studies.

---

## Case Studies

| Notebook | Market | Prediction Market Signal | Key Risk Metric |
|---|---|---|---|
| `Energy_Lower_Freq_Nuclear.ipynb` | Belgian electricity (EPEX spot) | Nuclear availability futures (Kalshi) | CVaR₉₅ long/short (EUR) |
| `Argentina.ipynb` | MERV / LLA equity | Argentine election contracts (Polymarket) | CVaR₉₅ long/short (USD) |
| `AGI.ipynb` | Tech/AI equities | AGI timeline contracts (Metaculus/Polymarket) | CVaR₉₅ long/short (USD) |

---

## Setup

**Python 3.11 recommended.**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

Then open the desired notebook and run all cells top-to-bottom.

---

## Data Files

All input data is included in this repository. No downloads are needed to run any notebook.

### Belgian Electricity (`Energy_Lower_Freq_Nuclear.ipynb`)
| File | Description |
|---|---|
| `GUI_ENERGY_PRICES_202412312300-202512312300.csv` | EPEX Spot day-ahead electricity prices (Dec 2024 – Dec 2025) |
| `Belgium 2025 hourly load.csv` | ENTSO-E hourly electricity load (2025) |
| `belgium 2026 hourly load.csv` | ENTSO-E hourly electricity load (2026) |
| `NuclearDetonation.csv` | Kalshi nuclear availability prediction market data |
| `daily_aligned_with_two_pm_2025.csv` | Daily electricity price aligned with PM signals |
| `daily_aligned_with_two_pm_2025_pct_changes.csv` | Percentage-change version of the above |
| `hourly_aligned_with_pm_window.csv` | Hourly electricity aligned with PM window |
| `hourly_aligned_with_pm_window_differences.csv` | First-differenced version |
| `hourly_aligned_with_pm_window_pct_changes.csv` | Percentage-change version |
| `pm_hourly_last_month_pipeline_wide.csv` | Prediction market hourly pipeline (wide format) |
| `pm_two_markets_daily_2025.csv` | Dual-market daily PM data (2025) |
| `pm_russia_ukraine_peace_parlay_hourly_last_month.csv` | Russia-Ukraine peace contract (hourly) |
| `pm_russia_ukraine_peace_parlay_hourly_last_month_wide.csv` | Wide-format version of the above |

### Argentina (`Argentina.ipynb`)
| File | Description |
|---|---|
| `Argentina.csv` | MERV index returns and LLA election contract prices |

### AGI (`AGI.ipynb`)
| File | Description |
|---|---|
| `agi-timeline-forecasts.csv` | AGI timeline forecast aggregates (Metaculus/community) |

---

## Methodology Summary

Each notebook follows the same five-step pipeline:

1. **Factor model** — Training-window-only PCA (first 80 % of data, ≥ 30 obs) to extract idiosyncratic returns, preventing look-ahead bias in factor loadings.

2. **Backtesting** — Expanding-window cross-validation with adaptive minimum training window (`max(30, n_obs // 3)`). Models: VAR (with time-to-resolution as exogenous regressor), SVAR, VECM, Ridge, ElasticNet, Random Forest, Extra Trees, Gradient Boosting, SVR, GARCH, Foundation Model.

3. **Scenario branching** — Empirical conditional transition probabilities (with Laplace smoothing) drive a binomial tree over the PM contract's remaining life, yielding terminal scenario paths.

4. **Bootstrap CVaR** — Block bootstrap (block length √n) on out-of-sample residuals (80/20 holdout) produces both left-tail CVaR₉₅ (adverse for long/producer exposure) and right-tail CVaR₉₅ (adverse for short/consumer exposure).

5. **Hedge sizing** — CVaR-scaled hedge notional in the case-study currency (EUR for Belgium; USD for Argentina/AGI), with rolling CVaR₈₀ as the position-sizing signal.

---

## Repository Structure

```
.
├── README.md
├── requirements.txt
├── .gitignore
│
├── Energy_Lower_Freq_Nuclear.ipynb   # Belgian electricity case study
├── Argentina.ipynb                   # Argentine election case study
├── AGI.ipynb                         # AGI timeline case study
│
├── *.csv                             # Input data files (see table above)
├── Images/                           # Factor model diagnostic plots
└── *.png                             # Analysis output charts
```

The `archive/` folder contains superseded notebooks, development scripts, and supplementary data files that are not required to reproduce the main results.

---

## Output Plots

Notebooks generate all figures inline. Key outputs saved to the root:

| File | Description |
|---|---|
| `windowsize.png` | Training window sensitivity |
| `rollingcvar.png` | Rolling CVaR₈₀ time series |
| `ImpulseResp.png` | SVAR impulse response functions |
| `localIRF.png` | Local linear IRF |
| `Impactheatmap.png` | PM-shock impact heatmap |
| `argentinapmshocksens.png` | Argentina PM shock sensitivity |
| `argcvar.png` | Argentina CVaR distribution |
| `agihist.png` | AGI probability histogram |
| `treesim.png` / `AGItreesim.png` | Binomial tree scenario paths |
| `Images/` | Belgium factor model diagnostics |

---

## Notes

- The notebooks fetch some live data (weather via Open-Meteo, equity prices via yfinance). An internet connection is required for those cells; all prediction market and electricity data is pre-loaded from the CSVs.
- API keys are **not** included and **must not** be committed. If you have a Polymarket or Kalshi key, set it as an environment variable before running.
- The `archive/private/` folder is listed in `.gitignore` and will never be pushed.
