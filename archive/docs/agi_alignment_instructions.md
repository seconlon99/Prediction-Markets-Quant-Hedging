# Copilot Instructions: Align AGI Notebook with Energy Notebook
## File: `AGI.ipynb`

---

## Overview

The AGI notebook has a materially different data structure from the Energy and Argentina cases. The prediction market signal is an aggregated expected year of AGI arrival (measured in years), not a binary event probability, and there is no contract resolution date. There is therefore **no `time_to_expiry` feature**. In its place, a sequential **time index** (`time_idx`) is added as a covariate — this gives models a way to track long-run changes in the relationship between ARTY returns and AGI expectations over the sample, compensating for the absence of a forward-looking clock.

The AGI notebook also contains a unique structural analysis block (Sign-restricted SVAR, Cholesky VAR robustness, and Local Projections) that has no counterpart in the Energy notebook. This block is methodologically valuable and is retained, but moved to a clearly labelled structural analysis section before the predictive backtest.

Changes fall into five categories:
1. **Delete** cells that are orphaned, purely debug, or create interactive widget dependencies
2. **Move** the structural analysis block to its correct position
3. **Add** section markdown headings
4. **Update** existing code cells to match methodology
5. **Add** new code cells for missing analytical steps

All cell index references are for the **current** `AGI.ipynb` (39 cells, indexed 0–38). Execute deletions first, then moves, then inserts so indexes remain valid.

---

## PART A — Cells to Delete

| Index | Cell id | Reason |
|---|---|---|
| 5 | `f6f72787` | Plots only the first 20 observations; the EDA suite (cells 7–13) provides a complete distributional analysis that makes this redundant |
| 29 | `dfb90c6a` | `ipywidgets` horizon dropdown creates an interactive dependency that breaks non-interactive execution and is fragile in export/papermill contexts. Replace with a plain variable assignment (see Part E, cell E-0) |

After deletion the notebook has **37 cells**, indexed 0–36.

---

## PART B — Cells to Move

### Move 1 — Sign-restricted SVAR and robustness overlay into structural analysis

**Cells to move:** `d1ad0396` (markdown), `5ae19b5c` (Sign-SVAR code), `d30d1594` (markdown), `07c3c605` (robustness overlay code)

**Current position:** after the backtest cell and simulation engine (currently cells 23–26 post-deletion)

**Move to:** immediately after cell `36d21d34` ("Compact model comparison summary"), which is the last cell of the structural analysis block (currently cell 19 post-deletion)

These four cells consume `var_fit`, `irf_obj`, and `lp_irf`, all of which are produced in the structural analysis block. They are structural diagnostics, not simulation outputs, and placing them after the backtest incorrectly implies they depend on ML model selection.

---

## PART C — Section Markdown Cells to Add

Insert the following markdown cells at the positions specified. All positions are relative to the **post-deletion, post-move** cell order.

### C-1 — Notebook title (new cell 0, before everything)

```markdown
# AGI Timeline Pipeline

End-to-end daily pipeline: ARTY ETF factor-model residualisation, AGI timeline signal construction, structural analysis, predictive model comparison, scenario simulation, CVaR risk diagnostics, and hedge sizing.

**Signal note:** The prediction market signal is the cross-platform average expected year of AGI arrival (Metaculus and Manifold), expressed as a log-difference. There is no binary resolution date, so `time_to_expiry` is replaced by a sequential `time_idx` covariate that captures long-run structural drift in the AGI–ARTY relationship over the sample.

**Run order:** Execute all cells top to bottom. Each section depends only on outputs from sections above it.
```

---

### C-2 — Section 1 heading (insert before cell `46f3623b`)

```markdown
## 1) Asset Data Import

Download ARTY ETF price history via yfinance for the April 2024 – January 2026 window.
```

---

### C-3 — Section 2 heading (insert before cell `8b152007`)

```markdown
## 2) Factor Model and Idiosyncratic Returns

Decompose ARTY log returns into a systematic technology-and-rates component and an idiosyncratic residual. Factors: Nasdaq-100 (^NDX), global equities (ACWI), and US 10-year rates (^TNX). PCA on standardised factor returns extracts components explaining at least 95% of factor variance. Huber robust regression (ε = 1.35) is used to limit the influence of early high-volatility observations.
```

---

### C-4 — Section 2a sub-heading (insert after the factor model code cell and before the new validation cell described in Part E)

```markdown
### 2a) Factor Model Validation

Residual diagnostics: Ljung-Box serial correlation, Breusch-Pagan heteroskedasticity, and Cook's distance influence analysis. Confirms `ARTY_idiosyncratic` is suitable as a downstream modeling target.
```

---

### C-5 — Section 3 heading (insert before cell `ab45be53`)

```markdown
## 3) AGI Timeline Signal Construction

Load the AGI timeline forecast CSV (Good Heart Labs aggregation of Metaculus and Manifold sources). Filter to April 2024 onward. Compute `avg agi prediction` as the cross-platform mean expected year of AGI arrival.
```

---

### C-6 — Section 4 heading (insert before cell `91ff5d1f`)

```markdown
## 4) Data Alignment and Feature Construction

Align AGI timeline forecasts with ARTY idiosyncratic returns on a common daily date index. Compute `avg agi prediction log diff` as the primary signal. Add `time_idx` (sequential integer from 0 at the start of the overlapping sample) as an auxiliary covariate to capture long-run structural drift in the absence of a contract resolution clock.
```

---

