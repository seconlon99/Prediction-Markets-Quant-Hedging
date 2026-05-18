# Notebook Restructuring Instructions
## `Energy_Lower_Freq_Nuclear.ipynb`

---

## Guiding Principle

The notebook should run cleanly from top to bottom with data flowing in one direction. Every cell's inputs must exist before it runs. Structural, validation, and diagnostic cells should sit inside the section they logically belong to, not at the top or bottom as orphaned fallbacks.

The proposed section order is:

```
0)  Environment Setup
1)  Electricity Data Preparation
2)  Prediction-Market and Weather Inputs
3)  Data Alignment and Feature Construction
4)  Factor Model and Idiosyncratic Returns
5)  Exploratory Data Analysis
6)  Predictive Modeling and Model Selection
7)  Rolling CVaR of Idiosyncratic Returns
8)  Branching Simulation and Scenario Analysis
9)  Hedge Sizing
```

---

## PART A — Cells to Delete

Delete the following cells entirely. They are either unreachable fallbacks, pure debug output, or exact duplicates of cells that appear later in the correct position.

| Cell index | Cell id | Reason |
|---|---|---|
| 0 | `27b473e3` | Fallback that reads `sim_df_all` before it is built; logic is duplicated in the robust handoff cell |
| 1 | `968fd34c` | Fallback `ts_daily` loader placed before any data exists; covered by Cell 24 in the correct position |
| 2 | `942e8ff5` | Fallback `hourly_aligned` loader placed before alignment runs; covered by Cell 18 |
| 48 | `005f931d` | Exact duplicate of `ts_daily` construction already in Cell 24 (`37a1f22d`) |
| 53 | `6e0888fa` | Bare `display(ts_daily.head())` debug cell with no analytical value |
| 54 | `0950ff07` | Near-duplicate of Cell 51 (`83edcc1d`); both run one-step simulation validation; keep Cell 51, delete this one |

After these deletions the notebook will have 52 cells. All subsequent index references in this document use the **post-deletion** numbering.

---

## PART B — Cells to Move

Execute each move in the order listed. After each move, adjust the cell's opening comment to match its new position.

### Move 1 — Post-handoff consistency audit into Section 4

**Cell to move:** `f03ec6e0` ("Post-handoff consistency audit")
**Current position:** last cell in the notebook
**Move to:** immediately after the robust factor-model handoff cell `3344c9b5`

This cell checks `BEL_returns`, `BEL_idiosyncratic`, and `BEL_fitted` in `hourly_aligned`. These columns are produced by `3344c9b5`, so the audit must follow it directly in Section 4.

---

### Move 2 — Factor model comparison into Section 4

**Cell to move:** `e38ba9b8` ("Compare daily factor-model explanatory power: weather-only vs weather+load")
**Current position:** after the Section 9 nuclear reporting cell
**Move to:** immediately after the post-handoff consistency audit (`f03ec6e0`), still inside Section 4

This cell consumes `hourly_aligned` and compares PCA specifications. It is a factor-model diagnostic and belongs in Section 4, not after the scenario analysis.

---

### Move 3 — Rolling CVaR into Section 7

**Cells to move:** markdown `rolling-cvar-md` and code `rolling-cvar-code` (currently cells 33–34, in Section 5a)
**Move to:** a new Section 7 block, placed immediately after the final model selection cell `57c99b87` and its out-of-sample R² cell `a84a40c5`

The rolling CVaR plot is a risk diagnostic that contextualises the model output. It belongs after model selection is complete, not inside the predictive modeling section before model fitting has happened.

---

### Move 4 — Feature importance and counterfactual sensitivity into Section 8

**Cell to move:** `24b37b7e` (feature importance, counterfactual sensitivity, `feat_imp` table)
**Current position:** near the bottom after the Section 11 markdown
**Move to:** immediately after the branching simulation cell `6521b74f` and its OOS R² cell `a84a40c5`

This cell reads `sim_df_all` and `best_models`, both produced by `6521b74f`. It belongs directly after simulation setup, before the tree visualisation.

---

