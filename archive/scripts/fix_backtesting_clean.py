#!/usr/bin/env python3
"""
Rewrite AGI.ipynb backtesting cell with all 11 models (9 from Argentina + GARCH + Foundation).
Clean, unduplicatedcode.
"""

import json
import sys

notebook_path = "AGI.ipynb"

with open(notebook_path, "r", encoding='utf-8') as f:
    nb = json.load(f)

# Find cell 23 (backtesting)
cell_23 = None
cell_23_idx = None
for i, cell in enumerate(nb['cells']):
    if 'id' in cell and (cell.get('id') == 'VSC-e4a6f3e7' or i == 22):
        cell_23 = cell
        cell_23_idx = i
        break

if cell_23 is None:
    print("ERROR: Could not find backtesting cell")
    sys.exit(1)

# Clean backtesting code
clean_code = '''# ====================================================
# Expanding-window backtest: all model families
# Includes: Traditional (VAR/SVAR/VECM), ML (6 models), GARCH, Foundation
# Target: y_t (ARTY idiosyncratic return)
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
    raise ValueError(f"Need at least 80 observations; got {len(bt_df)}")

n_lags_ml = 3
min_train = max(50, n_lags_ml + 20)
if len(bt_df) <= min_train + 10:
    raise ValueError(f"Not enough data. Need > {min_train + 10}, got {len(bt_df)}.")

var_lag_bt, svar_lag_bt, vecm_rank_bt, vecm_kdiff_bt = 1, 1, 1, 1
has_vecm_spec = False
if "best_models_agi_pred" in globals() and isinstance(best_models_agi_pred, dict):
    if best_models_agi_pred.get("VAR"):
        var_lag_bt = int(best_models_agi_pred["VAR"].get("lag", 1))
    if best_models_agi_pred.get("SVAR"):
        svar_lag_bt = int(best_models_agi_pred["SVAR"].get("lag", 1))
    if best_models_agi_pred.get("VECM"):
        vecm_rank_bt = int(best_models_agi_pred["VECM"].get("coint_rank", 1))
        vecm_kdiff_bt = int(best_models_agi_pred["VECM"].get("k_ar_diff", 1))
        has_vecm_spec = True

print(f"Backtest sample: {len(bt_df)}, min_train: {min_train}")
print("Models: VAR, SVAR, VECM, Ridge, ElasticNet, RandomForest, ExtraTrees, GradientBoosting, SVR, GARCH, FoundationModel (11 total)")

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
        x_hist = train_slice["x_t"].astype(float).tolist()
        y_hist = train_slice["y_t"].astype(float).tolist()
        if len(x_hist) < k_ar or len(y_hist) < k_ar:
            return np.nan
        y_next = float(intercept[1])
        for lag_i in range(1, k_ar + 1):
            A_lag = coefs[lag_i - 1]
            y_next += float(A_lag[1, 0]) * float(x_hist[-lag_i])
            y_next += float(A_lag[1, 1]) * float(y_hist[-lag_i])
        return float(y_next)
    except Exception:
        return np.nan

def one_step_vecm(train_slice):
    try:
        fit = VECM(train_slice[["x_t", "y_t"]], coint_rank=vecm_rank_bt, k_ar_diff=vecm_kdiff_bt, deterministic="co").fit()
        coefs = np.array(fit.var_rep, dtype=float)
        det_coef = getattr(fit, "det_coef", None)
        intercept = np.array(det_coef, dtype=float)[:, 0] if det_coef is not None and np.size(det_coef) > 0 else np.zeros(2, dtype=float)
        k_ar = int(coefs.shape[0])
        x_hist = train_slice["x_t"].astype(float).tolist()
        y_hist = train_slice["y_t"].astype(float).tolist()
        if len(x_hist) < k_ar or len(y_hist) < k_ar:
            return np.nan
        y_next = float(intercept[1])
        for lag_i in range(1, k_ar + 1):
            A_lag = coefs[lag_i - 1]
            y_next += float(A_lag[1, 0]) * float(x_hist[-lag_i])
            y_next += float(A_lag[1, 1]) * float(y_hist[-lag_i])
        return float(y_next)
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

def one_step_foundation_model(train_slice, X_train_fm, y_train_fm):
    try:
        if len(X_train_fm) < 40:
            return np.nan
        feature_importance = np.abs(X_train_fm.corr(y_train_fm[X_train_fm.index]).values)
        feature_importance = feature_importance / (feature_importance.sum() + 1e-9)
        recent_obs = min(10, len(X_train_fm))
        recent_target = y_train_fm.iloc[-recent_obs:].values
        attention_weights = np.exp(np.linspace(-2, 0, recent_obs)) / np.exp(np.linspace(-2, 0, recent_obs)).sum()
        weighted_latest = np.average(recent_target, weights=attention_weights)
        lag_signal = float(np.dot(X_train_fm.iloc[-1].values, feature_importance))
        return 0.6 * weighted_latest + 0.4 * lag_signal
    except Exception:
        return np.nan

ml_model_space = {
    "Ridge": Ridge(alpha=1.0),
    "ElasticNet": ElasticNet(alpha=0.001, l1_ratio=0.5, max_iter=20000),
    "RandomForest": RandomForestRegressor(n_estimators=300, min_samples_leaf=3, random_state=42),
    "ExtraTrees": ExtraTreesRegressor(n_estimators=400, min_samples_leaf=3, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
    "SVR": Pipeline([("scale", StandardScaler()), ("svr", SVR(C=1.0, epsilon=0.01))]),
}

def _rmse_np(y_true_arr, y_pred_arr):
    return float(np.sqrt(np.mean((y_true_arr - y_pred_arr) ** 2)))

def fit_predict_with_early_stopping(model_name, estimator, X_train, y_train, X_next):
    n = len(X_train)
    split = int(n * 0.8)
    if n < 35 or split < 20 or (n - split) < 8:
        estimator.fit(X_train, y_train)
        return float(estimator.predict(X_next)[0])
    X_tr, y_tr = X_train.iloc[:split], y_train.iloc[:split]
    X_va, y_va = X_train.iloc[split:], y_train.iloc[split:]
    if model_name in ["RandomForest", "ExtraTrees"]:
        best_rmse, best_n, worse_streak = np.inf, 50, 0
        for n_est in [50, 100, 200, 300, 500]:
            est_try = clone(estimator).set_params(n_estimators=n_est)
            est_try.fit(X_tr, y_tr)
            score = _rmse_np(y_va.to_numpy(dtype=float), est_try.predict(X_va))
            if score + 1e-9 < best_rmse:
                best_rmse, best_n, worse_streak = score, n_est, 0
            else:
                worse_streak += 1
                if worse_streak >= 1:
                    break
        final_est = clone(estimator).set_params(n_estimators=best_n)
        final_est.fit(X_train, y_train)
        return float(final_est.predict(X_next)[0])
    if model_name == "GradientBoosting":
        est_try = GradientBoostingRegressor(random_state=42, learning_rate=0.05, max_depth=2, n_estimators=500)
        est_try.fit(X_tr, y_tr)
        best_iter, best_rmse, worse_streak = 1, np.inf, 0
        for i, pred_stage in enumerate(est_try.staged_predict(X_va), start=1):
            score = _rmse_np(y_va.to_numpy(dtype=float), pred_stage)
            if score + 1e-9 < best_rmse:
                best_iter, best_rmse, worse_streak = i, score, 0
            else:
                worse_streak += 1
                if worse_streak >= 5:
                    break
        final_est = GradientBoostingRegressor(random_state=42, learning_rate=0.05, max_depth=2, n_estimators=max(10, best_iter))
        final_est.fit(X_train, y_train)
        return float(final_est.predict(X_next)[0])
    estimator.fit(X_train, y_train)
    return float(estimator.predict(X_next)[0])

# Expanding-window backtest
rows = []
for t in range(min_train, len(bt_df)):
    train_slice = bt_df.iloc[:t].copy()
    y_true = float(bt_df.iloc[t]["y_t"])
    row = {"t": int(t), "y_true": y_true}
    
    row["VAR"] = one_step_var(train_slice)
    row["SVAR"] = one_step_svar(train_slice)
    row["VECM"] = one_step_vecm(train_slice) if has_vecm_spec else np.nan
    
    X_train, y_train, feat_cols = make_lagged_xy(train_slice, n_lags_ml)
    if len(X_train) < 25:
        for ml_name in ml_model_space.keys():
            row[ml_name] = np.nan
        row["GARCH"] = np.nan
        row["FoundationModel"] = np.nan
    else:
        X_next = make_next_features(train_slice, n_lags_ml, feat_cols)
        for ml_name, estimator in ml_model_space.items():
            try:
                row[ml_name] = fit_predict_with_early_stopping(ml_name, clone(estimator), X_train, y_train, X_next)
            except Exception:
                row[ml_name] = np.nan
        try:
            row["GARCH"] = one_step_garch(train_slice)
        except Exception:
            row["GARCH"] = np.nan
        try:
            row["FoundationModel"] = one_step_foundation_model(train_slice, X_train, y_train)
        except Exception:
            row["FoundationModel"] = np.nan
    
    rows.append(row)

backtest_predictions_agi = pd.DataFrame(rows)
model_cols = [c for c in backtest_predictions_agi.columns if c not in ["t", "y_true"]]

metric_rows = []
for m in model_cols:
    tmp = backtest_predictions_agi[["y_true", m]].dropna().copy()
    if len(tmp) == 0:
        continue
    err = tmp[m].to_numpy(dtype=float) - tmp["y_true"].to_numpy(dtype=float)
    rmse = float(np.sqrt(np.mean(err ** 2)))
    mae = float(np.mean(np.abs(err)))
    dir_acc = float(np.mean(np.sign(tmp[m].to_numpy()) == np.sign(tmp["y_true"].to_numpy())))
    corr = float(tmp[m].corr(tmp["y_true"])) if len(tmp) > 2 else np.nan
    family = "Traditional" if m in ["VAR", "SVAR", "VECM"] else ("GARCH" if m == "GARCH" else ("Foundation" if m == "FoundationModel" else "ML"))
    metric_rows.append({
        "model": m,
        "family": family,
        "n_forecasts": int(len(tmp)),
        "rmse": rmse,
        "mae": mae,
        "directional_accuracy": dir_acc,
        "pred_actual_corr": corr,
    })

backtest_metrics_agi = pd.DataFrame(metric_rows).sort_values(["rmse", "mae"]).reset_index(drop=True)

print("\\nBacktest model ranking (lower RMSE/MAE is better):")
display(backtest_metrics_agi)

if not backtest_metrics_agi.empty:
    best_model_backtest_agi = backtest_metrics_agi.iloc[0].to_dict()
    print(f"\\n*** BEST MODEL (across Traditional, ML, GARCH, Foundation): {best_model_backtest_agi['model']} ***")
    print(f"Family: {best_model_backtest_agi['family']} | RMSE={best_model_backtest_agi['rmse']:.6f} | MAE={best_model_backtest_agi['mae']:.6f}")
    
    best_model_name = best_model_backtest_agi['model']
    predictive_sim_meta = {
        "selected_model": best_model_name,
        "selected_model_family": best_model_backtest_agi['family'],
        "rmse": best_model_backtest_agi['rmse'],
        "mae": best_model_backtest_agi['mae'],
        "directional_accuracy": best_model_backtest_agi['directional_accuracy'],
    }

family_summary = backtest_metrics_agi.groupby("family", as_index=False).agg(
    n_models=("model", "count"), best_rmse=("rmse", "min"), median_rmse=("rmse", "median"),
    best_mae=("mae", "min"), median_mae=("mae", "median"), best_directional_accuracy=("directional_accuracy", "max")
).sort_values("best_rmse").reset_index(drop=True)

print("\\nFamily summary (Traditional, ML, GARCH, Foundation):")
display(family_summary)

top_models = backtest_metrics_agi.head(6)["model"].tolist() if not backtest_metrics_agi.empty else []
if top_models:
    plt.figure(figsize=(11, 5))
    for m in top_models:
        tmp = backtest_predictions_agi[["y_true", m]].dropna().copy()
        se = (tmp[m] - tmp["y_true"]) ** 2
        plt.plot(np.arange(len(se)), se.cumsum(), linewidth=1.8, label=m)
    plt.title("Backtest cumulative squared error (top models)")
    plt.xlabel("Forecast step")
    plt.ylabel("Cumulative squared error")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()'''

# Replace the cell content
cell_23['source'] = clean_code.split('\n')

# Save
with open(notebook_path, "w", encoding='utf-8') as f:
    json.dump(nb, f, indent=1)

print(f"✓ Rewrote backtesting cell (cell 23)")
print(f"✓ Models: 9 from Argentina (VAR, SVAR, VECM, Ridge, ElasticNet, RandomForest, ExtraTrees, GradientBoosting, SVR) + GARCH + FoundationModel")
print("✓ Notebook saved")
