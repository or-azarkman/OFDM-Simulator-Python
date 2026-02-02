"""
BER comparison plots from existing CSV results.

- AWGN vs Multipath (ZF): same symbol count, effect of channel + equalization.
- 500 vs 5000 symbols (multipath ZF): Monte Carlo convergence.
- ZF vs MMSE: multipath BER comparison when both runs exist.
- Comparison table: BER by scenario (AWGN, Multipath no eq, ZF, MMSE) per SNR.

Run from project root: py simulations/plot_ber_comparison.py [--symbols 5000]
Output (results/summary/ber/): ber_comparison_*.png, comparison_table.csv, comparison_table.md, comparison_table_readable.txt.
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import argparse
from typing import Dict, Tuple

import numpy as np
import matplotlib.pyplot as plt

from src.theory import theoretical_ber
from simulations.config import SimulationConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _load_ber_csv(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load SNR(dB), BER from CSV; return snr, ber arrays."""
    if not path.exists():
        return np.array([]), np.array([])
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]


def _multipath_dir(results: Path, symbols: int) -> Path:
    """Use multipath results dir: _multipath_zf or _multipath (legacy)."""
    for suffix in ("_multipath_zf", "_multipath_mmse", "_multipath"):
        d = results / f"{symbols}_symbols{suffix}"
        if d.exists() and (d / f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv").exists():
            return d
    return results / f"{symbols}_symbols_multipath_zf"


def plot_awgn_vs_multipath(symbols: int = 5000) -> None:
    """Plot BER vs SNR: AWGN (sim + theory) vs Multipath (ZF) for QPSK and 16-QAM."""
    root = _project_root()
    results = root / "results"
    awgn_dir = results / f"{symbols}_symbols"
    multipath_dir = _multipath_dir(results, symbols)
    summary_dir = SimulationConfig.summary_ber_dir()

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


def _multipath_dir_n(results: Path, n: int) -> Path:
    for suffix in ("_multipath_zf", "_multipath"):
        d = results / f"{n}_symbols{suffix}"
        if d.exists() and (d / f"ber_vs_snr_{n}symbols_multipath_qpsk.csv").exists():
            return d
    return results / f"{n}_symbols_multipath_zf"


def plot_symbols_comparison() -> None:
    """Plot 500 vs 5000 symbols (multipath ZF) to show Monte Carlo convergence."""
    root = _project_root()
    results = root / "results"
    summary_dir = SimulationConfig.summary_ber_dir()

    for mod, name in [("qpsk", "QPSK"), ("16qam", "16-QAM")]:
        d500 = _multipath_dir_n(results, 500)
        d5k = _multipath_dir_n(results, 5000)
        s500_snr, s500_ber = _load_ber_csv(d500 / f"ber_vs_snr_500symbols_multipath_{mod}.csv")
        s5k_snr, s5k_ber = _load_ber_csv(d5k / f"ber_vs_snr_5000symbols_multipath_{mod}.csv")
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


def plot_zf_vs_mmse(symbols: int = 5000) -> None:
    """Plot ZF vs MMSE BER (multipath) for QPSK and 16-QAM."""
    root = _project_root()
    results = root / "results"
    summary_dir = SimulationConfig.summary_ber_dir()
    d_zf = results / f"{symbols}_symbols_multipath_zf"
    d_mmse = results / f"{symbols}_symbols_multipath_mmse"
    if not d_zf.exists() or not d_mmse.exists():
        print(f"ZF vs MMSE plot skipped: need both {d_zf.name} and {d_mmse.name}. Run multipath with --equalize zf and --equalize mmse.")
        return
    snr_zf_q, ber_zf_q = _load_ber_csv(d_zf / f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_zf_16, ber_zf_16 = _load_ber_csv(d_zf / f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv")
    snr_mmse_q, ber_mmse_q = _load_ber_csv(d_mmse / f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_mmse_16, ber_mmse_16 = _load_ber_csv(d_mmse / f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv")
    if len(snr_zf_q) == 0 or len(snr_mmse_q) == 0:
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(snr_zf_q, ber_zf_q, "o-", label="QPSK ZF", color="C0", markersize=5)
    ax.semilogy(snr_zf_16, ber_zf_16, "s-", label="16-QAM ZF", color="C1", markersize=5)
    ax.semilogy(snr_mmse_q, ber_mmse_q, "^-", label="QPSK MMSE", color="C0", markersize=5, alpha=0.8)
    ax.semilogy(snr_mmse_16, ber_mmse_16, "v-", label="16-QAM MMSE", color="C1", markersize=5, alpha=0.8)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("BER")
    ax.set_title(f"Multipath: ZF vs MMSE — {symbols} symbols")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-5, 1)
    fig.tight_layout()
    out = summary_dir / f"ber_comparison_zf_vs_mmse_{symbols}symbols.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")


def _ber_by_snr(snr: np.ndarray, ber: np.ndarray) -> Dict[int, float]:
    """Return dict SNR(dB) -> BER for lookup."""
    return dict(zip(snr.astype(int).tolist(), ber.tolist()))


def save_comparison_table(symbols: int = 5000) -> None:
    """Build BER comparison table: AWGN, Multipath (no eq), ZF, MMSE per SNR. Save CSV + MD."""
    root = _project_root()
    results = root / "results"
    summary_dir = SimulationConfig.summary_ber_dir()

    # Scenario dirs: AWGN, multipath (no suffix = no eq), _zf, _mmse
    awgn_dir = results / f"{symbols}_symbols"
    mp_none_dir = results / f"{symbols}_symbols_multipath"
    mp_zf_dir = results / f"{symbols}_symbols_multipath_zf"
    mp_mmse_dir = results / f"{symbols}_symbols_multipath_mmse"

    def load_pair(d: Path, qpsk_name: str, qam16_name: str) -> Tuple[Dict[int, float], Dict[int, float]]:
        sq, bq = _load_ber_csv(d / qpsk_name)
        s16, b16 = _load_ber_csv(d / qam16_name)
        return _ber_by_snr(sq, bq), _ber_by_snr(s16, b16)

    awgn_q, awgn_16 = load_pair(
        awgn_dir,
        f"ber_vs_snr_{symbols}symbols_qpsk.csv",
        f"ber_vs_snr_{symbols}symbols_16qam.csv",
    )
    mp_none_q, mp_none_16 = load_pair(
        mp_none_dir,
        f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )
    mp_zf_q, mp_zf_16 = load_pair(
        mp_zf_dir,
        f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )
    mp_mmse_q, mp_mmse_16 = load_pair(
        mp_mmse_dir,
        f"ber_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"ber_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )

    all_snr = sorted(
        set(awgn_q) | set(awgn_16) | set(mp_none_q) | set(mp_none_16)
        | set(mp_zf_q) | set(mp_zf_16) | set(mp_mmse_q) | set(mp_mmse_16)
    )
    if not all_snr:
        print(f"No CSV data for {symbols} symbols. Run simulations first.")
        return

    def fmt(ber: float | None) -> str:
        return f"{ber:.6e}" if ber is not None else "—"

    # CSV: long format (SNR, Scenario, Modulation, BER) — easy to read and filter in Excel
    csv_path = summary_dir / "comparison_table.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("SNR_dB,Scenario,Modulation,BER\n")
        for snr in all_snr:
            for scenario, q_val, a16_val in [
                ("AWGN", awgn_q.get(snr), awgn_16.get(snr)),
                ("Multipath_noeq", mp_none_q.get(snr), mp_none_16.get(snr)),
                ("Multipath_ZF", mp_zf_q.get(snr), mp_zf_16.get(snr)),
                ("Multipath_MMSE", mp_mmse_q.get(snr), mp_mmse_16.get(snr)),
            ]:
                if q_val is not None:
                    f.write(f"{snr},{scenario},QPSK,{fmt(q_val)}\n")
                if a16_val is not None:
                    f.write(f"{snr},{scenario},16QAM,{fmt(a16_val)}\n")
    print(f"Saved: {csv_path}")

    # Markdown: four separate tables (one per scenario) for readable comparison
    md_path = summary_dir / "comparison_table.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# BER comparison — {symbols} symbols\n\n")
        for title, q_vals, a16_vals in [
            ("AWGN", awgn_q, awgn_16),
            ("Multipath (no eq)", mp_none_q, mp_none_16),
            ("Multipath (ZF)", mp_zf_q, mp_zf_16),
            ("Multipath (MMSE)", mp_mmse_q, mp_mmse_16),
        ]:
            f.write(f"## {title}\n\n")
            f.write("| SNR (dB) | QPSK | 16-QAM |\n")
            f.write("|----------|------|--------|\n")
            for snr in all_snr:
                f.write(f"| {snr} | {fmt(q_vals.get(snr))} | {fmt(a16_vals.get(snr))} |\n")
            f.write("\n")
        f.write("Scenarios: AWGN (no multipath), Multipath no eq, ZF, MMSE.\n")
    print(f"Saved: {md_path}")

    # Plain-text readable table (same 4 tables, easy to view in any editor)
    txt_path = summary_dir / "comparison_table_readable.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"BER comparison — {symbols} symbols\n")
        f.write("=" * 50 + "\n\n")
        for title, q_vals, a16_vals in [
            ("AWGN", awgn_q, awgn_16),
            ("Multipath (no eq)", mp_none_q, mp_none_16),
            ("Multipath (ZF)", mp_zf_q, mp_zf_16),
            ("Multipath (MMSE)", mp_mmse_q, mp_mmse_16),
        ]:
            f.write(f"--- {title} ---\n")
            f.write(f"{'SNR(dB)':>8}  {'QPSK':>12}  {'16-QAM':>12}\n")
            f.write("-" * 36 + "\n")
            for snr in all_snr:
                f.write(f"{snr:>8}  {fmt(q_vals.get(snr)):>12}  {fmt(a16_vals.get(snr)):>12}\n")
            f.write("\n")
    print(f"Saved: {txt_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BER comparison plots")
    parser.add_argument("--symbols", type=int, default=5000, help="Symbol count")
    parser.add_argument("--no-symbols-compare", action="store_true", help="Skip 500 vs 5000 plot")
    parser.add_argument("--no-table", action="store_true", help="Skip comparison table")
    args = parser.parse_args()
    plot_awgn_vs_multipath(symbols=args.symbols)
    plot_zf_vs_mmse(symbols=args.symbols)
    if not args.no_symbols_compare:
        plot_symbols_comparison()
    if not args.no_table:
        save_comparison_table(symbols=args.symbols)
