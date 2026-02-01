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
from src.channel import awgn_channel, multipath_channel
from src.theory import theoretical_ber
from src.equalizers import equalize_zf, equalize_mmse

CONFIG = SimulationConfig()


def _apply_channel(stream: np.ndarray, config: SimulationConfig, snr_db: float) -> np.ndarray:
    if config.channel_type.lower() == "multipath" and config.multipath_taps is not None:
        return multipath_channel(stream, config.multipath_taps, snr_db, config.cp_len)
    return awgn_channel(stream, snr_db)


def _after_channel_no_cp(stream: np.ndarray, config: SimulationConfig) -> np.ndarray:
    """Return time-domain symbols without CP for FFT. Multipath channel already returns no CP."""
    if config.channel_type.lower() == "multipath":
        return stream
    return remove_cyclic_prefix(stream, config.cp_len)


def _multipath_freq_response(config: SimulationConfig) -> np.ndarray:
    """Channel frequency response H_k (length = fft_size)."""
    if config.channel_type.lower() != "multipath" or config.multipath_taps is None:
        return np.ones(config.fft_size, dtype=complex)
    taps = np.asarray(config.multipath_taps, dtype=complex)
    h_pad = np.zeros(config.fft_size, dtype=complex)
    h_pad[: len(taps)] = taps
    return np.fft.fft(h_pad)


def _equalize(freq_symbols: np.ndarray, config: SimulationConfig, snr_db: float) -> np.ndarray:
    """Apply ZF or MMSE equalization when channel is multipath; no-op otherwise."""
    if config.channel_type.lower() != "multipath" or config.multipath_taps is None:
        return freq_symbols
    eq = (getattr(config, "equalize", None) or "zf").lower()
    if eq == "none":
        return freq_symbols
    H = _multipath_freq_response(config)
    if eq == "mmse":
        snr_linear = 10.0 ** (snr_db / 10.0)
        return equalize_mmse(freq_symbols, H, snr_linear)
    return equalize_zf(freq_symbols, H)


def get_equalized_freq_symbols(
    config: SimulationConfig,
    modulation: str,
    snr_db: float,
    num_symbols: int = 1,
) -> np.ndarray:
    """Return equalized frequency-domain symbols for constellation plotting.
    Used by plot_constellation_comparison to compare AWGN vs multipath (no eq, ZF, MMSE)."""
    bits_per_sub = 2 if modulation.upper() == "QPSK" else 4
    total_bits = num_symbols * config.fft_size * bits_per_sub
    bits_tx = generate_random_bits(total_bits)
    ofdm_stream = generate_ofdm_stream(
        bits_tx, config.fft_size, config.cp_len, modulation
    )
    return get_freq_symbols_from_stream(ofdm_stream, config, snr_db)


def get_freq_symbols_from_stream(
    ofdm_stream: np.ndarray,
    config: SimulationConfig,
    snr_db: float,
) -> np.ndarray:
    """Return equalized frequency-domain symbols from a given OFDM stream (with CP).
    Same stream can be passed to different configs (AWGN, multipath none/zf/mmse) for fair comparison."""
    noisy = _apply_channel(ofdm_stream, config, float(snr_db))
    ofdm_no_cp = _after_channel_no_cp(noisy, config)
    freq = fft_ofdm(ofdm_no_cp)
    return _equalize(freq, config, float(snr_db))


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
            noisy_stream = _apply_channel(ofdm_stream, config, float(snr_db))
            ofdm_no_cp = _after_channel_no_cp(noisy_stream, config)
            freq_symbols = fft_ofdm(ofdm_no_cp)
            freq_symbols = _equalize(freq_symbols, config, float(snr_db))
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
    is_multipath = config.channel_type.lower() == "multipath"
    eq = (getattr(config, "equalize", None) or "zf").lower() if is_multipath else ""
    if is_multipath and eq == "none":
        channel_label = "Multipath (no eq)"
    elif is_multipath and eq:
        channel_label = f"Multipath ({eq})"
    elif is_multipath:
        channel_label = "Multipath"
    else:
        channel_label = "AWGN"
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
    if not is_multipath:
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
    if not is_multipath:
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
        f"BER vs SNR — OFDM {channel_label}\n"
        f"Symbols={config.num_symbols}, Trials={config.monte_carlo_trials}, "
        f"FFT={config.fft_size}, CP={config.cp_len}"
    )
    ax.legend(loc="upper right")
    ax.grid(True, which="both", alpha=0.3)
    ax.set_ylim(1e-5, 1)
    suffix = "_multipath" if is_multipath else ""
    out_path = config.images_dir / f"ber_vs_snr_{config.num_symbols}symbols{suffix}.png"
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
        noisy = _apply_channel(ofdm_symbol, config, float(snr))
        base_no_cp = _after_channel_no_cp(noisy, config)
        freq_syms = fft_ofdm(base_no_cp)
        freq_syms = _equalize(freq_syms, config, float(snr))

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

    is_mp = config.channel_type.lower() == "multipath"
    eq = (getattr(config, "equalize", None) or "zf").lower() if is_mp else ""
    if is_mp and eq == "none":
        channel_label = "Multipath (no eq)"
    elif is_mp and eq:
        channel_label = f"Multipath ({eq})"
    elif is_mp:
        channel_label = "Multipath"
    else:
        channel_label = "AWGN"
    plt.suptitle(
        f"{modulation} Constellation ({channel_label}) — {config.num_symbols} symbols, "
        f"FFT={config.fft_size}, CP={config.cp_len}"
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    suffix = "_multipath" if config.channel_type.lower() == "multipath" else ""
    out_path = config.images_dir / f"constellation_{modulation}_{config.num_symbols}symbols{suffix}.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved: {out_path}")