### Move 5 — Simulation model one-step validation into Section 8

**Cell to move:** `83edcc1d` (one-step directional accuracy diagnostic for simulation model)
**Current position:** after the Section 10 hedge sizing markdown
**Move to:** immediately after the feature importance cell (`24b37b7e`), still in Section 8

---

### Move 6 — `time_to_expiry` construction into Section 8

**Cell to move:** `fc9b48ee` ("Ensure ts_daily has time_to_expiry column")
**Current position:** second-to-last cell at the bottom
**Move to:** immediately after the branching simulation cell `6521b74f`, before feature importance

`fc9b48ee` computes `time_to_expiry` using `sim_df_all`, which is first created in `6521b74f`. It must run before the feature importance cell that uses it.

---

## PART C — Section Markdown Cells

Replace all existing section markdown cells with the cells defined below. Delete all old `##` and `###` heading cells first, then insert the new ones at the positions specified.

---

### New Cell C-1 — Notebook title (replace cell `04cd1ce1`)

Position: first cell in the notebook (index 0 after deletions and before new inserts)

```markdown
# Nuclear Energy Pipeline (Lower Frequency)

End-to-end daily pipeline: Belgian electricity data preparation, nuclear prediction-market integration, factor-model residualisation, predictive model comparison, scenario simulation, CVaR risk diagnostics, and hedge sizing.

**Run order:** Execute all cells top to bottom. Each section depends only on outputs from sections above it.
```

---

### New Cell C-2 — Section 1 heading (replace cell `1191a478`)

Position: immediately before cell `2d8b0c68`

```markdown
## 1) Electricity Data Preparation

Load the ENTSO-E day-ahead Belgium price CSV, aggregate quarter-hourly observations to daily frequency, retain only days with complete intraday coverage, and build a balanced daily panel.
```

---

### New Cell C-3 — Section 2 heading (replace cell `f610d9ac`)

Position: immediately before cell `2065d869`

```markdown
## 2) Prediction-Market and Weather Inputs

Load the nuclear prediction-market daily CSV (Polymarket "Nuclear weapon detonation in 2025?"), retrieve Belgium weather data from Open-Meteo, and merge all inputs into the canonical `hourly_aligned` daily panel.
```

---

### New Cell C-4 — Section 3 heading (replace cell `bc2fe7b0`)

Position: immediately before cell `c6c834b8`

```markdown
## 3) Data Alignment and Feature Construction

Validate UTC alignment across electricity, PM, and weather sources. Construct differenced and percentage-change feature datasets for downstream modeling.
```

---

### New Cell C-5 — Section 4 heading (replace cell `eeef53d5`)

Position: immediately before cell `150d7020`

```markdown
## 4) Factor Model and Idiosyncratic Returns

Decompose Belgian electricity returns into a systematic weather-and-load component and an idiosyncratic residual. The residual series `BEL_idiosyncratic` is the target variable for all downstream modeling.
```

---

### New Cell C-6 — Section 4a sub-heading (replace cell `08699377`)

Position: immediately before cell `1b065517`

```markdown
### 4a) Factor Model Validation

Assess PCA stability, residual autocorrelation (Ljung-Box, Durbin-Watson), heteroskedasticity (Breusch-Pagan, White, ARCH), and influence diagnostics. The post-handoff consistency audit and weather-vs-load comparison follow immediately below.
```

---

### New Cell C-7 — Section 4b sub-heading (replace cell `4206bd57`)

Position: immediately before cell `3344c9b5`

```markdown
### 4b) Robust Factor-Model Handoff

Rebuild the Belgium idiosyncratic series using Huber robust regression to down-weight the 5 October 2025 outlier. Writes `BEL_idiosyncratic`, `BEL_fitted`, and `BEL_returns` back to `hourly_aligned` for all downstream cells.
```

---

### New Cell C-8 — Section 4c sub-heading (new, insert after `f03ec6e0`)

Position: immediately before cell `e38ba9b8` (now in Section 4 after the move)

