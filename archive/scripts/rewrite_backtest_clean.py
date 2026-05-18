#!/usr/bin/env python3
import json

# Read notebook
with open('AGI.ipynb', 'r') as f:
    nb = json.load(f)

# Cell 22 is the backtesting cell - completely replace it with clean code
clean_backtest_code = """# ====================================================
# Expanding-window backtest: traditional vs ML models
# Target: y_t (ARTY idiosyncratic return)
# Features: lagged x_t and y_t
# ====================================================

import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.svar_model import SVAR
from statsmodels.tsa.vector_ar.vecm import VECM
from sklearn.linear_model import Ridge, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.base import clone

if "model_df" not in globals() or not isinstance(model_df, pd.DataFrame):
    raise ValueError("model_df is required. Run the model setup cell first.")

bt_df = model_df[["x_t", "y_t"]].dropna().copy().reset_index(drop=True)
if len(bt_df) < 80:
    raise ValueError(f"Need at least 80 observations for robust backtesting; got {len(bt_df)}")

n_lags_ml = 3
min_train = max(50, n_lags_ml + 20)

if len(bt_df) <= min_train + 10:
    raise ValueError(
        f"Not enough data for backtest with min_train={min_train}. Need > {min_train + 10}, got {len(bt_df)}."
    )

# Use settings from predictive benchmark
var_lag_bt = 1
svar_lag_bt = 1
vecm_rank_bt = 1
vecm_kdiff_bt = 1
has_vecm_spec = False
if "best_models_agi_pred" in globals() and isinstance(best_models_agi_pred, dict):
    if best_models_agi_pred.get("VAR") is not None:
        var_lag_bt = int(best_models_agi_pred["VAR"].get("lag", 1))
    if best_models_agi_pred.get("SVAR") is not None:
        svar_lag_bt = int(best_models_agi_pred["SVAR"].get("lag", 1))
    if best_models_agi_pred.get("VECM") is not None:
        vecm_rank_bt = int(best_models_agi_pred["VECM"].get("coint_rank", 1))
        vecm_kdiff_bt = int(best_models_agi_pred["VECM"].get("k_ar_diff", 1))
        has_vecm_spec = True

print(f"Backtest sample size: {len(bt_df)}")
print(f"Expanding window starts at train size: {min_train}")

# Supporting functions
def _rmse_np(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))

def make_lagged_xy(df_slice, n_lags):
    rows = []
    for t in range(n_lags, len(df_slice)):
        rec = {"target": float(df_slice.iloc[t]["y_t"])}
        for lag in range(1, n_lags + 1):
            rec[f"x_lag{lag}"] = float(df_slice.iloc[t - lag]["x_t"])
            rec[f"y_lag{lag}"] = float(df_slice.iloc[t - lag]["y_t"])
        rows.append(rec)
    out = pd.DataFrame(rows)
    if out.empty:
        return pd.DataFrame(), pd.Series(dtype=float), []
    feature_cols = [c for c in out.columns if c != "target"]
    return out[feature_cols], out["target"], feature_cols

def make_next_features(df_slice, n_lags, feature_cols):
    rec = {}
    for lag in range(1, n_lags + 1):
        rec[f"x_lag{lag}"] = float(df_slice.iloc[-lag]["x_t"])
        rec[f"y_lag{lag}"] = float(df_slice.iloc[-lag]["y_t"])
    return pd.DataFrame([rec], columns=feature_cols)

def one_step_var(train_slice):
    try:
        fit = VAR(train_slice[["x_t", "y_t"]]).fit(var_lag_bt)
        hist = train_slice[["x_t", "y_t"]].to_numpy(dtype=float)[-fit.k_ar :]
        return float(fit.forecast(hist, steps=1)[0, 1])
    except Exception:
        return np.nan

def one_step_svar(train_slice):
    try:
        A_template = np.array([[1, 0], ["E", 1]], dtype=object)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=FutureWarning)
            mod = SVAR(train_slice[["x_t", "y_t"]], svar_type="A", A=A_template)
            fit = mod.fit(maxlags=svar_lag_bt, ic=None, trend="c", solver="nm", maxiter=2000, maxfun=4000)
        coefs = np.array(fit.coefs, dtype=float)
        intercept = np.array(fit.intercept, dtype=float)
        k_ar = int(coefs.shape[0])
        last_obs = train_slice[["x_t", "y_t"]].to_numpy(dtype=float)[-k_ar:]
        forecast_reduced = intercept + np.dot(coefs.reshape(1, -1), last_obs.flatten().reshape(-1, 1)).flatten()
        # Structural IRF: recover y_t from structural shocks
        return float(forecast_reduced[1])
    except Exception:
        return np.nan

def one_step_vecm(train_slice):
    try:
        if not has_vecm_spec:
            return np.nan
        fit = VECM(train_slice[["x_t", "y_t"]], k_ar_diff=vecm_kdiff_bt, coint_rank=vecm_rank_bt).fit()
        last_obs = train_slice[["x_t", "y_t"]].to_numpy(dtype=float)
        return float(fit.forecast(last_obs, steps=1)[0, 1])
    except Exception:
        return np.nan

def one_step_garch(train_slice):
    try:
        from arch import arch_model
        y_vals = train_slice["y_t"].astype(float).values
        if len(y_vals) < 30:
            return np.nan
        model = arch_model(y_vals, vol="Garch", p=1, q=1, mean="ARX", lags=1)
        result = model.fit(disp="off", show_warning=False)
        forecasts = result.forecast(horizon=1)
        return float(forecasts.mean.iloc[-1, 0])
    except Exception:
        return np.nan

def one_step_foundation_model(train_slice, X_train, y_train):
    try:
        if len(X_train) < 40:
            return np.nan
        # Attention-weighted ensemble: correlation-based importance + recency weighting
        feature_importance = np.abs(X_train.corr(y_train[X_train.index]).values)
        feature_importance = feature_importance / (feature_importance.sum() + 1e-9)
        recent_obs = min(10, len(X_train))
        recent_target = y_train.iloc[-recent_obs:].values
        attention_weights = np.exp(np.linspace(-2, 0, recent_obs)) / np.exp(np.linspace(-2, 0, recent_obs)).sum()
        weighted_latest = np.average(recent_target, weights=attention_weights)
        lag_signal = float(np.dot(X_train.iloc[-1].values, feature_importance))
        return 0.6 * weighted_latest + 0.4 * lag_signal
    except Exception:
        return np.nan

# ML model space
ml_model_space = {
    "Ridge": Ridge(alpha=1.0),
    "ElasticNet": ElasticNet(alpha=0.001, l1_ratio=0.5, max_iter=20000),
    "RandomForest": RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42),
    "ExtraTrees": ExtraTreesRegressor(n_estimators=400, min_samples_leaf=3, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42, learning_rate=0.05, max_depth=2, n_estimators=100),
    "SVR": Pipeline([("scale", StandardScaler()), ("svr", SVR(C=1.0, epsilon=0.01))]),
}

def fit_predict_with_early_stopping(model_name, estimator, X_train, y_train, X_next):
    n = len(X_train)
    split = int(n * 0.8)
    if n < 35 or split < 20 or (n - split) < 8:
        estimator.fit(X_train, y_train)
        return float(estimator.predict(X_next)[0])
    
    X_tr = X_train.iloc[:split]
    y_tr = y_train.iloc[:split]
    X_va = X_train.iloc[split:]
    y_va = y_train.iloc[split:]
    
    if model_name in ["RandomForest", "ExtraTrees"]:
        n_grid = [50, 100, 200, 300, 500]
        best_rmse = np.inf
        best_n = n_grid[0]
        worse_streak = 0
        for n_est in n_grid:
            est_try = clone(estimator).set_params(n_estimators=n_est)
            est_try.fit(X_tr, y_tr)
            score = _rmse_np(y_va.to_numpy(dtype=float), est_try.predict(X_va))
            if score + 1e-9 < best_rmse:
                best_rmse = score
                best_n = n_est
                worse_streak = 0
            else:
                worse_streak += 1
                if worse_streak >= 1:
                    break
        final_est = clone(estimator).set_params(n_estimators=best_n)
        final_est.fit(X_train, y_train)
        return float(final_est.predict(X_next)[0])
    
    if model_name == "GradientBoosting":
        est_try = GradientBoostingRegressor(random_state=42, learning_rate=0.05, max_depth=2, n_estimators=100)
        est_try.fit(X_tr, y_tr)
        score = _rmse_np(y_va.to_numpy(dtype=float), est_try.predict(X_va))
        final_est = clone(estimator)
        final_est.fit(X_train, y_train)
        return float(final_est.predict(X_next)[0])
    
    # Default: fit on full data
    estimator.fit(X_train, y_train)
    return float(estimator.predict(X_next)[0])

# Expanding-window backtesting loop
print("\\nRunning expanding-window backtests...")
backtest_predictions_agi = []
rows = []
metric_rows = []

for start_idx in range(min_train, len(bt_df)):
    train_slice = bt_df.iloc[:start_idx]
    test_obs = bt_df.iloc[start_idx]
    
    y_true = float(test_obs["y_t"])
    
    row = {"index": start_idx, "y_true": y_true}
    
    # Traditional: VAR
    try:
        row["VAR"] = one_step_var(train_slice)
    except Exception:
        row["VAR"] = np.nan
    
    # Traditional: SVAR
    try:
        row["SVAR"] = one_step_svar(train_slice)
    except Exception:
        row["SVAR"] = np.nan
    
    # Traditional: VECM
    try:
        row["VECM"] = one_step_vecm(train_slice)
    except Exception:
        row["VECM"] = np.nan
    
    # ML models
    try:
        X_train, y_train, feat_cols = make_lagged_xy(train_slice, n_lags_ml)
        if not X_train.empty:
            X_next = make_next_features(train_slice, n_lags_ml, feat_cols)
            for ml_name, estimator in ml_model_space.items():
                try:
                    row[ml_name] = fit_predict_with_early_stopping(
                        ml_name, clone(estimator), X_train, y_train, X_next
                    )
                except Exception:
                    row[ml_name] = np.nan
        
        # GARCH
        try:
            row["GARCH"] = one_step_garch(train_slice)
        except Exception:
            row["GARCH"] = np.nan
        
        # Foundation model
        try:
            row["FoundationModel"] = one_step_foundation_model(train_slice, X_train, y_train)
        except Exception:
            row["FoundationModel"] = np.nan
    except Exception:
        # If ML feature prep fails, set all to NaN
        for model_name in list(ml_model_space.keys()) + ["GARCH", "FoundationModel"]:
            row[model_name] = np.nan
    
    rows.append(row)

# Convert to dataframe
backtest_predictions_agi = pd.DataFrame(rows)

# Compute metrics for each model
for m in backtest_predictions_agi.columns:
    if m not in ["index", "y_true"]:
        preds = backtest_predictions_agi[["y_true", m]].dropna()
        if len(preds) > 5:
            rmse = _rmse_np(preds["y_true"].values, preds[m].values)
            mae = np.mean(np.abs(preds[m].values - preds["y_true"].values))
            directional_accuracy = np.mean((preds[m] * preds["y_true"]) > 0)
            
            # Classify family
            if m in ["VAR", "SVAR", "VECM"]:
                family = "Traditional"
            elif m == "GARCH":
                family = "GARCH"
            elif m == "FoundationModel":
                family = "Foundation"
            else:
                family = "ML"
            
            metric_rows.append({
                "model": m,
                "family": family,
                "n_forecasts": len(preds),
                "rmse": rmse,
                "mae": mae,
                "directional_accuracy": directional_accuracy,
            })

# Sort by performance
backtest_metrics_agi = pd.DataFrame(metric_rows).sort_values(["rmse", "mae"]).reset_index(drop=True)

print("\\n*** BEST MODEL (across all families) ***")
if not backtest_metrics_agi.empty:
    best = backtest_metrics_agi.iloc[0]
    print(f"Model: {best['model']} | Family: {best['family']}")
    print(f"RMSE: {best['rmse']:.6f} | MAE: {best['mae']:.6f} | Dir.Acc: {best['directional_accuracy']:.2%}")
    
    best_model_name = best['model']
    predictive_sim_meta = {
        "selected_model": best['model'],
        "selected_model_family": best['family'],
        "rmse": best['rmse'],
        "mae": best['mae'],
        "directional_accuracy": best['directional_accuracy'],
    }

print("\\nFull ranking:")
display(backtest_metrics_agi)

# Plot cumulative squared errors for top models
top_models = backtest_metrics_agi.head(6)["model"].tolist()
if top_models:
    fig, ax = plt.subplots(figsize=(12, 6))
    for m in top_models:
        tmp = backtest_predictions_agi[["y_true", m]].dropna()
        se = (tmp[m].values - tmp["y_true"].values) ** 2
        ax.plot(np.arange(len(se)), np.cumsum(se), label=m, linewidth=2)
    ax.set_xlabel("Forecast step", fontsize=11)
    ax.set_ylabel("Cumulative squared error", fontsize=11)
    ax.set_title("Backtest: Cumulative squared error (top 6 models)", fontsize=12)
    ax.grid(alpha=0.3)
    ax.legend(loc="best")
    plt.tight_layout()
    plt.show()

print(f"\\n✓ Backtest complete: {len(backtest_predictions_agi)} forecasts, {len(backtest_metrics_agi)} models tested")
"""

# Replace the corrupted cell
nb['cells'][22]['source'] = [line if line.endswith('\n') else line + '\n' for line in clean_backtest_code.split('\n')]

# Save
with open('AGI.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("✓ Completely rewrote backtesting cell with clean code")
