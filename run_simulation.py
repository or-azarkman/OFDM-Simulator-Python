"""
Launcher: run OFDM simulation from project root.

Use this so the run works no matter where your terminal/Cursor started.
- From Cursor: open this file and Run (F5 or Run Python File).
- From terminal: python run_simulation.py [--symbols 500] [--trials 20]
"""

import os
import sys
from pathlib import Path

# Project root = directory where this script lives
PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now run the simulation
from simulations.run_ber_and_constellation import main
from simulations.config import SimulationConfig
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OFDM simulation launcher")
    parser.add_argument("--symbols", type=int, default=5000, help="OFDM symbols")
    parser.add_argument("--trials", type=int, default=50, help="Monte Carlo trials")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-seed", action="store_true", help="No seed (non-reproducible)")
    args = parser.parse_args()
    config = SimulationConfig(
        num_symbols=args.symbols,
        monte_carlo_trials=args.trials,
        random_seed=None if args.no_seed else args.seed,
    )
    main(config)