```markdown
### 4c) Factor Model Comparison: Weather-Only vs Weather + Load

Compare PCA factor specifications to confirm that adding load variables provides defensible incremental explanatory power beyond weather alone, even when the marginal R² gain is small.
```

---

### New Cell C-9 — Section 4d sub-heading (replace cell `12546c70`)

Position: immediately before cell `b8079a32`

```markdown
### 4d) Export Main-Text Figures

Export the scree plot and residual diagnostics panel to `Images/` for inclusion in the thesis write-up.
```

---

### New Cell C-10 — Section 5 heading

Position: immediately before cell `3ec594b2`

```markdown
## 5) Exploratory Data Analysis

Examine the marginal distributions, autocorrelation structure, and stationarity of `BEL_idiosyncratic` and `PM_nuclear_returns` before model fitting. ADF and KPSS tests determine whether standard lag-based modeling is appropriate for each series.
```

---

### New Cell C-11 — Section 6 heading (replace cell `be8aa365` and cell `261752b0`)

Delete both `be8aa365` ("## 5) Daily Predictive Modeling") and `261752b0` ("## 6) Single-Market Attribution"). Replace with:

Position: immediately before cell `06008c54`

```markdown
## 6) Predictive Modeling and Model Selection

Two-stage model comparison across VAR, SVAR, GARCH, and nine machine-learning specifications. Stage 1 is a fixed holdout bakeoff (RMSE, MAE, directional accuracy). Stage 2 is an expanding-window and rolling-window generalizability evaluation. The model with the best combined ranking is selected for simulation.
```

---

### New Cell C-12 — Section 6a sub-heading

Position: immediately before cell `06008c54`

```markdown
### 6a) Model Specification and VAR / ML Benchmark Fitting

Fit VAR, recursive SVAR, and all machine-learning candidate models on the joint `PM_nuclear_returns` → `BEL_idiosyncratic` series. Produces `ts_df` for the backtest cell.
```

---

### New Cell C-13 — Section 6b sub-heading (replace cell `6db47dbf`)

Replace markdown cell `6db47dbf` ("## 7) Backtesting Traditional vs ML Predictive Models"). The backtest is now a subsection of Section 6, not a standalone section.

Position: immediately before cell `03b0ed46`

```markdown
### 6b) Nuclear Single-Market Attribution and Impulse Response

Fit the best nuclear-only model and compute one-step shock sensitivity and multi-horizon IRF grids. Produces `separate_pm_performance`, `one_step_irf_sensitivity`, and `sensitivity_irf_grid` for downstream reporting.
```

---

### New Cell C-14 — Section 6c sub-heading

Position: immediately before cell `f425d08f`

```markdown
### 6c) Expanding-Window Backtest

One-step-ahead backtest across all candidate models under a fixed expanding-window scheme. Produces `backtest_metrics_energy_lowerfreq`.
```

---

### New Cell C-15 — Section 6d sub-heading

Position: immediately before cell `57c99b87`

```markdown
### 6d) Generalizability Validation and Final Model Selection

Expanding-window and rolling-window cross-validation on shortlisted models. The model with the best combined two-stage ranking is stored in `best_models` as the production simulation model.
```

---

### New Cell C-16 — Section 6e sub-heading

Position: immediately before cell `a84a40c5`

```markdown
### 6e) Out-of-Sample R² Summary

Report the OOS R² for the selected simulation model, evaluated over the full expanding-window backtest sequence.
```

---

### New Cell C-17 — Section 7 heading (replace the old `rolling-cvar-md` cell)

The old `rolling-cvar-md` content is now the heading for Section 7. Replace it with:

```markdown
## 7) Rolling CVaR of Idiosyncratic Returns

20-day rolling empirical CVaR₉₅ of `BEL_idiosyncratic`, plotted alongside `PM_nuclear_returns`. Serves as a time-varying tail-risk diagnostic: compare periods of elevated CVaR severity against PM return spikes to assess whether geopolitical risk signals coincide with fat-tailed electricity return regimes.
```

---

### New Cell C-18 — Section 8 heading (replace cell `18d6715d`)

