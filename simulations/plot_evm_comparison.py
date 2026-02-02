"""
EVM comparison plots from existing CSV results.

- AWGN vs Multipath (ZF): EVM vs SNR.
- ZF vs MMSE: multipath EVM comparison.
- All scenarios: single plot with AWGN, Multipath no eq, ZF, MMSE (per modulation).
- Comparison table: EVM (%) by scenario per SNR.

Run from project root: python simulations/plot_evm_comparison.py [--symbols 5000]

Requires EVM CSV files from simulations. Generate them first:
  py run_simulation.py
  py run_simulation.py --channel multipath --equalize none
  py run_simulation.py --channel multipath --equalize zf
  py run_simulation.py --channel multipath --equalize mmse
(Use --symbols 500 for a quick run.)

Output (results/summary/): evm_comparison_*.png, evm_comparison_table.csv, evm_comparison_table.md.
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


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


_evm_hint_printed = False


def _print_evm_run_hint(symbols: int) -> None:
    """Print once per run how to generate EVM data."""
    global _evm_hint_printed
    if _evm_hint_printed:
        return
    _evm_hint_printed = True
    print(
        "Generate EVM data by running simulations (each run now includes EVM):\n"
        f"  py run_simulation.py --symbols {symbols}\n"
        f"  py run_simulation.py --channel multipath --equalize none --symbols {symbols}\n"
        f"  py run_simulation.py --channel multipath --equalize zf --symbols {symbols}\n"
        f"  py run_simulation.py --channel multipath --equalize mmse --symbols {symbols}\n"
        "Then run this script again."
    )


def _load_evm_csv(path: Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load SNR_dB, EVM_pct from CSV; return snr, evm arrays."""
    if not path.exists():
        return np.array([]), np.array([])
    data = np.loadtxt(path, delimiter=",", skiprows=1)
    return data[:, 0], data[:, 1]


