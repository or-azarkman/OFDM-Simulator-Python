"""
Plot BER comparison: AWGN vs Multipath (optional: 500 vs 5000 symbols).

Loads existing CSV results and generates comparison plots for portfolio/interview:
- AWGN vs Multipath (same symbol count) — shows effect of channel + equalization
- Optional: 500 vs 5000 symbols — shows Monte Carlo convergence

Run from project root: py simulations/plot_ber_comparison.py [--symbols 5000]
Output: results/summary/ber_comparison_awgn_vs_multipath_<N>symbols.png
"""

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt

from src.theory import theoretical_ber


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_ber_csv(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load SNR(dB), BER from CSV; return snr, ber arrays."""
    if not path.exists():
        return np.array([]), np.array([])
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]


def plot_awgn_vs_multipath(symbols: int = 5000) -> None:
    """Plot BER vs SNR: AWGN (sim + theory) vs Multipath for QPSK and 16-QAM."""
    root = _project_root()
    results = root / "results"
    awgn_dir = results / f"{symbols}_symbols"
    multipath_dir = results / f"{symbols}_symbols_multipath"
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    snr_awgn_q, ber_awgn_q = _load_ber_csv(awgn_dir / f"ber_vs_snr_{symbols}symbols_qpsk.csv")
    snr_awgn_16, ber_awgn_16 = _load_ber_csv(awgn_dir / f"ber_vs_snr_{symbols}symbols_16qam.csv")
    snr_mp_q, ber_mp_q = _load_ber_csv(multipath_dir / f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_mp_16, ber_mp_16 = _load_ber_csv(multipath_dir / f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv")

    if len(snr_awgn_q) == 0 and len(snr_mp_q) == 0:
        print(f"No CSV data found for {symbols} symbols. Run AWGN and multipath first.")
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    snr_ref = snr_awgn_q if len(snr_awgn_q) else snr_mp_q

    if len(snr_awgn_q):
        ax.semilogy(snr_awgn_q, ber_awgn_q, "o-", label="QPSK AWGN (sim)", color="C0", markersize=5)
        ax.semilogy(snr_awgn_16, ber_awgn_16, "s-", label="16-QAM AWGN (sim)", color="C1", markersize=5)
        theory_q = theoretical_ber(snr_ref, "QPSK")
        theory_16 = theoretical_ber(snr_ref, "16QAM")
        ax.semilogy(snr_ref, theory_q, "--", label="QPSK theoretical", color="C0", alpha=0.8)
        ax.semilogy(snr_ref, theory_16, "--", label="16-QAM theoretical", color="C1", alpha=0.8)
    if len(snr_mp_q):
        ax.semilogy(snr_mp_q, ber_mp_q, "^-", label="QPSK Multipath (ZF)", color="C0", markersize=5, alpha=0.9)
        ax.semilogy(snr_mp_16, ber_mp_16, "v-", label="16-QAM Multipath (ZF)", color="C1", markersize=5, alpha=0.9)

    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Bit Error Rate (BER)")
    ax.set_title(f"BER vs SNR — AWGN vs Multipath (ZF equalized)\n{symbols} symbols")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-5, 1)
    fig.tight_layout()
    out = summary_dir / f"ber_comparison_awgn_vs_multipath_{symbols}symbols.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")


def plot_symbols_comparison() -> None:
    """Plot 500 vs 5000 symbols (multipath) to show Monte Carlo convergence."""
    root = _project_root()
    results = root / "results"
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    for mod, name in [("qpsk", "QPSK"), ("16qam", "16-QAM")]:
        s500_snr, s500_ber = _load_ber_csv(results / f"500_symbols_multipath" / f"ber_vs_snr_500symbols_multipath_{mod}.csv")
        s5k_snr, s5k_ber = _load_ber_csv(results / f"5000_symbols_multipath" / f"ber_vs_snr_5000symbols_multipath_{mod}.csv")
        if len(s500_snr) == 0 or len(s5k_snr) == 0:
            continue
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.semilogy(s500_snr, s500_ber, "o-", label="500 symbols", markersize=5)
        ax.semilogy(s5k_snr, s5k_ber, "s-", label="5000 symbols", markersize=5)
        ax.set_xlabel("SNR (dB)")
        ax.set_ylabel("BER")
        ax.set_title(f"Multipath (ZF) — {name}: 500 vs 5000 symbols")
        ax.legend()
        ax.grid(True, which="both", alpha=0.3)
        ax.set_ylim(1e-5, 1)
        fig.tight_layout()
        out = summary_dir / f"ber_500_vs_5000_multipath_{mod}.png"
        fig.savefig(out, dpi=300)
        plt.close(fig)
        print(f"Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BER comparison plots (AWGN vs Multipath, 500 vs 5000)")
    parser.add_argument("--symbols", type=int, default=5000, help="Symbol count for AWGN vs Multipath plot")
    parser.add_argument("--no-symbols-compare", action="store_true", help="Skip 500 vs 5000 plot")
    args = parser.parse_args()
    plot_awgn_vs_multipath(symbols=args.symbols)
    if not args.no_symbols_compare:
        plot_symbols_comparison()