Replace markdown cell `18d6715d` ("## 8) Empirical Branching Trees").

```markdown
## 8) Branching Simulation and Scenario Analysis

Forward scenario generation using the selected SVR model. Includes simulation setup, feature importance, one-step validation, branching tree visualisation, and terminal-node CVaR reporting.
```

---

### New Cell C-19 — Section 8a sub-heading

Position: immediately before cell `6521b74f`

```markdown
### 8a) Simulation Setup and Forward Paths

Build `sim_df_all`, fit the production SVR model, run the two-stage branching simulation, and compute `scenario_summary` with bootstrap CVaR₉₅ at each terminal node.
```

---

### New Cell C-20 — Section 8b sub-heading

Position: immediately before cell `fc9b48ee` (now moved here)

```markdown
### 8b) Feature Importance and Counterfactual Sensitivity

Rank predictor importances in the fitted simulation model and compute a one-step counterfactual sensitivity sweep over the PM return lag to quantify the marginal effect of the nuclear signal on next-period electricity return forecasts.
```

---

### New Cell C-21 — Section 8c sub-heading

Position: immediately before cell `3119befe`

```markdown
### 8c) Branching Tree Visualisation

Plot the two-stage empirical branching tree with cumulative abnormal return (CAR) and bootstrap CVaR₉₅ projections at each terminal node.
```

---

### New Cell C-22 — Section 8d sub-heading (replace cell `4f82683a`)

Replace markdown cell `4f82683a` ("## 9) Nuclear Market Analysis").

```markdown
### 8d) Scenario Outputs and Terminal Node Reporting

Path-level branch summaries, terminal-node CAR and CVaR₉₅ table, one-step IRF sensitivity, and multi-horizon shock grid for the nuclear pipeline.
```

---

### New Cell C-23 — Section 9 heading (replace cell `b45d8f08`)

Replace markdown cell `b45d8f08` ("## 10) Deterministic Hedge Sizing").

```markdown
## 9) Hedge Sizing

Translate the scenario-weighted downside distribution into a hedge-sizing recommendation. Reports both the point-estimate notional (based on CAR) and the CVaR₉₅-informed notional (based on bootstrap tail risk) for comparison.
```

---

## PART D — Delete Orphaned Section Headings

After all moves and replacements above, the following markdown cells will have no code cells beneath them or will duplicate section content. Delete them:

| Cell id | Content | Reason |
|---|---|---|
| `4065539e` | "## 11) Time-Series Generalization Check" | Section no longer exists; content absorbed into Section 6d |
| `rolling-cvar-md` | Old "## 5a) Rolling CVaR" heading | Replaced by new Section 7 heading (C-17) |

---

## PART E — Opening Comment Updates

After all moves, update the first `#` comment line inside each relocated code cell to match its new section. Use the pattern `# Section X) Description`.

| Cell id | New opening comment |
|---|---|
| `f03ec6e0` | `# Section 4a) Post-handoff consistency audit` |
| `e38ba9b8` | `# Section 4c) Factor model comparison: weather-only vs weather + load` |
| `rolling-cvar-code` | `# Section 7) Rolling empirical CVaR95 of BEL_idiosyncratic (20-day window)` |
| `24b37b7e` | `# Section 8b) Feature importance and counterfactual sensitivity` |
| `83edcc1d` | `# Section 8b) Simulation model one-step validation` |
| `fc9b48ee` | `# Section 8b) Ensure ts_daily has time_to_expiry column` |

---

## PART F — Final Cell Order Verification

After all edits, the notebook should contain cells in this exact top-to-bottom sequence. Cell ids are shown; markdown cells are labelled `[MD]`.

