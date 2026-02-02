"""Run OFDM BER and EVM simulation from project root. Sets cwd and path then calls main(config)."""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulations.run_ber_and_constellation import main
from simulations.config import SimulationConfig
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OFDM simulation launcher")
    parser.add_argument("--symbols", type=int, default=5000, help="OFDM symbols")
    parser.add_argument("--trials", type=int, default=50, help="Monte Carlo trials")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-seed", action="store_true", help="No seed")
    parser.add_argument("--channel", type=str, default="awgn", choices=("awgn", "multipath"), help="Channel type")
    parser.add_argument("--equalize", type=str, default="zf", choices=("none", "zf", "mmse"), help="Equalizer for multipath")
    parser.add_argument("--pilots", action="store_true", help="Use pilot subcarriers for channel estimation (multipath)")
    args = parser.parse_args()
    config = SimulationConfig(
        num_symbols=args.symbols,
        monte_carlo_trials=args.trials,
        random_seed=None if args.no_seed else args.seed,
        channel_type=args.channel,
        equalize=args.equalize,
        use_pilots=args.pilots,
    )
    main(config)
