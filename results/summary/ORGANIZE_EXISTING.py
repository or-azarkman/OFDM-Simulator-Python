"""
Organize existing files in results/summary into subdirectories.

This script moves existing files to the new organized structure:
  summary/ber/ - BER comparison plots and tables
  summary/evm/ - EVM comparison plots and tables
  summary/constellation/ - Constellation comparison plots
  summary/pilots/ - Pilot-based channel estimation plots
  summary/docs/ - Summary documentation files

Run from project root: py results/summary/ORGANIZE_EXISTING.py
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

# Files to move (patterns)
ber_patterns = [
    "ber_comparison_*.png",
    "ber_500_vs_5000_*.png",
    "comparison_table.*",
]

evm_patterns = [
    "evm_comparison_*.png",
    "evm_comparison_table.*",
]

constellation_patterns = [
    "constellation_comparison_*.png",
]

docs_files = [
    "simulation_summary.md",
    "README.txt",
    "RUN_COMPARISON.txt",
]

# Move files
moved = []
skipped = []

# BER files
for pattern in ber_patterns:
    for f in _summary.glob(pattern):
        if f.is_file() and f.name != "ORGANIZE_EXISTING.py" and f.name != "ORGANIZE_SUMMARY.py":
            try:
                shutil.move(str(f), str(ber_dir / f.name))
                moved.append(f"BER: {f.name}")
            except Exception as e:
                skipped.append(f"{f.name}: {e}")

# EVM files
for pattern in evm_patterns:
    for f in _summary.glob(pattern):
        if f.is_file() and f.name != "ORGANIZE_EXISTING.py" and f.name != "ORGANIZE_SUMMARY.py":
            try:
                shutil.move(str(f), str(evm_dir / f.name))
                moved.append(f"EVM: {f.name}")
            except Exception as e:
                skipped.append(f"{f.name}: {e}")

# Constellation files
for pattern in constellation_patterns:
    for f in _summary.glob(pattern):
        if f.is_file() and f.name != "ORGANIZE_EXISTING.py" and f.name != "ORGANIZE_SUMMARY.py":
            try:
                shutil.move(str(f), str(constellation_dir / f.name))
                moved.append(f"Constellation: {f.name}")
            except Exception as e:
                skipped.append(f"{f.name}: {e}")

# Docs files
for fname in docs_files:
    f = _summary / fname
    if f.is_file():
        try:
            shutil.move(str(f), str(docs_dir / f.name))
            moved.append(f"Docs: {f.name}")
        except Exception as e:
            skipped.append(f"{f.name}: {e}")

print(f"Moved {len(moved)} files:")
for m in moved:
    print(f"  {m}")

if skipped:
    print(f"\nSkipped {len(skipped)} files:")
    for s in skipped:
        print(f"  {s}")

print("\nNew structure:")
print("  summary/ber/ - BER plots and tables")
print("  summary/evm/ - EVM plots and tables")
print("  summary/constellation/ - Constellation comparison plots")
print("  summary/pilots/ - Pilot-based channel estimation plots")
print("  summary/docs/ - Summary documentation")
