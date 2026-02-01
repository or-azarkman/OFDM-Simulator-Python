"""
run_ber_and_constellation.py

OFDM BER simulation and constellation visualization.

- Monte Carlo BER vs SNR for QPSK and 16-QAM
- Theoretical BER curves for validation
- Constellation diagrams at selected SNRs
- Reproducible runs via config and random seed
"""

from pathlib import Path
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt

from simulations.config import SimulationConfig
from src.transmitter import generate_random_bits, generate_ofdm_stream
from src.receiver import (
    remove_cyclic_prefix,
    fft_ofdm,
    demodulate_ofdm_symbols,
    compute_ber,
)
from src.channel import awgn_channel
from src.theory import theoretical_ber

# Default config (override by passing config to main())
CONFIG = SimulationConfig()


def simulate_ber_monte_carlo(
    modulation: str,
    config: SimulationConfig,
) -> np.ndarray:
    """
    Run Monte Carlo BER simulation for a given modulation.

    Args:
        modulation: "QPSK" or "16QAM"
        config: Simulation parameters (FFT size, CP, symbols, trials, SNR range).

    Returns:
        Average BER at each SNR point.
    """
    bits_per_sub = 2 if modulation.upper() == "QPSK" else 4
    ber_avg = []

    for snr_db in config.snr_range_db:
        ber_trials = []
        for _ in range(config.monte_carlo_trials):
            total_bits = config.num_symbols * config.fft_size * bits_per_sub
            bits_tx = generate_random_bits(total_bits)

            ofdm_stream = generate_ofdm_stream(
                bits_tx, config.fft_size, config.cp_len, modulation
            )
            noisy_stream = awgn_channel(ofdm_stream, float(snr_db))
            ofdm_no_cp = remove_cyclic_prefix(noisy_stream, config.cp_len)
            freq_symbols = fft_ofdm(ofdm_no_cp)
            bits_rx = demodulate_ofdm_symbols(freq_symbols, modulation)

            ber_trials.append(compute_ber(bits_tx, bits_rx))

        avg_ber = np.mean(ber_trials)
        print(f"  {modulation} @ {snr_db} dB → avg BER = {avg_ber:.6e}")
        ber_avg.append(avg_ber)

    return np.array(ber_avg)


def plot_ber_vs_snr(
    config: SimulationConfig,
    ber_qpsk: np.ndarray,
    ber_16qam: np.ndarray,
) -> None:
    """
    Plot simulated and theoretical BER vs SNR; save to config run directory.
    """
    theory_qpsk = theoretical_ber(config.snr_range_db, "QPSK")
    theory_16qam = theoretical_ber(config.snr_range_db, "16QAM")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(
        config.snr_range_db,
        ber_qpsk,
        "o-",
        label="QPSK (simulated)",
        color="C0",
        markersize=6,
    )
    ax.semilogy(
        config.snr_range_db,
        theory_qpsk,
        "--",
        label="QPSK (theoretical)",
        color="C0",
        alpha=0.8,
    )
    ax.semilogy(
        config.snr_range_db,
        ber_16qam,
        "s-",
        label="16-QAM (simulated)",
        color="C1",
        markersize=6,
    )
    ax.semilogy(
        config.snr_range_db,
        theory_16qam,
        "--",
        label="16-QAM (theoretical)",
        color="C1",
        alpha=0.8,
    )
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Bit Error Rate (BER)")
    ax.set_title(
        f"BER vs SNR — OFDM AWGN\n"
        f"Symbols={config.num_symbols}, Trials={config.monte_carlo_trials}, "
        f"FFT={config.fft_size}, CP={config.cp_len}"
    )
    ax.legend(loc="upper right")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-5, 1)
    fig.tight_layout()
    out_path = config.images_dir / f"ber_vs_snr_{config.num_symbols}symbols.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}\n")


