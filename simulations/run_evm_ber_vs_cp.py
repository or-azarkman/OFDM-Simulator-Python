"""
run_evm_ber_vs_cp.py

EVM and BER vs Cyclic Prefix (CP) length — for LinkedIn / reports.

- X-axis: CP length (samples)
- Y-axis: EVM (%) and/or BER
- Shows degradation when CP is shorter than the channel delay spread (ISI).

Uses multipath channel with linear convolution so that short CP causes
real inter-symbol interference (ISI). Run from project root:

  python -m simulations.run_evm_ber_vs_cp

Optional: --snr 12 --trials 40 --cp 0 2 4 8 12 16 24
"""

from pathlib import Path
import argparse
import numpy as np
import matplotlib.pyplot as plt

from simulations.config import SimulationConfig
from src.transmitter import generate_random_bits, generate_ofdm_stream
from src.receiver import fft_ofdm, demodulate_ofdm_symbols, compute_ber
from src.channel import multipath_channel_linear
from src.equalizers import equalize_zf
from src.evm import compute_evm


def _channel_freq_response(fft_size: int, taps: np.ndarray) -> np.ndarray:
    """H_k for ZF equalization (same as in multipath model)."""
    h_pad = np.zeros(fft_size, dtype=complex)
    h_pad[: len(taps)] = taps
    return np.fft.fft(h_pad)