### C-7 — Section 5 heading (insert before cell `9850faaa`, replacing its existing `##` heading)

Delete the existing markdown cell `9850faaa` and replace it with:

```markdown
## 5) Exploratory Data Analysis

Distributional diagnostics, ACF/PACF, prewhitening-based cross-correlation, stationarity battery (ADF, Phillips-Perron, KPSS, Zivot-Andrews), structural break detection (CUSUM, binary segmentation), and ARCH diagnostics for `y_t` (ARTY residual return) and `x_t` (AGI log difference).
```

---

### C-8 — Section 6 heading (insert before cell `71aa7942`, replacing its existing `##` heading)

Delete the existing markdown cell `71aa7942` and replace it with:

```markdown
## 6) Structural Analysis: ARDL, VAR, Local Projections, and Sign-Restricted SVAR

Baseline model comparison using ARDL dynamic regression (AIC/BIC lag selection — valid here as all three are OLS or likelihood-based with countable parameters), reduced-form VAR with impulse responses, Local Projections, and sign-restricted SVAR. These structural diagnostics characterise the dynamic relationship between the AGI signal and ARTY returns before the predictive backtest.
```

---

### C-9 — Section 7 heading (insert before cell `517ac764`, replacing its existing `##` heading)

Delete the existing markdown cell `517ac764` and replace it with:

```markdown
## 7) Predictive Modeling and Model Selection

Two-stage model comparison across VAR, SVAR, VECM, GARCH, and nine machine-learning specifications. Stage 1 is a fixed holdout bakeoff (RMSE, MAE, directional accuracy). Stage 2 is expanding-window generalizability evaluation. The final model is selected by equal-weight sum of bakeoff and validation ranks. Result stored in `best_models`.
```

---

### C-10 — Section 7a sub-heading (insert before cell `c03507f4`, replacing the existing `##` heading in cell `517ac764`)

```markdown
### 7a) VAR / SVAR / VECM Benchmark Fitting

Fit VAR, SVAR, and VECM as traditional benchmarks. VAR and SVAR lag orders are selected by holdout RMSE (not BIC) for cross-model consistency. VECM cointegration rank is selected by Johansen trace test. These lag choices inform the expanding-window backtest in Section 7b.
```

---

### C-11 — Section 7b sub-heading (insert before cell `9cf9bf47`, replacing the existing `##` heading in cell `b14fd144`)

Delete markdown cell `b14fd144` and replace with:

```markdown
### 7b) Expanding-Window Backtest and Final Model Selection

One-step-ahead backtest across all 11 candidate models. Stage 1 bakeoff on a fixed holdout produces `bakeoff_summary`. Stage 2 expanding-window validation produces `generalization_summary` with composite rank. Final model stored in `best_models` using the canonical key schema.
```

---

### C-12 — Section 7c sub-heading (insert after the backtest cell, before the new OOS R² cell in Part E)

```markdown
### 7c) Out-of-Sample R² Summary

Report the OOS R² for the selected simulation model over the full expanding-window sequence.
```

---

### C-13 — Section 8 heading (insert before the new rolling CVaR cell in Part E)

```markdown
## 8) Rolling CVaR of Idiosyncratic Returns

20-day rolling empirical CVaR₉₅ of `ARTY_idiosyncratic`, plotted alongside the AGI log-difference signal. Serves as a time-varying tail-risk diagnostic: compare periods of elevated AGI expectation revision against periods of heavier downside tails in the ARTY residual.
```

---

### C-14 — Section 9 heading (insert before cell `26a44756`)

```markdown
## 9) Branching Simulation and Scenario Analysis

Forward scenario generation using the selected model. The branching mechanism applies 10th, 50th, and 90th percentile year-shifts from the observed AGI timeline distribution over the selected horizon. Three branches (advanced, central, severe\_delay) each split to three sub-branches, yielding nine terminal nodes. Bootstrap CVaR₉₅ is computed at each terminal node.
```

---

### C-15 — Section 9a sub-heading (insert before cell `26a44756`)

```markdown
### 9a) Simulation Engine and Forward Paths

Build `simulate_y_path_from_x_path`, the canonical prediction function. Includes bootstrap CVaR₉₅ function. Run the three-stage branching simulation and produce `scenario_summary`, `scenario_summary_by_market`, and `terminal_summary_by_market`.
```

---

### C-16 — Section 9b sub-heading (insert before the new feature importance cell in Part E)

```markdown
### 9b) Feature Importance and Counterfactual Sensitivity

Rank predictor importances in the fitted simulation model. For SVR, use permutation importance. Compute a one-step counterfactual sensitivity sweep over `x_t_lag1` to quantify the marginal effect of the AGI signal on next-period ARTY idiosyncratic return forecasts.
```

---

### C-17 — Section 9c sub-heading (insert before cell `7ed7928a`)

```markdown
### 9c) Distribution Diagnostics and Terminal Node Reporting

Terminal CAR and CVaR₉₅ table by AGI scenario branch. Distribution histogram of cumulative ARTY returns by scenario state.
```

---

### C-18 — Section 9d sub-heading (insert before cell `8ac88468`)

Delete the existing markdown cell `12cf417a` and replace with:

```markdown
### 9d) Branching Scenarios with Confidence Intervals and Sign Diagnostics

Scenario path visualisation with model residual confidence bands. Sign diagnostic table verifying that contemporaneous, lagged, and scenario-mapped effects are internally consistent.
```

---

### C-19 — Section 10 heading (insert before cell `9dc4d490`, replacing the existing `##` heading in cell `be22aa3c`)

