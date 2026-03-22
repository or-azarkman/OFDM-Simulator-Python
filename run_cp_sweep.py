"""Run EVM/BER vs CP length from project root (for LinkedIn plot)."""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulations.run_evm_ber_vs_cp import main

if __name__ == "__main__":
    main()