```
[MD] C-1   Notebook title
[MD] C-2   ## 1) Electricity Data Preparation
     2d8b0c68   Load electricity CSV
     475b6167   Daily average
     3cef54cc   Balanced panel
     75d27b6b   Plot electricity prices
[MD] C-3   ## 2) Prediction-Market and Weather Inputs
     2065d869   Belgium weather
     85e696b2   Weather compatibility frame
     584c6e1f   PM hourly CSV load
     e5ed77e0   PM retry alias
     01249db8   PM schema debug
     e864bffd   Nuclear daily PM import
     4e1baf98   Save + align two-market PM data
     729b6207   Plot PM yes/no prices
     dd2e7178   UTC audit + aligned dataset
[MD] C-4   ## 3) Data Alignment and Feature Construction
     c6c834b8   Differenced dataset
     5261a6f2   Pct-change dataset
[MD] C-5   ## 4) Factor Model and Idiosyncratic Returns
     150d7020   PCA factor model construction
     37a1f22d   ts_daily canonical prep
[MD] C-6   ### 4a) Factor Model Validation
     1b065517   Comprehensive validation
[MD] C-7   ### 4b) Robust Factor-Model Handoff
     3344c9b5   Huber robust regression handoff
     f03ec6e0   Post-handoff consistency audit   ← MOVED from bottom
[MD] C-8   ### 4c) Factor Model Comparison
     e38ba9b8   Weather-only vs weather+load     ← MOVED from Section 9 area
[MD] C-9   ### 4d) Export Main-Text Figures
     b8079a32   Export scree + residual figures
[MD] C-10  ## 5) Exploratory Data Analysis
     3ec594b2   EDA: ACF, stationarity, distributions
[MD] C-11  ## 6) Predictive Modeling and Model Selection
[MD] C-12  ### 6a) Model Specification and VAR / ML Benchmark Fitting
     06008c54   VAR, SVAR, ML models → ts_df
[MD] C-13  ### 6b) Nuclear Single-Market Attribution and Impulse Response
     03b0ed46   Nuclear diagnostics → separate_pm_performance, IRF outputs
[MD] C-14  ### 6c) Expanding-Window Backtest
     f425d08f   Backtest → backtest_metrics_energy_lowerfreq
[MD] C-15  ### 6d) Generalizability Validation and Final Model Selection
     57c99b87   Generalizability + best_models
[MD] C-16  ### 6e) Out-of-Sample R² Summary
     a84a40c5   OOS R²
[MD] C-17  ## 7) Rolling CVaR of Idiosyncratic Returns
     rolling-cvar-code   Rolling CVaR plot and summary   ← MOVED from Section 5a
[MD] C-18  ## 8) Branching Simulation and Scenario Analysis
[MD] C-19  ### 8a) Simulation Setup and Forward Paths
     6521b74f   Branching simulation → sim_df_all, scenario_summary
[MD] C-20  ### 8b) Feature Importance and Counterfactual Sensitivity
     fc9b48ee   time_to_expiry construction          ← MOVED from bottom
     24b37b7e   Feature importance + counterfactual  ← MOVED from bottom
     83edcc1d   Simulation model one-step validation ← MOVED from Section 10 area
[MD] C-21  ### 8c) Branching Tree Visualisation
     3119befe   Tree plot
[MD] C-22  ### 8d) Scenario Outputs and Terminal Node Reporting
     6a985b21   Nuclear reporting block
[MD] C-23  ## 9) Hedge Sizing
     bfb7b6d2   Hedge sizing with CVaR comparison
```

Total cells after restructuring: **48** (52 post-deletion minus 4 old markdown cells replaced by new ones).

---

## PART G — Checks to Run After Restructuring

Run the full notebook top-to-bottom and confirm:

1. No `NameError` or `ValueError` for missing globals at any cell.
2. `ts_daily` is constructed by cell `37a1f22d` and is available from that point onward without any fallback being triggered.
3. `separate_pm_performance` exists before cell `6521b74f` runs (produced by `03b0ed46`).
4. `backtest_metrics_energy_lowerfreq` exists before cell `57c99b87` runs (produced by `f425d08f`).
5. `sim_df_all` and `scenario_summary` exist before cell `3119befe` runs (produced by `6521b74f`).
6. The rolling CVaR cell produces `rolling_cvar_df` and the two-panel figure without error.
7. The hedge sizing cell prints both the point-estimate table and the CVaR₉₅ comparison table.