def plot_constellations(
    modulation: str,
    config: SimulationConfig,
    snr_list: tuple[int, ...] = (0, 10, 20),
) -> None:
    """Plot constellation at selected SNRs; save to config run directory."""
    plt.figure(figsize=(len(snr_list) * 4, 4))
    bits_per_sub = 2 if modulation.upper() == "QPSK" else 4
    total_bits = config.fft_size * bits_per_sub

    for idx, snr in enumerate(snr_list):
        bits_tx = generate_random_bits(total_bits)
        ofdm_symbol = generate_ofdm_stream(
            bits_tx, config.fft_size, config.cp_len, modulation
        )
        noisy = awgn_channel(ofdm_symbol, float(snr))
        base_no_cp = remove_cyclic_prefix(noisy, config.cp_len)
        freq_syms = fft_ofdm(base_no_cp)

        plt.subplot(1, len(snr_list), idx + 1)
        plt.scatter(
            freq_syms.real.flatten(),
            freq_syms.imag.flatten(),
            s=2,
            alpha=0.5,
        )
        plt.title(f"{modulation} @ {snr} dB")
        plt.xlabel("Real")
        plt.ylabel("Imag")
        plt.grid(True)
        plt.axis("equal")

    plt.suptitle(
        f"{modulation} Constellation — {config.num_symbols} symbols, "
        f"FFT={config.fft_size}, CP={config.cp_len}"
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = config.images_dir / f"constellation_{modulation}_{config.num_symbols}symbols.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def save_ber_csv(
    config: SimulationConfig,
    ber_qpsk: np.ndarray,
    ber_16qam: np.ndarray,
) -> None:
    """Save BER vs SNR to CSV in run directory."""
    snr_int = config.snr_range_db.astype(int)
    np.savetxt(
        config.run_dir / f"ber_vs_snr_{config.num_symbols}symbols_qpsk.csv",
        np.column_stack((snr_int, ber_qpsk)),
        delimiter=",",
        header="SNR(dB),BER",
        comments="",
        fmt=["%d", "%.6e"],
    )
    np.savetxt(
        config.run_dir / f"ber_vs_snr_{config.num_symbols}symbols_16qam.csv",
        np.column_stack((snr_int, ber_16qam)),
        delimiter=",",
        header="SNR(dB),BER",
        comments="",
        fmt=["%d", "%.6e"],
    )
    print(f"Saved CSV files in {config.run_dir}")


def main(config: Optional[SimulationConfig] = None) -> None:
    """Run full BER + constellation pipeline with given or default config."""
    cfg = config or CONFIG
    cfg.ensure_dirs()

    if cfg.random_seed is not None:
        np.random.seed(cfg.random_seed)
        print(f"Random seed: {cfg.random_seed}")

    print(f"BER simulation: {cfg.num_symbols} symbols, {cfg.monte_carlo_trials} trials")
    ber_qpsk = simulate_ber_monte_carlo("QPSK", cfg)
    ber_16qam = simulate_ber_monte_carlo("16QAM", cfg)

    plot_ber_vs_snr(cfg, ber_qpsk, ber_16qam)
    save_ber_csv(cfg, ber_qpsk, ber_16qam)

    print("Constellation plots...")
    plot_constellations("QPSK", cfg, snr_list=(0, 10, 20))
    plot_constellations("16QAM", cfg, snr_list=(0, 10, 20))

    print("Done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OFDM BER + constellation simulation")
    parser.add_argument(
        "--symbols",
        type=int,
        default=5000,
        help="Number of OFDM symbols (default: 5000)",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=50,
        help="Monte Carlo trials per SNR (default: 50)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)",
    )
    parser.add_argument(
        "--no-seed",
        action="store_true",
        help="Disable random seed (non-reproducible)",
    )
    args = parser.parse_args()
    config = SimulationConfig(
        num_symbols=args.symbols,
        monte_carlo_trials=args.trials,
        random_seed=None if args.no_seed else args.seed,
    )
    main(config)