Delete markdown cell `be22aa3c` and replace with:

```markdown
## 10) Hedge Sizing

Translate scenario-weighted downside into a hedge notional. The exposure convention (`long_price` for an ARTY holder harmed by falling prices) is set explicitly. Reports both the point-estimate notional (from CAR) and the CVaR₉₅-informed notional (from bootstrap tail risk).
```

---

## PART D — Updates to Existing Code Cells

### Update D-1 — Cell `8b152007` (Factor Model): Replace OLS with Huber regression

**Find and replace** the block:
```python
# OLS on orthogonal PCs: ARTY = alpha + gamma*PCs + eps
X_design = np.column_stack([np.ones(len(X_pca)), X_pca.to_numpy()])
coef = np.linalg.lstsq(X_design, y.to_numpy(), rcond=None)[0]
alpha = coef[0]
pc_loadings = pd.Series(coef[1:], index=pc_cols, name='loading')
ret_df.loc[X_pca.index, 'ARTY_fitted'] = X_design @ coef
ret_df.loc[X_pca.index, 'ARTY_idiosyncratic'] = y - ret_df.loc[X_pca.index, 'ARTY_fitted']
```

**With:**
```python
# Huber robust regression: ARTY ~ PCs
# epsilon=1.35 downweights observations beyond ~1.35 residual std deviations.
# This is important for ARTY which has an early high-volatility period in mid-2024
# that would dominate an OLS fit.
from sklearn.linear_model import HuberRegressor
huber = HuberRegressor(epsilon=1.35, alpha=1e-4, max_iter=2000)
huber.fit(X_pca.to_numpy(), y.to_numpy())

pc_loadings = pd.Series(huber.coef_, index=pc_cols, name='loading')
y_fitted = huber.predict(X_pca.to_numpy())
ret_df.loc[X_pca.index, 'ARTY_fitted'] = y_fitted
ret_df.loc[X_pca.index, 'ARTY_idiosyncratic'] = y.to_numpy() - y_fitted

factor_model_state = {
    'estimator': 'HuberRegressor',
    'estimator_params': {'epsilon': 1.35, 'alpha': 1e-4},
    'n_components': n_components,
    'explained_variance_ratio': explained_var_ratio.tolist(),
    'cumulative_explained_variance': cum_explained.tolist(),
    'pc_loadings': pc_loadings.to_dict(),
}
```

Also update the write-back block to match:
```python
df_etf.loc[X_pca.index, 'ARTY_fitted'] = ret_df.loc[X_pca.index, 'ARTY_fitted']
df_etf.loc[X_pca.index, 'ARTY_idiosyncratic'] = ret_df.loc[X_pca.index, 'ARTY_idiosyncratic']
```

---

### Update D-2 — Cell `91ff5d1f` (Feature Construction): Add `time_idx`

**At the end of the cell**, after `df_analysis["ARTY residual return"] = df_analysis["ARTY_idiosyncratic"]`, add:

```python
# time_idx: sequential integer from 0 at the start of the overlapping sample.
# Used in place of time_to_expiry (absent here — there is no resolution date).
# Gives models a way to track long-run structural drift in the AGI–ARTY
# relationship, compensating for the absence of a forward-looking clock.
# Note: time_idx is a purely ordinal feature; models that treat it as a
# continuous effect will impose a linear time trend.
df_analysis = df_analysis.copy()
df_analysis["time_idx"] = np.arange(len(df_analysis), dtype=float)

print(f"df_analysis columns: {df_analysis.columns.tolist()}")
print(f"time_idx range: 0 – {int(df_analysis['time_idx'].max())}")
display(df_analysis[["avg agi prediction log diff", "ARTY residual return", "time_idx"]].head())
```

---

### Update D-3 — Cell `63747632` (EDA setup): Add `time_idx` to `eda_df`

**Find:**
```python
eda_df = (
    df_analysis[["avg agi prediction log diff", "ARTY residual return"]]
    .dropna()
    .rename(columns={
        "avg agi prediction log diff": "x_t",
        "ARTY residual return": "y_t",
    })
    .copy()
)
```

**Replace with:**
```python
eda_df = (
    df_analysis[["avg agi prediction log diff", "ARTY residual return", "time_idx"]]
    .dropna()
    .rename(columns={
        "avg agi prediction log diff": "x_t",
        "ARTY residual return": "y_t",
    })
    .copy()
)
```

This ensures `time_idx` flows through to `model_df` (which is built from `eda_df` in cell `abf1049a`) and is available as a feature in all downstream models.

---

### Update D-4 — Cell `abf1049a` (Model setup): Include `time_idx` in `model_df`

**Find:**
```python
model_df = eda_df[["y_t", "x_t"]].dropna().copy()
```

**Replace with:**
```python
model_df = eda_df[["y_t", "x_t", "time_idx"]].dropna().copy()
```

---

### Update D-5 — Cell `c03507f4` (VAR/SVAR/VECM): Replace BIC with RMSE for cross-model lag selection

**Change the opening comment from:**
```python
# Benchmark criterion: BIC (primary), AIC (tie-break)
```
**To:**
```python
# VAR and SVAR lag order: selected by holdout RMSE for cross-model consistency.
# VECM cointegration rank: selected by Johansen trace test (not a model-selection
# criterion — it tests for cointegration, which is separate from predictive ranking).
# Note: BIC is used internally by ARDL in Section 6 because ARDL is OLS-based
# with a proper likelihood and countable parameters; that use is valid.
```

