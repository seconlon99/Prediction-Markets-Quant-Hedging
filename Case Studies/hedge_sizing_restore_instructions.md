# Copilot Instructions: Restore Hedge Sizing Cell
## File: `Energy_Lower_Freq_Nuclear.ipynb`

---

## Problem

Cell 58 (id `bfb7b6d2`, the only code cell under the `## 9) Hedge Sizing` markdown) currently contains a copy of the nuclear reporting block from Section 8d. The actual hedge sizing logic is missing. The cell must be **completely replaced** with the implementation described below.

---

## Action: Replace the entire source of cell `bfb7b6d2` with the following code

**Do not modify any other cell.** Only replace the source of cell id `bfb7b6d2`.

---

```python
# ====================================================
# Section 9) Hedge Sizing
# Translates scenario-weighted downside into a hedge notional.
# Reports both the point-estimate notional (CAR-based) and the
# CVaR95-informed notional (bootstrap tail risk) for comparison.
# Consumes: scenario_summary_by_market, terminal_summary_by_market
# ====================================================

import numpy as np
import pandas as pd

# ---- Prerequisites ----
nuclear_key = "PM_nuclear_returns"

if "scenario_summary_by_market" not in globals() or nuclear_key not in scenario_summary_by_market:
    raise ValueError(
        "scenario_summary_by_market missing or does not contain nuclear key. "
        "Run the branching simulation cell (Section 8a) first."
    )
if "terminal_summary_by_market" not in globals() or nuclear_key not in terminal_summary_by_market:
    raise ValueError(
        "terminal_summary_by_market missing. Run the branching simulation cell first."
    )

hedge_table = scenario_summary_by_market[nuclear_key].copy()
nuclear_terminal = terminal_summary_by_market[nuclear_key].copy()

# ---- Portfolio and risk parameters ----
portfolio_value       = 1_000_000   # USD notional exposure
risk_budget_fraction  = 0.015       # 1.5 % of portfolio value
execution_haircut     = 0.70        # discount for implementation shortfall / liquidity
hedge_efficiency      = 0.60        # conservative payoff efficiency after costs / slippage

# Exposure convention:
#   short_price  -> position is harmed by RISING electricity prices (e.g. energy consumer / load)
#   long_price   -> position is harmed by FALLING electricity prices (e.g. producer / generator)
exposure_to_price = "short_price"

# ============================================================
# PART 1: Point-estimate hedge sizing (CAR-based)
# ============================================================

w     = hedge_table["probability"].to_numpy(dtype=float)
r_s   = hedge_table["terminal_abnormal_return"].to_numpy(dtype=float)

if exposure_to_price == "short_price":
    # Loss occurs when prices RISE → positive idiosyncratic CAR is adverse
    L_s = np.maximum(r_s, 0.0)
elif exposure_to_price == "long_price":
    # Loss occurs when prices FALL → negative idiosyncratic CAR is adverse
    L_s = np.maximum(-r_s, 0.0)
else:
    raise ValueError("exposure_to_price must be 'short_price' or 'long_price'.")

weighted_loss = float(np.sum(w * L_s))

# Target coverage: hedge only the loss in excess of the risk budget
if weighted_loss <= risk_budget_fraction:
    target_coverage = 0.0
else:
    target_coverage = (weighted_loss - risk_budget_fraction) / weighted_loss

raw_hedge_notional_pct = target_coverage / hedge_efficiency if hedge_efficiency > 0 else 0.0
hedge_notional_pct     = float(np.clip(raw_hedge_notional_pct * execution_haircut, 0.0, 0.80))
hedge_notional_usd     = hedge_notional_pct * portfolio_value


def hedge_instrument_mix(weighted_downside: float) -> str:
    """Map expected weighted downside to a broad instrument recommendation."""
    if weighted_downside <= 0:
        return "No additional hedge required"
    if weighted_downside <= 0.01:
        return (
            "Mild downside: light OTM electricity/gas put spread "
            "(1–3 month, staged TWAP execution)."
        )
    if weighted_downside <= 0.03:
        return (
            "Moderate downside: protective put or collar on electricity forwards; "
            "optional gas sleeve."
        )
    return (
        "Severe downside: collar + partial de-risking; "
        "larger gas/power downside sleeve or cross-commodity hedge."
    )


recommended_structure = hedge_instrument_mix(weighted_loss)

# ============================================================
# PART 2: CVaR95-informed hedge sizing (bootstrap tail risk)
# ============================================================

has_cvar = (
    "node_cvar_95" in hedge_table.columns
    and hedge_table["node_cvar_95"].notna().any()
)

if has_cvar:
    cvar_vals = hedge_table["node_cvar_95"].to_numpy(dtype=float)
    w_cvar    = hedge_table["probability"].to_numpy(dtype=float)

    # Apply same exposure convention to CVaR values
    if exposure_to_price == "short_price":
        cvar_loss = np.maximum(cvar_vals, 0.0)
    else:
        cvar_loss = np.maximum(-cvar_vals, 0.0)

    weighted_cvar_loss = float(np.sum(w_cvar * cvar_loss))

    if weighted_cvar_loss <= risk_budget_fraction:
        cvar_target_coverage = 0.0
    else:
        cvar_target_coverage = (
            (weighted_cvar_loss - risk_budget_fraction) / weighted_cvar_loss
        )

    raw_cvar_notional_pct = (
        cvar_target_coverage / hedge_efficiency if hedge_efficiency > 0 else 0.0
    )
    cvar_notional_pct = float(
        np.clip(raw_cvar_notional_pct * execution_haircut, 0.0, 0.80)
    )
    cvar_notional_usd = cvar_notional_pct * portfolio_value
else:
    weighted_cvar_loss = float("nan")
    cvar_target_coverage = float("nan")
    cvar_notional_pct = float("nan")
    cvar_notional_usd = float("nan")

# ============================================================
# Output: parameter block
# ============================================================

param_rows = [
    ("Portfolio value",          f"${portfolio_value:,.0f}"),
    ("Exposure mode",            exposure_to_price),
    ("Risk-budget fraction",     f"{risk_budget_fraction:.1%}"),
    ("Execution haircut",        f"{execution_haircut:.2f}"),
    ("Hedge efficiency",         f"{hedge_efficiency:.2f}"),
]

print("─" * 52)
print("Hedge Sizing Parameters")
print("─" * 52)
for label, value in param_rows:
    print(f"  {label:<30} {value}")
print()

# ============================================================
# Output: comparison table
# ============================================================

def _fmt(x, pct=False, usd=False):
    if isinstance(x, float) and (x != x):   # NaN check
        return "N/A"
    if usd:
        return f"${x:,.0f}"
    if pct:
        return f"{x:.4f}"
    return f"{x:.4f}"


comparison_rows = [
    {
        "Metric":                "Expected weighted loss",
        "Point-estimate (CAR)":  _fmt(weighted_loss, pct=True),
        "CVaR₉₅ (bootstrap)":   _fmt(weighted_cvar_loss, pct=True),
    },
    {
        "Metric":                "Target coverage",
        "Point-estimate (CAR)":  _fmt(target_coverage, pct=True),
        "CVaR₉₅ (bootstrap)":   _fmt(cvar_target_coverage, pct=True),
    },
    {
        "Metric":                "Hedge notional (% exposure)",
        "Point-estimate (CAR)":  _fmt(hedge_notional_pct, pct=True),
        "CVaR₉₅ (bootstrap)":   _fmt(cvar_notional_pct, pct=True),
    },
    {
        "Metric":                "Hedge notional (USD)",
        "Point-estimate (CAR)":  _fmt(hedge_notional_usd, usd=True),
        "CVaR₉₅ (bootstrap)":   _fmt(cvar_notional_usd, usd=True),
    },
]

comparison_df = pd.DataFrame(comparison_rows).set_index("Metric")
print("Hedge Sizing: Point-Estimate vs CVaR₉₅ (bootstrap)")
display(comparison_df)
print()

# ============================================================
# Output: terminal scenario detail
# ============================================================

print("Terminal scenario detail (used as hedge sizing input):")
detail_cols = ["terminal_resolution", "probability", "terminal_abnormal_return"]
if "node_cvar_95" in hedge_table.columns:
    detail_cols.append("node_cvar_95")

detail_df = hedge_table[detail_cols].copy()
rename_map = {
    "terminal_resolution":      "Terminal state",
    "probability":              "Prob",
    "terminal_abnormal_return": "CAR (point estimate)",
    "node_cvar_95":             "CVaR₉₅ (bootstrap)",
}
detail_df = detail_df.rename(columns={k: v for k, v in rename_map.items() if k in detail_df.columns})
display(detail_df)
print()

# ============================================================
# Output: recommendation
# ============================================================

print("─" * 52)
print("Recommended structure (point-estimate basis):")
print(f"  {recommended_structure}")
print()
print(
    "Note: the point-estimate notional uses the probability-weighted mean CAR "
    "across the four terminal branches. The CVaR₉₅ notional uses the probability-"
    "weighted mean of the worst-5% bootstrap paths at each terminal node and is "
    "the more conservative of the two. Both should be treated as indicative hedge "
    "demand rather than executable instructions: execution costs, market impact, "
    "and available instrument liquidity are not modelled here."
)

if not has_cvar:
    print(
        "\n[CVaR₉₅ sizing skipped: node_cvar_95 not available in scenario_summary. "
        "Re-run the branching simulation cell to generate bootstrap CVaR values.]"
    )
```

---

## Verification

After replacing the cell source, run the notebook from **Section 8a** onward and confirm:

1. The cell executes without error.
2. The parameter block prints the five configuration rows.
3. The comparison DataFrame has three rows: `Metric`, `Point-estimate (CAR)`, `CVaR₉₅ (bootstrap)`.
4. The terminal scenario detail table shows `CAR (point estimate)` and, if available, `CVaR₉₅ (bootstrap)` columns.
5. The recommended structure string is printed beneath the comparison table.
6. If `node_cvar_95` is present in `scenario_summary`, both notional columns contain finite values. If CVaR values are all zero or NaN, the bootstrap simulation in cell 48 did not complete successfully — re-run Section 8a first.

---

## Notes for Copilot

- **Do not touch cell 56** (`id=6a985b21`). That cell is the Section 8d scenario reporting block and is correct.
- Cell 58 (`id=bfb7b6d2`) is the **only cell to modify**. Its current content is a mis-pasted copy of the reporting block and should be entirely replaced.
- The `exposure_to_price = "short_price"` default matches the convention used in the thesis (a position harmed by rising electricity prices, consistent with Section 3.1.6 and Table 7).
- `node_cvar_95` flows from `scenario_summary_by_market` which is built in cell 48. No additional imports are required.
