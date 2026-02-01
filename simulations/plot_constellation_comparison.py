"""
Constellation comparison: same signal at 0, 10, 20 dB for AWGN vs Multipath (no eq, ZF, MMSE).

Generates one OFDM stream per (modulation, SNR), then runs it through four scenarios
so constellations are directly comparable. Output: 4 columns × 3 rows (SNR) per modulation.

Run from project root: py simulations/plot_constellation_comparison.py [--symbols 100]
Output: results/summary/constellation_comparison_QPSK.png, constellation_comparison_16QAM.png
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import argparse
import numpy as np
import matplotlib.pyplot as plt

from simulations.config import SimulationConfig
from simulations.run_ber_and_constellation import get_freq_symbols_from_stream
from src.transmitter import generate_random_bits, generate_ofdm_stream


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _scenario_configs(num_symbols: int, seed: int = 42) -> list[tuple[str, SimulationConfig]]:
    """(label, config) for AWGN, Multipath no eq, ZF, MMSE."""
    def make(channel: str, equalize: str) -> SimulationConfig:
        return SimulationConfig(
            fft_size=64,
            cp_len=16,
            num_symbols=num_symbols,
            random_seed=seed,
            channel_type=channel,
            equalize=equalize,
        )
    return [
        ("AWGN", make("awgn", "zf")),
        ("Multipath (no eq)", make("multipath", "none")),
        ("Multipath (ZF)", make("multipath", "zf")),
        ("Multipath (MMSE)", make("multipath", "mmse")),
    ]


def plot_constellation_comparison(
    num_symbols: int = 100,
    snr_list: tuple[int, ...] = (0, 10, 20),
    seed: int = 42,
) -> None:
    """Plot 4 (scenarios) × 3 (SNR) constellation grid for QPSK and 16-QAM."""
    root = _project_root()
    summary_dir = root / "results" / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    scenarios = _scenario_configs(num_symbols, seed)
    n_cols = len(scenarios)
    n_rows = len(snr_list)

    for modulation, mod_name in [("QPSK", "QPSK"), ("16QAM", "16-QAM")]:
        bits_per_sub = 2 if modulation == "QPSK" else 4
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(4 * n_cols, 4 * n_rows))
        if n_rows == 1:
            axes = axes.reshape(1, -1)

        for row, snr_db in enumerate(snr_list):
            np.random.seed(seed)
            total_bits = num_symbols * 64 * bits_per_sub
            bits_tx = generate_random_bits(total_bits)
            ofdm_stream = generate_ofdm_stream(bits_tx, 64, 16, modulation)

            for col, (label, config) in enumerate(scenarios):
                freq_syms = get_freq_symbols_from_stream(ofdm_stream, config, float(snr_db))
                ax = axes[row, col]
                ax.scatter(
                    freq_syms.real.flatten(),
                    freq_syms.imag.flatten(),
                    s=2,
                    alpha=0.5,
                )
                ax.set_title(f"{label}\n{snr_db} dB")
                ax.set_xlabel("Real")
                ax.set_ylabel("Imag")
                ax.grid(True, alpha=0.3)
                ax.axis("equal")

        fig.suptitle(f"Constellation comparison — {mod_name} ({num_symbols} symbols, seed={seed})")
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        out = summary_dir / f"constellation_comparison_{mod_name.replace('-', '')}.png"
        fig.savefig(out, dpi=300)
        plt.close(fig)
        print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Constellation comparison: AWGN vs Multipath (no eq, ZF, MMSE)")
    parser.add_argument("--symbols", type=int, default=100, help="OFDM symbols per scenario")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()
    plot_constellation_comparison(num_symbols=args.symbols, seed=args.seed)
