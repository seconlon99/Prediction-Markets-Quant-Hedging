#!/usr/bin/env python3
import json

with open('AGI.ipynb', 'r') as f:
    nb = json.load(f)

# Get the problematic cell (cell 22 - the backtesting cell)
cell = nb['cells'][22]
src_text = ''.join(cell['source'])

# Fix the corruption at lines 276-282
# The GradientBoosting block is incomplete. Replace the broken section:
broken = """    if model_name == "GradientBoosting":
        est_try = GradientBoostingRegressor(
            random_state=42,
            learning_rate=0.05,
            max_depth=2,
        row["GARCH"] = np.nan
        row["FoundationModel"] = np.nan
    else:"""

fixed = """    if model_name == "GradientBoosting":
        est_try = GradientBoostingRegressor(
            random_state=42,
            learning_rate=0.05,
            max_depth=2,
            n_estimators=100,
        )
        est_try.fit(X_tr, y_tr)
        score = _rmse_np(y_va.to_numpy(dtype=float), est_try.predict(X_va))
        final_est = clone(estimator)
        final_est.fit(X_train, y_train)
        return float(final_est.predict(X_next)[0])
    
    # Default: use standard fit"""

src_text_fixed = src_text.replace(broken, fixed)

# Update cell source
cell['source'] = [s if s.endswith('\n') else s + '\n' for s in src_text_fixed.split('\n')]
if cell['source'][-1] == '\n':
    cell['source'][-1] = cell['source'][-1][:-1]

# Save
with open('AGI.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("✓ Fixed backtesting cell")
