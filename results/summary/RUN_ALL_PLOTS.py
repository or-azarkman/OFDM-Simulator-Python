"""
Run all comparison plot scripts to populate summary subdirectories.

This script runs all plot comparison scripts in the correct order to generate
all summary outputs organized in subdirectories:
  - ber/ - BER plots and tables
  - evm/ - EVM plots and tables
  - constellation/ - Constellation comparison plots
  - pilots/ - Pilot-based channel estimation plots

Run from project root: py results/summary/RUN_ALL_PLOTS.py
"""

import subprocess
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent.parent

def run_script(script_name: str, args: list = None) -> bool:
    """Run a Python script and return True if successful."""
    script_path = _project_root / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, cwd=str(_project_root), check=True, capture_output=False)
        print(f"✓ Success: {script_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {script_name} (exit code {e.returncode})")
        return False
    except Exception as e:
        print(f"✗ Error: {script_name} - {e}")
        return False

def main():
    """Run all comparison plot scripts."""
    print("="*60)
    print("Running All Comparison Plot Scripts")
    print("="*60)
    print("\nThis will generate all summary outputs in organized subdirectories:")
    print("  - results/summary/ber/")
    print("  - results/summary/evm/")
    print("  - results/summary/constellation/")
    print("  - results/summary/pilots/")
    print()
    
    scripts = [
        ("simulations/plot_ber_comparison.py", []),
        ("simulations/plot_evm_comparison.py", []),
        ("simulations/plot_constellation_comparison.py", []),
        ("simulations/plot_pilots_comparison.py", ["--symbols", "5000", "--equalize", "zf"]),
        ("simulations/plot_pilots_comparison.py", ["--symbols", "5000", "--equalize", "mmse"]),
    ]
    
    results = []
    for script, args in scripts:
        success = run_script(script, args)
        results.append((script, success))
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    for script, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {script}")
    
    all_success = all(success for _, success in results)
    if all_success:
        print("\n✓ All scripts completed successfully!")
        print("\nCheck outputs in:")
        print("  - results/summary/ber/")
        print("  - results/summary/evm/")
        print("  - results/summary/constellation/")
        print("  - results/summary/pilots/")
    else:
        print("\n⚠ Some scripts failed. Check output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
