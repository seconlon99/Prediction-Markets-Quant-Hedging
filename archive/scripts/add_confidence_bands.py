#!/usr/bin/env python3
import json

nb_path = 'AGI.ipynb'

with open(nb_path, 'r') as f:
    nb = json.load(f)

print(f"Total cells: {len(nb['cells'])}")

# Find hedge cell
hedge_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
        if 'Hedge Suggestion For Prediction Window' in src:
            hedge_idx = i
            print(f"Found hedge markdown at index {i}")
            break

if hedge_idx is None:
    print("ERROR: Could not find hedge cell")
    exit(1)

# Create confidence bands markdown
md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Branching Scenarios with Confidence Intervals\n",
        "Using the **best-performing predictive model**, we generate AGI scenario branches with uncertainty bands derived from backtesting residuals.\n"
    ]
}

# Create confidence bands code
code_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "# Scenario branching with confidence bands\n",
        "if 'best_model_name' not in locals():\n",
        "    print('ERROR: Run backtesting cell first')\n",
        "else:\n",
        "    # Extract residuals from best model predictions\n",
        "    best_preds = backtest_predictions_agi[['y_true', best_model_name]].dropna()\n",
        "    residuals = best_preds[best_model_name].values - best_preds['y_true'].values\n",
        "    rmse_best = np.sqrt(np.mean(residuals**2))\n",
        "    \n",
        "    # Define scenarios based on AGI expectation distribution\n",
        "    target_horizon = 10\n",
        "    base_year = float(df_overlap_timeseries['avg agi prediction'].dropna().iloc[-1])\n",
        "    \n",
        "    # Calibrate shifts from historical data\n",
        "    year_series = df_overlap_timeseries['avg agi prediction'].dropna().astype(float)\n",
        "    obs_shifts = (year_series.shift(-target_horizon) - year_series).dropna()\n",
        "    \n",
        "    branches_data = [\n",
        "        {'name': 'Advanced AGI', 'shift': obs_shifts.quantile(0.10), 'prob': 0.25},\n",
        "        {'name': 'Central', 'shift': obs_shifts.quantile(0.50), 'prob': 0.50},\n",
        "        {'name': 'Delayed AGI', 'shift': obs_shifts.quantile(0.90), 'prob': 0.25},\n",
        "    ]\n",
        "    \n",
        "    scenario_records = []\n",
        "    fig, ax = plt.subplots(figsize=(12, 6))\n",
        "    colors = {'Advanced AGI': 'green', 'Central': 'blue', 'Delayed AGI': 'red'}\n",
        "    \n",
        "    for branch_info in branches_data:\n",
        "        year_shift = branch_info['shift']\n",
        "        target_year = base_year + year_shift\n",
        "        x_shock = np.log(max(1.0, target_year) / base_year)\n",
        "        x_path = np.concatenate([[x_shock], np.zeros(target_horizon - 1)])\n",
        "        \n",
        "        # Simulate mean path\n",
        "        y_mean = simulate_y_path_from_x_path(x_path)\n",
        "        y_cumsum = np.cumsum(y_mean)\n",
        "        \n",
        "        # Add confidence bands\n",
        "        y_lo = y_cumsum - 1.96 * rmse_best * np.sqrt(np.arange(1, len(y_cumsum) + 1))\n",
        "        y_hi = y_cumsum + 1.96 * rmse_best * np.sqrt(np.arange(1, len(y_cumsum) + 1))\n",
        "        \n",
        "        terminal_ret = np.exp(y_cumsum[-1]) - 1.0\n",
        "        terminal_lo = np.exp(y_lo[-1]) - 1.0\n",
        "        terminal_hi = np.exp(y_hi[-1]) - 1.0\n",
        "        \n",
        "        running_max = np.maximum.accumulate(y_cumsum)\n",
        "        max_dd = np.max(running_max - y_cumsum)\n",
        "        \n",
        "        scenario_records.append({\n",
        "            'branch': branch_info['name'],\n",
        "            'terminal_abnormal_return': terminal_ret,\n",
        "            'terminal_return_ci_lo': terminal_lo,\n",
        "            'terminal_return_ci_hi': terminal_hi,\n",
        "            'probability': branch_info['prob'],\n",
        "            'max_drawdown': max_dd,\n",
        "        })\n",
        "        \n",
        "        # Plot\n",
        "        h_range = np.arange(target_horizon + 1)\n",
        "        ax.plot(h_range, y_cumsum * 100, label=branch_info['name'], color=colors[branch_info['name']], linewidth=2.5)\n",
        "        ax.fill_between(h_range, y_lo * 100, y_hi * 100, color=colors[branch_info['name']], alpha=0.2)\n",
        "    \n",
        "    scenario_summary = pd.DataFrame(scenario_records)\n",
        "    ax.axhline(0, color='k', linewidth=0.8, linestyle='--', alpha=0.5)\n",
        "    ax.set_xlabel('Horizon (days)', fontsize=11)\n",
        "    ax.set_ylabel('Cumulative return (%)', fontsize=11)\n",
        "    ax.set_title(f'AGI Scenarios with Confidence Bands (Best Model: {best_model_name})', fontsize=12)\n",
        "    ax.grid(alpha=0.3)\n",
        "    ax.legend(loc='best')\n",
        "    plt.tight_layout()\n",
        "    plt.show()\n",
        "    \n",
        "    print(f'\\nModel RMSE: {rmse_best:.6f} | Used for 95% confidence bands')\n",
        "    display(scenario_summary)\n"
    ]
}

# Insert before hedge sizing
nb['cells'].insert(hedge_idx, md_cell)
nb['cells'].insert(hedge_idx + 1, code_cell)
print(f"Inserted md+code at indices {hedge_idx}, {hedge_idx+1}")

with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Final cell count: {len(nb['cells'])}")
print("✓ Refactoring complete: MC removed, confidence bands added")