Also delete the markdown cell `517ac764` line that reads:
> "selects the downstream simulation model using information criteria (BIC primary, AIC tie-break)"

This is superseded by the Section 7 markdown heading added in C-9.

Then apply the same holdout-RMSE VAR lag selection update as in the Argentina instructions (Part D, Update D-2), adapting variable names from `ts_df` to match the AGI cell's existing variable (`ts_df`).

---

### Update D-6 — Cell `9cf9bf47` (Backtest): Add Lasso, `time_idx`, and two-stage structure

**Step 1: Add Lasso to the ML model candidates.**

Find the ML model candidates dict and add Lasso:
```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet
...
"Lasso": Pipeline([("scale", StandardScaler()), ("model", Lasso(alpha=0.01, max_iter=20000, random_state=42))]),
```

**Step 2: Add `time_idx` to the lagged feature matrix.**

In the `build_lagged_features` function (or equivalent feature-building block), after the loop that adds `x_t_lag{i}` and `y_t_lag{i}` columns, add:
```python
# time_idx is not lagged — use the current value at each step
if "time_idx" in bt_df.columns:
    row["time_idx"] = float(bt_df.loc[t, "time_idx"]) if hasattr(bt_df, "loc") else float(bt_df["time_idx"].iloc[t])
```

Ensure `feat_cols` includes `"time_idx"` so that the feature matrix is consistent between train and test.

**Step 3: Add two-stage structure and canonical `best_models` dict.**

At the end of the cell, after the existing `backtest_metrics_agi` summary and `best_model_name` assignment, add:

```python
# ============================================================
# Two-stage model selection (canonical schema matching Energy notebook)
# ============================================================
bakeoff_summary = (
    backtest_metrics_agi.groupby("model", as_index=False)
    .agg(bakeoff_best_rmse=("rmse", "min"), bakeoff_best_mae=("mae", "min"),
         bakeoff_directional_accuracy=("directional_accuracy", "max"),
         family=("family", "first"))
)
bakeoff_summary["bakeoff_rank"] = bakeoff_summary["bakeoff_best_rmse"].rank(ascending=True, method="min")

generalization_summary = (
    backtest_metrics_agi.groupby("model", as_index=False)
    .agg(mean_rmse=("rmse", "mean"),
         mean_directional_accuracy=("directional_accuracy", "mean"),
         family=("family", "first"))
)
generalization_summary["rank_rmse"] = generalization_summary["mean_rmse"].rank(ascending=True, method="min")
generalization_summary["rank_dir"] = generalization_summary["mean_directional_accuracy"].rank(ascending=False, method="min")
generalization_summary["composite_rank_score"] = generalization_summary["rank_rmse"] + generalization_summary["rank_dir"]
generalization_summary["validation_rank"] = generalization_summary["composite_rank_score"].rank(ascending=True, method="min")

selection_summary = bakeoff_summary.merge(
    generalization_summary[["model", "validation_rank", "composite_rank_score"]],
    on="model", how="left"
)
selection_summary["final_rank_score"] = selection_summary["bakeoff_rank"] + selection_summary["validation_rank"]
selection_summary = selection_summary.sort_values("final_rank_score").reset_index(drop=True)

best_final_row = selection_summary.iloc[0]
best_final_model = str(best_final_row["model"])

best_models = {
    "bakeoff_best_model": bakeoff_summary.sort_values("bakeoff_rank").iloc[0]["model"],
    "validation_best_model": generalization_summary.sort_values("validation_rank").iloc[0]["model"],
    "selected_model_for_simulation": best_final_model,
    "production_model_name": best_final_model,
    "selected_model_family": str(best_final_row.get("family", "Unknown")),
    "final_model_selection_source": "combined_bakeoff_validation_rank",
    "bakeoff_summary": bakeoff_summary.copy(),
    "generalization_summary": generalization_summary.copy(),
    "selection_summary": selection_summary.copy(),
}

print(f"\nFinal selected model: {best_final_model}")
print("\nSelection summary:")
display(selection_summary[["model", "family", "bakeoff_rank", "validation_rank", "final_rank_score"]].head(10))
```

---

### Update D-7 — Cell `26a44756` (Simulation engine): Add bootstrap CVaR, `time_idx`, and canonical output schema

**Step 1: Update `simulate_y_path_from_x_path` to include `time_idx`.**

In the feature construction loop inside the simulation engine, after adding `x_t_lag{i}` and `y_t_lag{i}`, add:
```python
# time_idx: use the current trailing value and increment by step
if "time_idx" in ts_engine.columns:
    current_tte = float(ts_engine["time_idx"].iloc[-1]) + float(step_i + 1)
    row["time_idx"] = current_tte
```

Also ensure `feat_cols` is consistent with what was used in training.

**Step 2: Add `simulate_y_path_bootstrap` function.**

After the definition of `simulate_y_path_from_x_path`, add:

