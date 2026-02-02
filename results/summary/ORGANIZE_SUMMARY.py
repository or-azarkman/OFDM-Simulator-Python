"""
Organize results/summary directory into subdirectories for better clarity.

Creates:
  summary/ber/ - BER comparison plots and tables
  summary/evm/ - EVM comparison plots and tables
  summary/constellation/ - Constellation comparison plots
  summary/pilots/ - Pilot-based channel estimation plots (moved from run directories)
  summary/docs/ - Summary documentation files

Run from project root: py results/summary/ORGANIZE_SUMMARY.py
"""

import shutil
from pathlib import Path

_summary = Path(__file__).parent

# Create subdirectories
ber_dir = _summary / "ber"
evm_dir = _summary / "evm"
constellation_dir = _summary / "constellation"
pilots_dir = _summary / "pilots"
docs_dir = _summary / "docs"

for d in [ber_dir, evm_dir, constellation_dir, pilots_dir, docs_dir]:
    d.mkdir(exist_ok=True)

# Move BER files
ber_files = [
    "ber_comparison_awgn_vs_multipath_*.png",
    "ber_500_vs_5000_*.png",
    "ber_comparison_zf_vs_mmse_*.png",
    "comparison_table.csv",
    "comparison_table.md",
    "comparison_table_readable.txt",
]

# Move EVM files
evm_files = [
    "evm_comparison_awgn_vs_multipath_*.png",
    "evm_comparison_zf_vs_mmse_*.png",
    "evm_comparison_all_scenarios_*.png",
    "evm_comparison_table.csv",
    "evm_comparison_table.md",
]

# Move constellation files
constellation_files = [
    "constellation_comparison_*.png",
]

# Move docs files
docs_files = [
    "simulation_summary.md",
    "README.txt",
    "RUN_COMPARISON.txt",
]

# Move files
moved = []
for pattern in ber_files:
    for f in _summary.glob(pattern):
        if f.is_file():
            shutil.move(str(f), str(ber_dir / f.name))
            moved.append(f"BER: {f.name}")

for pattern in evm_files:
    for f in _summary.glob(pattern):
        if f.is_file():
            shutil.move(str(f), str(evm_dir / f.name))
            moved.append(f"EVM: {f.name}")

for pattern in constellation_files:
    for f in _summary.glob(pattern):
        if f.is_file():
            shutil.move(str(f), str(constellation_dir / f.name))
            moved.append(f"Constellation: {f.name}")

for fname in docs_files:
    f = _summary / fname
    if f.is_file():
        shutil.move(str(f), str(docs_dir / f.name))
        moved.append(f"Docs: {f.name}")

print(f"Moved {len(moved)} files:")
for m in moved:
    print(f"  {m}")

print("\nNew structure:")
print("  summary/ber/ - BER plots and tables")
print("  summary/evm/ - EVM plots and tables")
print("  summary/constellation/ - Constellation comparison plots")
print("  summary/pilots/ - Pilot-based channel estimation plots (to be populated)")
print("  summary/docs/ - Summary documentation")
