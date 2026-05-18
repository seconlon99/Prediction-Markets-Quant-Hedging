import json
import re
from pathlib import Path

p = Path("Energy_Lower_Freq_Nuclear.ipynb")
nb = json.loads(p.read_text())

for cell in nb.get("cells", []):
    if cell.get("cell_type") != "code":
        continue

    src = cell.get("source", [])
    text = "\n".join(src)

    if "# CSV-only: hourly Russia-Nuclear peace market data (last month)" in text:
        cell["source"] = [
            "# CSV-only: local PM hourly market data (last month)\n",
            "from pathlib import Path\n",
            "import pandas as pd\n",
            "\n",
            "csv_candidates = [\n",
            "    \"pm_hourly_last_month_pipeline_wide.csv\",\n",
            "    \"pm_hourly_last_month.csv\",\n",
            "]\n",
            "\n",
            "chosen_path = None\n",
            "for p in csv_candidates:\n",
            "    if Path(p).exists():\n",
            "        chosen_path = p\n",
            "        break\n",
            "\n",
            "if chosen_path is None:\n",
            "    raise FileNotFoundError(\n",
            "        \"No local PM hourly CSV found. Expected one of: \" + \", \".join(csv_candidates)\n",
            "    )\n",
            "\n",
            "pm_hourly_last_month = pd.read_csv(chosen_path)\n",
            "\n",
            "required_cols = {\"timestamp\", \"price_Yes\", \"price_No\"}\n",
            "missing = required_cols - set(pm_hourly_last_month.columns)\n",
            "if missing:\n",
            "    raise ValueError(f\"Missing required columns in {chosen_path}: {sorted(missing)}\")\n",
            "\n",
            "pm_hourly_last_month[\"timestamp\"] = pd.to_datetime(\n",
            "    pm_hourly_last_month[\"timestamp\"], utc=True, errors=\"coerce\"\n",
            ")\n",
            "pm_hourly_last_month = (\n",
            "    pm_hourly_last_month\n",
            "    .dropna(subset=[\"timestamp\"])\n",
            "    .sort_values(\"timestamp\")\n",
            "    .drop_duplicates(subset=[\"timestamp\"], keep=\"last\")\n",
            "    .reset_index(drop=True)\n",
            ")\n",
            "\n",
            "# Keep compatibility with downstream references\n",
            "now_utc = pd.Timestamp.now(tz=\"UTC\").floor(\"h\")\n",
            "window_start = now_utc - pd.Timedelta(days=29)\n",
            "selected_market = {\n",
            "    \"id\": \"csv_source\",\n",
            "    \"question\": \"Nuclear PM (from local CSV)\",\n",
            "    \"title\": \"Nuclear PM (from local CSV)\",\n",
            "    \"slug\": \"nuclear-pm-csv\",\n",
            "}\n",
            "source_used = f\"local_csv:{chosen_path}\"\n",
            "scored_candidates = []\n",
            "candidate_markets = [selected_market]\n",
            "\n",
            "print(\"Selected market:\", selected_market[\"question\"])\n",
            "print(\"Market id:\", selected_market[\"id\"])\n",
            "print(\"Data source used:\", source_used)\n",
            "print(\"Rows:\", pm_hourly_last_month.shape)\n",
            "print(pm_hourly_last_month.head())\n",
        ]

    if "# Import two daily prediction markets (2025) from local CSVs" in text:
        cell["source"] = [
            "# Import nuclear daily prediction market (2025) from local CSV\n",
            "import pandas as pd\n",
            "\n",
            "\n",
            "def load_daily_pm_csv(path, yes_col_name):\n",
            "    df = pd.read_csv(path)\n",
            "    required = {\"category\", \"Yes\"}\n",
            "    if not required.issubset(df.columns):\n",
            "        raise ValueError(f\"{path} must contain columns: {required}\")\n",
            "\n",
            "    out = df[[\"category\", \"Yes\"]].copy()\n",
            "    out[\"Date\"] = pd.to_datetime(out[\"category\"], utc=True, errors=\"coerce\").dt.floor(\"D\")\n",
            "    out = out.dropna(subset=[\"Date\"]).rename(columns={\"Yes\": yes_col_name})\n",
            "    out[yes_col_name] = pd.to_numeric(out[yes_col_name], errors=\"coerce\")\n",
            "    out = out.dropna(subset=[yes_col_name])\n",
            "    out = out[[\"Date\", yes_col_name]].sort_values(\"Date\").drop_duplicates(subset=[\"Date\"], keep=\"last\")\n",
            "    return out\n",
            "\n",
            "pm_nuclear = load_daily_pm_csv(\"NuclearDetonation.csv\", \"price_Yes_nuclear\")\n",
            "\n",
            "# Build 2025 daily PM panel\n",
            "start_utc = pd.Timestamp(\"2025-01-01\", tz=\"UTC\")\n",
            "end_utc = pd.Timestamp(\"2026-01-01\", tz=\"UTC\")\n",
            "daily_index_2025 = pd.DataFrame({\"Date\": pd.date_range(start_utc, end_utc, freq=\"D\", inclusive=\"left\")})\n",
            "\n",
            "pm_daily_2025 = (\n",
            "    daily_index_2025\n",
            "    .merge(pm_nuclear, on=\"Date\", how=\"left\")\n",
            "    .sort_values(\"Date\", ignore_index=True)\n",
            ")\n",
            "\n",
            "# Fill gaps with time interpolation + carry edges for clean daily alignment\n",
            "pm_daily_2025[\"price_Yes_nuclear\"] = pm_daily_2025[\"price_Yes_nuclear\"].interpolate(method=\"linear\", limit_direction=\"both\")\n",
            "\n",
            "# Backward-compatible single-market aliases for downstream cells\n",
            "pm_daily_2025[\"price_Yes\"] = pm_daily_2025[\"price_Yes_nuclear\"]\n",
            "pm_daily_2025[\"price_No\"] = 1.0 - pm_daily_2025[\"price_Yes\"]\n",
            "\n",
            "print(\"Daily PM panel built:\", pm_daily_2025.shape)\n",
            "print(pm_daily_2025.head())\n",
            "print(pm_daily_2025.tail())\n",
        ]

    if "mkt_keys = list(terminal_summary_by_market.keys())" in text and "Joint terminal scenarios for hedge sizing" in text:
        text = re.sub(
            r"mkt_keys = list\(terminal_summary_by_market\.keys\(\)\)\n.*?joint_terminal_scenarios = pd\.DataFrame\(joint_rows\)",
            (
                "mkt_keys = list(terminal_summary_by_market.keys())\n"
                "if len(mkt_keys) == 0:\n"
                "    raise ValueError(\"No market terminal summaries available for scenario construction.\")\n"
                "\n"
                "joint_rows = []\n"
                "if len(mkt_keys) == 1:\n"
                "    m1 = mkt_keys[0]\n"
                "    t1 = terminal_summary_by_market[m1].copy()\n"
                "    for _, r1 in t1.iterrows():\n"
                "        joint_rows.append(\n"
                "            {\n"
                "                \"branch\": f\"{m1}:{int(r1['terminal_resolution'])}\",\n"
                "                \"market1\": m1,\n"
                "                \"market1_resolution\": int(r1[\"terminal_resolution\"]),\n"
                "                \"market2\": m1,\n"
                "                \"market2_resolution\": int(r1[\"terminal_resolution\"]),\n"
                "                \"probability\": float(r1[\"total_probability\"]),\n"
                "                \"terminal_abnormal_return\": float(r1[\"expected_terminal_abnormal_return\"]),\n"
                "                \"max_drawdown\": float(r1[\"weighted_max_drawdown\"]),\n"
                "                \"horizon_days\": horizon,\n"
                "                \"joint_probability_source\": \"single_market_terminal_probs\",\n"
                "            }\n"
                "        )\n"
                "else:\n"
                "    m1, m2 = mkt_keys[0], mkt_keys[1]\n"
                "    t1 = terminal_summary_by_market[m1].copy()\n"
                "    t2 = terminal_summary_by_market[m2].copy()\n"
                "    for _, r1 in t1.iterrows():\n"
                "        for _, r2 in t2.iterrows():\n"
                "            p_joint = float(r1[\"total_probability\"] * r2[\"total_probability\"])\n"
                "            ret_joint = float(0.5 * r1[\"expected_terminal_abnormal_return\"] + 0.5 * r2[\"expected_terminal_abnormal_return\"])\n"
                "            mdd_joint = float(0.5 * r1[\"weighted_max_drawdown\"] + 0.5 * r2[\"weighted_max_drawdown\"])\n"
                "\n"
                "            joint_rows.append(\n"
                "                {\n"
                "                    \"branch\": f\"{m1}:{int(r1['terminal_resolution'])} | {m2}:{int(r2['terminal_resolution'])}\",\n"
                "                    \"market1\": m1,\n"
                "                    \"market1_resolution\": int(r1[\"terminal_resolution\"]),\n"
                "                    \"market2\": m2,\n"
                "                    \"market2_resolution\": int(r2[\"terminal_resolution\"]),\n"
                "                    \"probability\": p_joint,\n"
                "                    \"terminal_abnormal_return\": ret_joint,\n"
                "                    \"max_drawdown\": mdd_joint,\n"
                "                    \"horizon_days\": horizon,\n"
                "                    \"joint_probability_source\": \"product_of_market_terminal_probs\",\n"
                "                }\n"
                "            )\n"
                "\n"
                "joint_terminal_scenarios = pd.DataFrame(joint_rows)"
            ),
            text,
            flags=re.DOTALL,
        )
        cell["source"] = [line + "\n" for line in text.split("\n")]

out = json.dumps(nb, indent=2)
out = out.replace("Nuclear.csv", "NuclearDetonation.csv")
nb = json.loads(out)
p.write_text(json.dumps(nb, indent=2))
print("patched")