def run_ber_evm_at_cp(
    cp_len: int,
    config: SimulationConfig,
    snr_db: float,
    n_trials: int,
    modulation: str = "QPSK",
) -> tuple[float, float]:
    """
    Run BER and EVM at a single CP length using linear-convolution multipath
    (ISI when CP < delay spread). Returns (avg_ber, avg_evm_pct).
    """
    fft_size = config.fft_size
    taps = config.multipath_taps
    num_symbols = config.num_symbols
    bits_per_sub = 2 if modulation.upper() == "QPSK" else 4
    total_bits = num_symbols * fft_size * bits_per_sub

    H = _channel_freq_response(fft_size, taps)
    ber_list = []
    evm_list = []

    for _ in range(n_trials):
        bits_tx = generate_random_bits(total_bits)
        ofdm_stream = generate_ofdm_stream(
            bits_tx, fft_size, cp_len, modulation, None, None
        )
        # Linear convolution multipath → ISI when CP short
        noisy = multipath_channel_linear(
            ofdm_stream, taps, snr_db, cp_len, fft_size
        )
        # noisy is (n_symbols, n_fft), no CP to remove
        freq_rx = fft_ofdm(noisy)
        freq_eq = equalize_zf(freq_rx, H)
        bits_rx = demodulate_ofdm_symbols(freq_eq, modulation)
        ber_list.append(compute_ber(bits_tx, bits_rx))

        # EVM: need tx frequency symbols (no channel)
        ofdm_no_cp = ofdm_stream[:, cp_len:]
        freq_tx = fft_ofdm(ofdm_no_cp)
        evm_list.append(
            compute_evm(freq_eq.flatten(), freq_tx.flatten(), percent=True)
        )

    return float(np.mean(ber_list)), float(np.mean(evm_list))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="EVM/BER vs CP length (multipath with ISI)"
    )
    parser.add_argument(
        "--snr",
        type=float,
        default=12.0,
        help="SNR in dB (single point for CP sweep)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=40,
        help="Monte Carlo trials per CP value",
    )
    parser.add_argument(
        "--symbols",
        type=int,
        default=2000,
        help="OFDM symbols per trial",
    )
    parser.add_argument(
        "--cp",
        type=int,
        nargs="+",
        default=[0, 2, 4, 6, 8, 10, 12, 16, 20, 24],
        help="CP lengths to sweep",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Output directory (default: results/summary/cp_sweep)",
    )
    args = parser.parse_args()

    np.random.seed(args.seed)
    config = SimulationConfig(
        num_symbols=args.symbols,
        fft_size=64,
        channel_type="multipath",
        equalize="zf",
    )
    cp_lengths = sorted(set(args.cp))
    delay_spread = max(0, len(config.multipath_taps) - 1)

    print(f"EVM/BER vs CP length @ SNR = {args.snr} dB")
    print(f"Channel delay spread (taps-1) = {delay_spread} samples")
    print(f"CP values: {cp_lengths}")

    ber_qpsk = []
    ber_16qam = []
    evm_qpsk = []
    evm_16qam = []

    for cp in cp_lengths:
        print(f"  CP = {cp} ...", end=" ", flush=True)
        b_q, e_q = run_ber_evm_at_cp(
            cp, config, args.snr, args.trials, "QPSK"
        )
        b_16, e_16 = run_ber_evm_at_cp(
            cp, config, args.snr, args.trials, "16QAM"
        )
        ber_qpsk.append(b_q)
        ber_16qam.append(b_16)
        evm_qpsk.append(e_q)
        evm_16qam.append(e_16)
        print(f"BER QPSK={b_q:.2e} 16QAM={b_16:.2e}  EVM QPSK={e_q:.1f}% 16QAM={e_16:.1f}%")

    ber_qpsk = np.array(ber_qpsk)
    ber_16qam = np.array(ber_16qam)
    evm_qpsk = np.array(evm_qpsk)
    evm_16qam = np.array(evm_16qam)

    out_dir = Path(args.out) if args.out else (
        config.results_dir / "summary" / "cp_sweep"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    # Plot: EVM and BER vs CP length (two subplots)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), sharex=True)

    ax1.plot(
        cp_lengths,
        evm_qpsk,
        "o-",
        label="QPSK",
        color="C0",
        markersize=7,
    )
    ax1.plot(
        cp_lengths,
        evm_16qam,
        "s-",
        label="16-QAM",
        color="C1",
        markersize=7,
    )
    ax1.axvline(
        x=delay_spread,
        color="gray",
        linestyle="--",
        alpha=0.8,
        label=f"Delay spread = {delay_spread}",
    )
    ax1.set_ylabel("EVM (%)")
    ax1.set_title(f"EVM vs CP length — Multipath (ZF), SNR = {args.snr} dB")
    ax1.legend(loc="best")
    ax1.grid(True, alpha=0.3)

    ax2.semilogy(
        cp_lengths,
        np.maximum(ber_qpsk, 1e-6),
        "o-",
        label="QPSK",
        color="C0",
        markersize=7,
    )
    ax2.semilogy(
        cp_lengths,
        np.maximum(ber_16qam, 1e-6),
        "s-",
        label="16-QAM",
        color="C1",
        markersize=7,
    )
    ax2.axvline(
        x=delay_spread,
        color="gray",
        linestyle="--",
        alpha=0.8,
        label=f"Delay spread = {delay_spread}",
    )
    ax2.set_xlabel("CP length (samples)")
    ax2.set_ylabel("Bit Error Rate (BER)")
    ax2.set_title(f"BER vs CP length — Multipath (ZF), SNR = {args.snr} dB")
    ax2.legend(loc="best")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    evm_ber_path = out_dir / "evm_ber_vs_cp_length.png"
    fig.savefig(evm_ber_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {evm_ber_path}")

    # Single strong plot for LinkedIn: EVM vs CP (most visual)
    fig2, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(cp_lengths, evm_qpsk, "o-", label="QPSK", color="C0", markersize=8)
    ax.plot(cp_lengths, evm_16qam, "s-", label="16-QAM", color="C1", markersize=8)
    ax.axvline(
        x=delay_spread,
        color="gray",
        linestyle="--",
        alpha=0.8,
        label=f"Delay spread = {delay_spread}",
    )
    ax.set_xlabel("CP length (samples)")
    ax.set_ylabel("EVM (%)")
    ax.set_title(
        f"EVM vs CP length — OFDM multipath, ZF equalizer, SNR = {args.snr} dB\n"
        "Short CP → ISI → degradation"
    )
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    fig2.tight_layout()
    evm_only_path = out_dir / "evm_vs_cp_length_linkedin.png"
    fig2.savefig(evm_only_path, dpi=300)
    plt.close(fig2)
    print(f"Saved (LinkedIn): {evm_only_path}")

    # CSV for reproducibility
    csv_path = out_dir / "evm_ber_vs_cp.csv"
    with open(csv_path, "w") as f:
        f.write("cp_len,EVM_QPSK_pct,EVM_16QAM_pct,BER_QPSK,BER_16QAM\n")
        for i, cp in enumerate(cp_lengths):
            f.write(
                f"{cp},{evm_qpsk[i]:.4f},{evm_16qam[i]:.4f},"
                f"{ber_qpsk[i]:.6e},{ber_16qam[i]:.6e}\n"
            )
    print(f"Saved: {csv_path}")
    print("Done.")


if __name__ == "__main__":
    main()