def plot_channel_response(config: SimulationConfig) -> None:
    """Plot CIR (impulse response) and CFR (frequency response) for multipath.
    Uses same normalized taps as the channel so CIR/CFR match simulation."""
    if config.channel_type.lower() != "multipath" or config.multipath_taps is None:
        return
    taps = np.asarray(config.multipath_taps, dtype=complex)
    taps_norm = taps / np.sqrt(np.sum(np.abs(taps) ** 2))
    n_fft = config.fft_size
    h_pad = np.zeros(n_fft, dtype=complex)
    h_pad[: len(taps_norm)] = taps_norm
    H = np.fft.fft(h_pad)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6))
    ax1.stem(np.arange(len(taps_norm)), np.abs(taps_norm), basefmt=" ")
    ax1.set_xlabel("Tap index")
    ax1.set_ylabel("|h[n]| (normalized)")
    ax1.set_title("Channel impulse response (CIR)")
    ax1.grid(True, alpha=0.3)

    ax2.plot(np.arange(n_fft), np.abs(H), color="C0")
    ax2.set_xlabel("Subcarrier index k")
    ax2.set_ylabel("|H(k)|")
    ax2.set_title("Channel frequency response (CFR)")
    ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    out_path = config.images_dir / f"channel_response_{config.num_symbols}symbols_multipath.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def save_ber_csv(
    config: SimulationConfig,
    ber_qpsk: np.ndarray,
    ber_16qam: np.ndarray,
) -> None:
    snr_int = config.snr_range_db.astype(int)
    suffix = "_multipath" if config.channel_type.lower() == "multipath" else ""
    np.savetxt(
        config.run_dir / f"ber_vs_snr_{config.num_symbols}symbols{suffix}_qpsk.csv",
        np.column_stack((snr_int, ber_qpsk)),
        delimiter=",",
        header="SNR(dB),BER",
        comments="",
        fmt=["%d", "%.6e"],
    )
    np.savetxt(
        config.run_dir / f"ber_vs_snr_{config.num_symbols}symbols{suffix}_16qam.csv",
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

    ch_label = cfg.channel_type.lower()
    eq_label = getattr(cfg, "equalize", "zf") or "zf"
    print(f"BER simulation: {cfg.num_symbols} symbols, {cfg.monte_carlo_trials} trials, channel={ch_label}, equalize={eq_label}")
    ber_qpsk = simulate_ber_monte_carlo("QPSK", cfg)
    ber_16qam = simulate_ber_monte_carlo("16QAM", cfg)

    plot_ber_vs_snr(cfg, ber_qpsk, ber_16qam)
    save_ber_csv(cfg, ber_qpsk, ber_16qam)

    if ch_label == "multipath":
        plot_channel_response(cfg)
    print("Constellation plots...")
    plot_constellations("QPSK", cfg, snr_list=(0, 10, 20))
    plot_constellations("16QAM", cfg, snr_list=(0, 10, 20))

    print("Done.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OFDM BER + constellation simulation")
    parser.add_argument("--symbols", type=int, default=5000, help="OFDM symbols")
    parser.add_argument("--trials", type=int, default=50, help="Monte Carlo trials per SNR")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--no-seed", action="store_true", help="No seed")
    parser.add_argument("--channel", type=str, default="awgn", choices=("awgn", "multipath"), help="Channel type")
    parser.add_argument("--equalize", type=str, default="zf", choices=("none", "zf", "mmse"), help="Equalizer for multipath: none, zf, or mmse")
    args = parser.parse_args()
    config = SimulationConfig(
        num_symbols=args.symbols,
        monte_carlo_trials=args.trials,
        random_seed=None if args.no_seed else args.seed,
        channel_type=args.channel,
        equalize=args.equalize,
    )
    main(config)