```python
def simulate_y_path_bootstrap(x_future, n_bootstrap=500, alpha=0.95, rng_seed=42):
    """
    Bootstrap residual simulation around the point-prediction path.
    Returns (point_path, cvar_alpha, boot_terminal_cars).
    Residuals are drawn from in-sample fit errors — this understates
    true out-of-sample uncertainty. Treat CVaR as an indicative lower bound.
    """
    point_path = simulate_y_path_from_x_path(x_future)

    # In-sample residuals
    X_is, y_is = [], []
    n_lags = getattr(simulate_y_path_from_x_path, '_n_lags', 3)
    train_data = ts_engine.copy()
    x_hist = train_data["x_t"].astype(float).tolist()
    y_hist = train_data["y_t"].astype(float).tolist()
    tti_hist = train_data["time_idx"].astype(float).tolist() if "time_idx" in train_data.columns else None

    for t in range(n_lags, len(train_data)):
        row = {}
        for lag in range(1, n_lags + 1):
            row[f"x_t_lag{lag}"] = float(x_hist[t - lag])
            row[f"y_t_lag{lag}"] = float(y_hist[t - lag])
        if tti_hist:
            row["time_idx"] = float(tti_hist[t])
        X_is.append(row)
        y_is.append(float(y_hist[t]))

    feat_cols_is = list(X_is[0].keys())
    import pandas as _pd
    X_is_df = _pd.DataFrame(X_is, columns=feat_cols_is)
    y_is_arr = np.array(y_is, dtype=float)

    try:
        residuals = y_is_arr - model_fitted.predict(X_is_df)
    except Exception:
        return point_path, float("nan"), np.array([])

    rng = np.random.default_rng(rng_seed)
    n_steps = len(x_future)
    boot_cars = []
    for _ in range(n_bootstrap):
        boot_res = rng.choice(residuals, size=n_steps, replace=True)
        boot_path = point_path + boot_res
        boot_cars.append(float(np.sum(boot_path)))
    boot_arr = np.array(boot_cars, dtype=float)
    threshold = np.percentile(boot_arr, (1.0 - alpha) * 100.0)
    tail = boot_arr[boot_arr <= threshold]
    cvar_val = float(np.mean(tail)) if len(tail) > 0 else float(np.min(boot_arr))
    return point_path, cvar_val, boot_arr
```

**Step 3: In the scenario row building loop**, add bootstrap CVaR to each terminal row:

```python
_, node_cvar_95, _ = simulate_y_path_bootstrap(
    x_path_for_this_branch, n_bootstrap=500, alpha=0.95, rng_seed=42
)
scenario_rows.append({
    ...existing fields...,
    "node_cvar_95": node_cvar_95,
})
```

**Step 4: Add canonical by-market output schema after `scenario_summary` is built:**

```python
scenario_summary_by_market = {"AGI_logdiff": scenario_summary.copy()}

agg_dict = {
    "probability": ("probability", "sum"),
    "terminal_abnormal_return": ("terminal_abnormal_return", "mean"),
}
if "node_cvar_95" in scenario_summary.columns:
    agg_dict["node_cvar_95"] = ("node_cvar_95", "mean")

terminal_summary = (
    scenario_summary.groupby("stage1", as_index=False)
    .agg(**agg_dict)
    .sort_values("stage1")
    .reset_index(drop=True)
)
terminal_summary_by_market = {"AGI_logdiff": terminal_summary.copy()}
```

---

### Update D-8 — Cell `9dc4d490` (Hedge Sizing): Add exposure convention and CVaR comparison

Replace the opening parameter block with:
```python
portfolio_value = 1_000_000
risk_budget_fraction = 0.015
execution_haircut = 0.70
hedge_efficiency = 0.60

# Exposure convention:
# - long_price: falling ARTY is adverse (ARTY ETF holder)
# - short_price: rising ARTY is adverse (short-seller view)
exposure_to_price = "long_price"
```

Replace the loss computation block:
```python
w = scenario_summary["probability"].to_numpy(dtype=float)
loss = -scenario_summary["terminal_abnormal_return"].to_numpy(dtype=float)
weighted_loss = float(np.sum(w * np.maximum(loss, 0.0)))
```

With:
```python
w = scenario_summary["probability"].to_numpy(dtype=float)
r_s = scenario_summary["terminal_abnormal_return"].to_numpy(dtype=float)

if exposure_to_price == "long_price":
    L_s = np.maximum(-r_s, 0.0)
elif exposure_to_price == "short_price":
    L_s = np.maximum(r_s, 0.0)
else:
    raise ValueError("exposure_to_price must be 'long_price' or 'short_price'.")

weighted_loss = float(np.sum(w * L_s))
```

Then add the CVaR comparison block at the end of the cell (same pattern as Argentina instructions, Part D, Update D-5 — adapting `hedge_table` to `scenario_summary` and removing the `short_price` special-case since the exposure here is `long_price` by default).

---

### Update D-9 — Cell `16f8d963` (Sign diagnostics): Convert to standalone diagnostic

This cell currently checks `scenario_summary` and `model_df`. It uses `var_engine_fit` from the simulation engine. It is a useful consistency check.

**Change the opening guard from:**
```python
if "model_df" not in globals() or "scenario_summary" not in globals():
    raise RuntimeError("Run model selection and scenario cells first.")
```

**To:**
```python
_required = ["model_df", "scenario_summary", "best_models"]
_missing = [v for v in _required if v not in globals()]
if _missing:
    raise ValueError(
        f"Missing prerequisites: {_missing}. "
        "Run Sections 7b and 9a first."
    )
```

---

## PART E — New Code Cells to Insert

### New Cell E-0 — Horizon variable (replace deleted ipywidgets cell, insert before the simulation cell `26a44756`)

```python
# Section 9a) Simulation horizon — set here, consumed by branching simulation and hedge cells.
# With no resolution date, the horizon is a modeling choice rather than a contract-derived quantity.
# 10 trading days is used as the default: short enough for the model to be informative,
# long enough for the branching structure to produce economically distinct paths.
selected_h = 10  # forward horizon in trading days

print(f"Simulation horizon: {selected_h} days")
print("To change the horizon, update selected_h and re-run Sections 9a–9d and Section 10.")
```