def _multipath_dir(results: Path, symbols: int) -> Path:
    for suffix in ("_multipath_zf", "_multipath_mmse", "_multipath"):
        d = results / f"{symbols}_symbols{suffix}"
        if d.exists() and (d / f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv").exists():
            return d
    return results / f"{symbols}_symbols_multipath_zf"


def plot_evm_awgn_vs_multipath(symbols: int = 5000) -> None:
    """Plot EVM vs SNR: AWGN vs Multipath (ZF) for QPSK and 16-QAM."""
    root = _project_root()
    results = root / "results"
    awgn_dir = results / f"{symbols}_symbols"
    multipath_dir = _multipath_dir(results, symbols)
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    snr_awgn_q, evm_awgn_q = _load_evm_csv(awgn_dir / f"evm_vs_snr_{symbols}symbols_qpsk.csv")
    snr_awgn_16, evm_awgn_16 = _load_evm_csv(awgn_dir / f"evm_vs_snr_{symbols}symbols_16qam.csv")
    snr_mp_q, evm_mp_q = _load_evm_csv(multipath_dir / f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_mp_16, evm_mp_16 = _load_evm_csv(multipath_dir / f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv")

    if len(snr_awgn_q) == 0 and len(snr_mp_q) == 0:
        print(f"No EVM CSV data found for {symbols} symbols.")
        _print_evm_run_hint(symbols)
        return

    fig, ax = plt.subplots(figsize=(8, 5))
    if len(snr_awgn_q):
        ax.plot(snr_awgn_q, evm_awgn_q, "o-", label="QPSK AWGN", color="C0", markersize=5)
        ax.plot(snr_awgn_16, evm_awgn_16, "s-", label="16-QAM AWGN", color="C1", markersize=5)
    if len(snr_mp_q):
        ax.plot(snr_mp_q, evm_mp_q, "^-", label="QPSK Multipath (ZF)", color="C0", markersize=5, alpha=0.9)
        ax.plot(snr_mp_16, evm_mp_16, "v-", label="16-QAM Multipath (ZF)", color="C1", markersize=5, alpha=0.9)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("EVM (%)")
    ax.set_title(f"EVM vs SNR — AWGN vs Multipath (ZF equalized)\n{symbols} symbols")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = summary_dir / f"evm_comparison_awgn_vs_multipath_{symbols}symbols.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")


def plot_evm_zf_vs_mmse(symbols: int = 5000) -> None:
    """Plot ZF vs MMSE EVM (multipath) for QPSK and 16-QAM."""
    root = _project_root()
    results = root / "results"
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    d_zf = results / f"{symbols}_symbols_multipath_zf"
    d_mmse = results / f"{symbols}_symbols_multipath_mmse"
    if not d_zf.exists() or not d_mmse.exists():
        print(f"ZF vs MMSE EVM plot skipped: need both {d_zf.name} and {d_mmse.name}.")
        _print_evm_run_hint(symbols)
        return
    snr_zf_q, evm_zf_q = _load_evm_csv(d_zf / f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_zf_16, evm_zf_16 = _load_evm_csv(d_zf / f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv")
    snr_mmse_q, evm_mmse_q = _load_evm_csv(d_mmse / f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv")
    snr_mmse_16, evm_mmse_16 = _load_evm_csv(d_mmse / f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv")
    if len(snr_zf_q) == 0 or len(snr_mmse_q) == 0:
        _print_evm_run_hint(symbols)
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(snr_zf_q, evm_zf_q, "o-", label="QPSK ZF", color="C0", markersize=5)
    ax.plot(snr_zf_16, evm_zf_16, "s-", label="16-QAM ZF", color="C1", markersize=5)
    ax.plot(snr_mmse_q, evm_mmse_q, "^-", label="QPSK MMSE", color="C0", markersize=5, alpha=0.8)
    ax.plot(snr_mmse_16, evm_mmse_16, "v-", label="16-QAM MMSE", color="C1", markersize=5, alpha=0.8)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("EVM (%)")
    ax.set_title(f"Multipath: ZF vs MMSE EVM — {symbols} symbols")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = summary_dir / f"evm_comparison_zf_vs_mmse_{symbols}symbols.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")


def plot_evm_all_scenarios(symbols: int = 5000, modulation: str = "16QAM") -> None:
    """Plot EVM vs SNR for all four scenarios (AWGN, Multipath no eq, ZF, MMSE) — one modulation."""
    root = _project_root()
    results = root / "results"
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    mod = modulation.upper()
    mod_key = "qpsk" if mod == "QPSK" else "16qam"
    mod_label = "QPSK" if mod == "QPSK" else "16-QAM"
    awgn_dir = results / f"{symbols}_symbols"
    mp_none_dir = results / f"{symbols}_symbols_multipath"
    mp_zf_dir = results / f"{symbols}_symbols_multipath_zf"
    mp_mmse_dir = results / f"{symbols}_symbols_multipath_mmse"
    awgn_file = f"evm_vs_snr_{symbols}symbols_{mod_key}.csv"
    mp_file = f"evm_vs_snr_{symbols}symbols_multipath_{mod_key}.csv"
    snr_a, evm_a = _load_evm_csv(awgn_dir / awgn_file)
    snr_n, evm_n = _load_evm_csv(mp_none_dir / mp_file)
    snr_z, evm_z = _load_evm_csv(mp_zf_dir / mp_file)
    snr_m, evm_m = _load_evm_csv(mp_mmse_dir / mp_file)
    if len(snr_a) == 0 and len(snr_n) == 0 and len(snr_z) == 0 and len(snr_m) == 0:
        print(f"No EVM data for {mod_label} {symbols} symbols.")
        _print_evm_run_hint(symbols)
        return
    fig, ax = plt.subplots(figsize=(8, 5))
    if len(snr_a):
        ax.plot(snr_a, evm_a, "o-", label="AWGN", color="C0", markersize=5)
    if len(snr_n):
        ax.plot(snr_n, evm_n, "s-", label="Multipath (no eq)", color="C1", markersize=5)
    if len(snr_z):
        ax.plot(snr_z, evm_z, "^-", label="Multipath (ZF)", color="C2", markersize=5)
    if len(snr_m):
        ax.plot(snr_m, evm_m, "v-", label="Multipath (MMSE)", color="C3", markersize=5)
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("EVM (%)")
    ax.set_title(f"EVM vs SNR — All scenarios ({mod_label}, {symbols} symbols)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    out = summary_dir / f"evm_comparison_all_scenarios_{mod_key}_{symbols}symbols.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")


def _evm_by_snr(snr: np.ndarray, evm: np.ndarray) -> Dict[int, float]:
    return dict(zip(snr.astype(int).tolist(), evm.tolist()))


def save_evm_comparison_table(symbols: int = 5000) -> None:
    """Build EVM comparison table: AWGN, Multipath (no eq), ZF, MMSE per SNR. Save CSV + MD."""
    root = _project_root()
    results = root / "results"
    summary_dir = results / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    awgn_dir = results / f"{symbols}_symbols"
    mp_none_dir = results / f"{symbols}_symbols_multipath"
    mp_zf_dir = results / f"{symbols}_symbols_multipath_zf"
    mp_mmse_dir = results / f"{symbols}_symbols_multipath_mmse"

    def load_pair(d: Path, qpsk_name: str, qam16_name: str) -> Tuple[Dict[int, float], Dict[int, float]]:
        sq, eq = _load_evm_csv(d / qpsk_name)
        s16, e16 = _load_evm_csv(d / qam16_name)
        return _evm_by_snr(sq, eq), _evm_by_snr(s16, e16)

    awgn_q, awgn_16 = load_pair(awgn_dir, f"evm_vs_snr_{symbols}symbols_qpsk.csv", f"evm_vs_snr_{symbols}symbols_16qam.csv")
    mp_none_q, mp_none_16 = load_pair(
        mp_none_dir,
        f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )
    mp_zf_q, mp_zf_16 = load_pair(
        mp_zf_dir,
        f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )
    mp_mmse_q, mp_mmse_16 = load_pair(
        mp_mmse_dir,
        f"evm_vs_snr_{symbols}symbols_multipath_qpsk.csv",
        f"evm_vs_snr_{symbols}symbols_multipath_16qam.csv",
    )
    all_snr = sorted(
        set(awgn_q) | set(awgn_16) | set(mp_none_q) | set(mp_none_16)
        | set(mp_zf_q) | set(mp_zf_16) | set(mp_mmse_q) | set(mp_mmse_16)
    )
    if not all_snr:
        print(f"No EVM CSV data for {symbols} symbols.")
        _print_evm_run_hint(symbols)
        return

    def fmt(evm: float | None) -> str:
        return f"{evm:.2f}" if evm is not None else "—"

    csv_path = summary_dir / "evm_comparison_table.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("SNR_dB,Scenario,Modulation,EVM_pct\n")
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

    md_path = summary_dir / "evm_comparison_table.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# EVM (%) comparison — {symbols} symbols\n\n")
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
        f.write("EVM = Error Vector Magnitude (%). Lower is better.\n")
    print(f"Saved: {md_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EVM comparison plots")
    parser.add_argument("--symbols", type=int, default=5000, help="Symbol count")
    parser.add_argument("--no-table", action="store_true", help="Skip comparison table")
    args = parser.parse_args()
    plot_evm_awgn_vs_multipath(symbols=args.symbols)
    plot_evm_zf_vs_mmse(symbols=args.symbols)
    plot_evm_all_scenarios(symbols=args.symbols, modulation="QPSK")
    plot_evm_all_scenarios(symbols=args.symbols, modulation="16QAM")
    if not args.no_table:
        save_evm_comparison_table(symbols=args.symbols)
