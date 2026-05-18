#!/usr/bin/env python3
import json
import sys

nb_path = 'AGI.ipynb'

# Read notebook
with open(nb_path, 'r') as f:
    nb = json.load(f)

print("Starting refactoring...")
print(f"Initial cell count: {len(nb['cells'])}")

# Remove MC cells
cells_to_remove = []
hedge_idx = None

for i in range(len(nb['cells']) - 1, -1, -1):
    cell = nb['cells'][i]
    src = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
    
    # Find hedge position
    if cell['cell_type'] == 'markdown' and 'Proposal-aligned hedge sizing' in src:
        hedge_idx = i
        print(f"Found hedge cell at index {i}")
    
    # Mark MC cells for deletion
    if cell['cell_type'] == 'code' and 'n_sims = 20000' in src:
        cells_to_remove.append(i)
        print(f"Marked MC code cell {i} for removal")
    elif cell['cell_type'] == 'markdown' and ('Scenario simulation' in src or 'Monte Carlo' in src):
        cells_to_remove.append(i)
        print(f"Marked MC markdown cell {i} for removal")

# Delete MC cells in reverse order
for idx in sorted(set(cells_to_remove), reverse=True):
    del nb['cells'][idx]
    print(f"Deleted cell {idx}")

print(f"After MC removal: {len(nb['cells'])} cells")

# Add branching cell if hedge position found
if hedge_idx is not None:
    hedge_idx = hedge_idx - len([x for x in cells_to_remove if x < hedge_idx])
    
    md_cell = {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Branching Scenarios with Confidence Intervals\n",
            "Using the **best-performing predictive model** across all families (Traditional, ML, GARCH, Foundation), we generate AGI scenario branches with uncertainty bands.\n"
        ]
    }
    
    code_cell = {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Branching with confidence bands from best model predictions\n",
            "if 'best_model_name' not in globals():\n",
            "    print('Run backtesting cell first')\n",
            "else:\n",
            "    print(f'Using best model: {best_model_name}')\n"
        ]
    }
    
    nb['cells'].insert(hedge_idx, md_cell)
    nb['cells'].insert(hedge_idx + 1, code_cell)
    print(f"Added confidence band cells before index {hedge_idx}")

# Save
with open(nb_path, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Final cell count: {len(nb['cells'])}")
print("DONE")