---

### New Cell E-1 — Factor model validation (insert in Section 2a, after the factor model code cell)

```python
# Section 2a) Factor model residual diagnostics
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

if "df_etf" not in globals() or "ARTY_idiosyncratic" not in df_etf.columns:
    raise ValueError("ARTY_idiosyncratic not found. Run the factor model cell first.")

resid = df_etf["ARTY_idiosyncratic"].dropna().copy()
fitted = df_etf["ARTY_fitted"].dropna().copy()
aligned = pd.concat([resid.rename("resid"), fitted.rename("fitted")], axis=1).dropna()

try:
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.stats.diagnostic import het_breuschpagan, acorr_ljungbox
    from statsmodels.regression.linear_model import OLS
    import statsmodels.api as sm

    lb = acorr_ljungbox(aligned["resid"], lags=[5, 10, 20], return_df=True)
    print("Ljung-Box serial correlation test:")
    display(lb)

    dw = durbin_watson(aligned["resid"].to_numpy())
    print(f"\nDurbin-Watson: {dw:.4f}  (2.0 = no autocorrelation)")

    X_bp = sm.add_constant(aligned["fitted"].to_numpy())
    bp_stat, bp_p, _, _ = het_breuschpagan(aligned["resid"].to_numpy(), X_bp)
    print(f"\nBreusch-Pagan heteroskedasticity: stat={bp_stat:.4f}, p={bp_p:.4f}")

    ols_res = OLS(aligned["resid"].to_numpy(), X_bp).fit()
    cooks_d = ols_res.get_influence().cooks_distance[0]
    top5 = np.argsort(cooks_d)[-5:][::-1]
    print("\nTop-5 influential observations (Cook's D):")
    for pos in top5:
        print(f"  {aligned.index[pos]}: {cooks_d[pos]:.4f}")

except ImportError:
    print("statsmodels not available — install to run diagnostics.")

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].scatter(aligned["fitted"], aligned["resid"], alpha=0.4, s=8)
axes[0].axhline(0, color="gray", linewidth=0.8)
axes[0].set_xlabel("Fitted"); axes[0].set_ylabel("Residual")
axes[0].set_title("Residuals vs Fitted — ARTY Factor Model"); axes[0].grid(alpha=0.2)

stats.probplot(aligned["resid"].to_numpy(), plot=axes[1])
axes[1].set_title("Q-Q Plot — ARTY Idiosyncratic Residuals"); axes[1].grid(alpha=0.2)
plt.tight_layout()
import os; os.makedirs("Images", exist_ok=True)
plt.savefig("Images/agi_factor_model_diagnostics.png", dpi=150, bbox_inches="tight")
plt.show()
print("Saved: Images/agi_factor_model_diagnostics.png")
```

---

### New Cell E-2 — OOS R² Summary (insert in Section 7c, after the backtest cell)

```python
# Section 7c) Out-of-sample R² for the selected simulation model
import numpy as np
import pandas as pd

if "best_models" not in globals():
    raise ValueError("best_models is missing. Run the backtest cell first.")

simulation_model = best_models.get("selected_model_for_simulation", "Unknown")
oos_r2 = np.nan
if "backtest_metrics_agi" in globals():
    rows = backtest_metrics_agi[backtest_metrics_agi["model"] == simulation_model]
    if "r2_oos" in rows.columns and not rows.empty:
        oos_r2 = float(rows["r2_oos"].mean())
    elif "rmse" in rows.columns and not rows.empty:
        # approximate OOS R2 from RMSE vs naive mean
        y_var = float(backtest_predictions_agi["y_true"].var()) if "backtest_predictions_agi" in globals() else np.nan
        rmse = float(rows["rmse"].mean())
        if not np.isnan(y_var) and y_var > 0:
            oos_r2 = 1.0 - (rmse ** 2) / y_var

oos_row = pd.DataFrame([{
    "Simulation model": simulation_model,
    "Family": best_models.get("selected_model_family", "Unknown"),
    "OOS R²": f"{oos_r2:.4f}" if not np.isnan(oos_r2) else "N/A",
    "Note": "Negative OOS R² = model underperforms naive mean on average (expected for this case)" if (not np.isnan(oos_r2) and oos_r2 < 0) else "",
}])
print("Out-of-sample R² for simulation model:")
display(oos_row)
```

---

### New Cell E-3 — Rolling CVaR (insert in Section 8)

```python
# Section 8) Rolling empirical CVaR95 of ARTY_idiosyncratic (20-day window)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if "df_analysis" not in globals() or "ARTY residual return" not in df_analysis.columns:
    raise ValueError("df_analysis is required. Run Section 4 first.")

roll_df = df_analysis[["avg agi prediction log diff", "ARTY residual return"]].dropna().copy()
roll_df.index = pd.to_datetime(roll_df.index)
roll_df = roll_df.sort_index().reset_index().rename(columns={"index": "timestamp", "Date": "timestamp"})
roll_df["timestamp"] = pd.to_datetime(roll_df["timestamp"])

ROLL_WINDOW = 20
CVAR_ALPHA = 0.95

def _empirical_cvar(series, alpha=0.95):
    arr = np.asarray(series, dtype=float)
    arr = arr[np.isfinite(arr)]
    if len(arr) == 0:
        return np.nan
    threshold = np.percentile(arr, (1.0 - alpha) * 100.0)
    tail = arr[arr <= threshold]
    return float(np.mean(tail)) if len(tail) > 0 else float(np.min(arr))

rolling_cvar_vals = [np.nan] * (ROLL_WINDOW - 1)
for _i in range(ROLL_WINDOW - 1, len(roll_df)):
    _w = roll_df["ARTY residual return"].iloc[_i - ROLL_WINDOW + 1 : _i + 1]
    rolling_cvar_vals.append(_empirical_cvar(_w, alpha=CVAR_ALPHA))

roll_df["rolling_cvar_95"] = rolling_cvar_vals
rolling_cvar_df = roll_df[["timestamp", "ARTY residual return", "avg agi prediction log diff", "rolling_cvar_95"]].copy()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
ax1.plot(roll_df["timestamp"], roll_df["avg agi prediction log diff"],
         color="#1f77b4", linewidth=1.0, alpha=0.85, label="AGI log diff")
ax1.axhline(0, color="gray", linewidth=0.7, alpha=0.5)
ax1.set_ylabel("AGI log diff", fontsize=10)
ax1.set_title(f"AGI Signal vs {ROLL_WINDOW}-Day Rolling CVaR₉₅ of ARTY Idiosyncratic Returns", fontsize=11)
ax1.legend(frameon=False, fontsize=9)
ax1.grid(alpha=0.2)

cvar_s = roll_df["rolling_cvar_95"]
ax2.fill_between(roll_df["timestamp"], cvar_s, 0, where=cvar_s < 0,
                 color="#d62728", alpha=0.25, label="Downside tail region")
ax2.plot(roll_df["timestamp"], cvar_s, color="#d62728", linewidth=1.3,
         label=f"Rolling CVaR₉₅ ({ROLL_WINDOW}-day, log return)")
ax2.axhline(0, color="gray", linewidth=0.7, alpha=0.5)
ax2.set_ylabel("CVaR₉₅ (log return)", fontsize=10)
ax2.set_xlabel("Date", fontsize=10)
ax2.legend(frameon=False, fontsize=9)
ax2.grid(alpha=0.2)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
fig.autofmt_xdate(rotation=30)
plt.tight_layout()
import os; os.makedirs("Images", exist_ok=True)
plt.savefig("Images/agi_rolling_cvar.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"\nRolling CVaR₉₅ summary ({ROLL_WINDOW}-day window):")
display(roll_df["rolling_cvar_95"].dropna().describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]).to_frame())
print("Saved: Images/agi_rolling_cvar.png")
```

---

### New Cell E-4 — Feature importance and counterfactual sensitivity (insert in Section 9b)

```python
# Section 9b) Feature importance and counterfactual sensitivity (AGI case)
import numpy as np
import pandas as pd

if "best_models" not in globals() or "model_fitted" not in globals():
    raise ValueError("Run Section 9a (simulation engine) first.")

simulation_model = best_models.get("production_model_name", "Unknown")
print(f"Simulation model: {simulation_model}")

# Feature importance: permutation importance for SVR; coef_ for linear; feature_importances_ for trees
feat_imp = None
try:
    if hasattr(model_fitted, "feature_importances_"):
        feat_imp = pd.Series(model_fitted.feature_importances_, index=feat_cols_engine, name="importance")
    elif hasattr(model_fitted, "coef_"):
        feat_imp = pd.Series(np.abs(model_fitted.coef_), index=feat_cols_engine, name="importance")
    elif hasattr(model_fitted, "named_steps"):
        inner = model_fitted.named_steps.get("svr") or model_fitted.named_steps.get("model")
        if hasattr(inner, "coef_"):
            feat_imp = pd.Series(np.abs(inner.coef_.ravel()), index=feat_cols_engine, name="importance")
        else:
            from sklearn.inspection import permutation_importance
            perm = permutation_importance(model_fitted, X_engine_train, y_engine_train,
                                          n_repeats=30, random_state=42)
            feat_imp = pd.Series(perm.importances_mean, index=feat_cols_engine, name="importance")
    if feat_imp is not None:
        feat_imp = feat_imp.sort_values(ascending=False)
        print("\nFeature importances:")
        display(feat_imp.to_frame())
except Exception as exc:
    print(f"Feature importance extraction failed: {exc}")

# One-step counterfactual sensitivity over x_t_lag1
x_lag1_col = "x_t_lag1"
if feat_cols_engine and x_lag1_col in feat_cols_engine:
    base_row = pd.DataFrame([{c: 0.0 for c in feat_cols_engine}])
    shocks = np.linspace(-0.10, 0.10, 41)
    sens_rows = []
    for s in shocks:
        row = base_row.copy()
        row[x_lag1_col] = float(s)
        try:
            y_hat = float(model_fitted.predict(row)[0])
        except Exception:
            y_hat = np.nan
        sens_rows.append({"x_t_lag1_shock": s, "predicted_y": y_hat})
    sens_df = pd.DataFrame(sens_rows)

    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 4))
    plt.plot(sens_df["x_t_lag1_shock"], sens_df["predicted_y"], linewidth=1.8)
    plt.axhline(0, color="gray", linewidth=0.7)
    plt.axvline(0, color="gray", linewidth=0.7)
    plt.xlabel("x_t_lag1 shock (AGI log diff)"); plt.ylabel("Predicted ARTY idio return")
    plt.title(f"One-step counterfactual sensitivity: {simulation_model}")
    plt.grid(alpha=0.2); plt.tight_layout()
    plt.savefig("Images/agi_counterfactual_sensitivity.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Saved: Images/agi_counterfactual_sensitivity.png")
else:
    print(f"{x_lag1_col} not found in feat_cols_engine — skipping sensitivity sweep.")
```

---

## PART F — Final Cell Order

After all edits the notebook should contain cells in this sequence:

```
[MD] C-1    Notebook title
[MD] C-2    ## 1) Asset Data Import
[CD] 46f3623b  Download ARTY ETF
[MD] C-3    ## 2) Factor Model and Idiosyncratic Returns
[CD] 8b152007  PCA factor model  ← UPDATED: Huber regression
[MD] C-4    ### 2a) Factor Model Validation
[CD] E-1       Factor model residual diagnostics  ← NEW
[MD] C-5    ## 3) AGI Timeline Signal Construction
[CD] ab45be53  Load CSV
[CD] 602c6297  Filter to April 2024, build agi_ts
[MD] C-6    ## 4) Data Alignment and Feature Construction
[CD] 91ff5d1f  df_analysis + time_idx  ← UPDATED: add time_idx
[CD] f6f72787  — DELETED (first-20-point debug plot)
[MD] C-7    ## 5) Exploratory Data Analysis
[CD] 63747632  EDA setup (eda_df)  ← UPDATED: include time_idx
[CD] 6ef80275  Summary statistics
[CD] 1c2d3272  ACF/PACF
[CD] 0108a465  Cross-correlation / prewhitening
[CD] f733c640  Stationarity battery
[CD] d6498f83  Structural breaks CUSUM
[CD] fe91e223  ARCH diagnostics
[MD] C-8    ## 6) Structural Analysis: ARDL, VAR, LP, Sign-SVAR
[CD] abf1049a  Model setup (model_df)  ← UPDATED: include time_idx
[CD] 1e915b98  ARDL (AIC/BIC — valid: OLS-based)
[CD] f1648f0d  VAR lag selection + IRF
[CD] 6cdeddf8  Local Projections IRF
[CD] 36d21d34  Model comparison summary
[MD]          ### Main model: Sign-restricted SVAR  (d1ad0396) ← MOVED here
[CD] 5ae19b5c  Sign-restricted SVAR  ← MOVED
[MD]          ### Robustness: Cholesky VAR and LP  (d30d1594) ← MOVED here
[CD] 07c3c605  Robustness overlay  ← MOVED
[MD] C-9    ## 7) Predictive Modeling and Model Selection
[MD] C-10   ### 7a) VAR / SVAR / VECM Benchmark Fitting
[CD] c03507f4  VAR/SVAR/VECM  ← UPDATED: RMSE lag selection
[MD] C-11   ### 7b) Expanding-Window Backtest
[CD] 9cf9bf47  Backtest  ← UPDATED: Lasso, time_idx, two-stage, best_models
[MD] C-12   ### 7c) OOS R²
[CD] E-2       OOS R² cell  ← NEW
[MD] C-13   ## 8) Rolling CVaR of Idiosyncratic Returns
[CD] E-3       Rolling CVaR  ← NEW
[MD] C-14   ## 9) Branching Simulation and Scenario Analysis
[MD] C-15   ### 9a) Simulation Engine and Forward Paths
[CD] E-0       Horizon variable (replaces deleted ipywidgets cell)  ← NEW
[CD] 26a44756  Simulation engine  ← UPDATED: time_idx, bootstrap CVaR, canonical schema
[CD] 182071c3  Branching simulation
[MD] C-16   ### 9b) Feature Importance and Counterfactual Sensitivity
[CD] E-4       Feature importance + counterfactual  ← NEW
[MD] C-17   ### 9c) Distribution Diagnostics and Terminal Node Reporting
[MD]          ## Distribution Diagnostics  (48f4a7b5) ← delete, replaced by C-17
[CD] 7ed7928a  Distribution histogram
[MD] C-18   ### 9d) Branching Scenarios, Confidence Intervals, Sign Diagnostics
[CD] 8ac88468  Scenario branching with CI bands
[CD] 16f8d963  Sign diagnostics  ← UPDATED: clean guard
[CD] cb611ddb  Counterfactual check
[MD] C-19   ## 10) Hedge Sizing
[CD] 9dc4d490  Hedge sizing  ← UPDATED: exposure_to_price + CVaR comparison
```

Total cells after restructuring: **44** (37 post-deletion + 7 new code/markdown cells).

---

## PART G — Run-Order Verification

Run the full notebook top to bottom and confirm:

1. `ARTY_idiosyncratic` and `factor_model_state` are produced by cell `8b152007` and available thereafter.
2. `df_analysis["time_idx"]` is a 0-based integer sequence with no gaps.
3. `model_df` contains columns `["y_t", "x_t", "time_idx"]`.
4. `eda_df` contains `time_idx`.
5. The Sign-SVAR cell (`5ae19b5c`) runs without error in its new position, consuming `var_fit` from cell `f1648f0d`.
6. `best_models["selected_model_for_simulation"]` is set after the backtest cell.
7. `scenario_summary`, `scenario_summary_by_market`, `terminal_summary_by_market` all exist after the simulation cell.
8. `node_cvar_95` is a column in `scenario_summary`.
9. `rolling_cvar_df` is produced by Section 8 without error.
10. The hedge sizing cell prints both the point-estimate table and the CVaR₉₅ comparison table.
11. No cell references `horizon_dropdown` or `ipywidgets` anywhere.
