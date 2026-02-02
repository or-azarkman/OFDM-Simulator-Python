"""
plot_pilots_comparison.py

Comparison plots for pilot-based channel estimation vs known channel.

- BER vs SNR: Known channel (ZF/MMSE) vs Pilot-based estimation (ZF/MMSE)
- EVM vs SNR: Known channel vs Pilot-based estimation
- Channel estimation accuracy: True H vs Estimated H (MSE, magnitude/phase error)
- Constellation comparison: With pilots vs without pilots

This demonstrates the impact of channel estimation errors on system performance.

Run from project root: py simulations/plot_pilots_comparison.py [--symbols 5000] [--equalize zf|mmse]

Output (results/summary/pilots/): channel_estimation_accuracy_*.png, ber_comparison_pilots_*.png, 
evm_comparison_pilots_*.png, constellation_pilots_comparison_*.png

Requires simulation runs with and without pilots:
  py run_simulation.py --channel multipath --equalize zf --symbols 5000
  py run_simulation.py --channel multipath --equalize zf --pilots --symbols 5000
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import argparse
from typing import Tuple

import numpy as np
import matplotlib.pyplot as plt

from simulations.config import SimulationConfig
from src.transmitter import generate_random_bits, generate_ofdm_stream
from src.receiver import remove_cyclic_prefix, fft_ofdm
from src.channel import multipath_channel
from src.equalizers import equalize_zf, equalize_mmse
from src.pilots import (
    generate_pilot_pattern,
    generate_pilot_symbols,
    extract_pilots,
    estimate_channel_ls,
    get_data_indices,
)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _multipath_freq_response(config: SimulationConfig) -> np.ndarray:
    """True channel frequency response H_k."""
    if config.channel_type.lower() != "multipath" or config.multipath_taps is None:
        return np.ones(config.fft_size, dtype=complex)
    taps = np.asarray(config.multipath_taps, dtype=complex)
    h_pad = np.zeros(config.fft_size, dtype=complex)
    h_pad[: len(taps)] = taps
    return np.fft.fft(h_pad)


def plot_channel_estimation_accuracy(
    config: SimulationConfig,
    snr_db: float = 20.0,
    num_trials: int = 100,
) -> None:
    """
    Plot channel estimation accuracy: true H vs estimated H.
    
    Shows:
    - Magnitude comparison (|H_true| vs |H_est|)
    - Phase comparison (angle(H_true) vs angle(H_est))
    - MSE vs subcarrier index
    """
    pilot_indices = generate_pilot_pattern(config.fft_size, pilot_spacing=config.pilot_spacing)
    pilot_symbols = generate_pilot_symbols(len(pilot_indices))
    H_true = _multipath_freq_response(config)
    
    H_est_all = []
    for _ in range(num_trials):
        # Generate OFDM symbol with pilots
        bits_per_sub = 2  # QPSK
        num_data_subcarriers = config.fft_size - len(pilot_indices)
        bits = generate_random_bits(num_data_subcarriers * bits_per_sub)
        ofdm_stream = generate_ofdm_stream(
            bits, config.fft_size, config.cp_len, "QPSK",
            pilot_indices, pilot_symbols,
        )
        
        # Apply channel
        noisy = multipath_channel(ofdm_stream, config.multipath_taps, snr_db, config.cp_len)
        freq_rx = fft_ofdm(noisy)
        
        # Estimate channel
        rx_pilots = extract_pilots(freq_rx, pilot_indices)
        H_est = estimate_channel_ls(rx_pilots, pilot_symbols, pilot_indices, config.fft_size)
        H_est_all.append(H_est)
    
    H_est_avg = np.mean(H_est_all, axis=0)
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Magnitude comparison
    ax = axes[0, 0]
    subcarriers = np.arange(config.fft_size)
    ax.plot(subcarriers, np.abs(H_true), 'b-', label='True |H|', linewidth=2)
    ax.plot(subcarriers, np.abs(H_est_avg), 'r--', label='Estimated |H|', linewidth=2)
    ax.scatter(pilot_indices, np.abs(H_true[pilot_indices]), c='blue', s=50, marker='o', 
               label='Pilot positions', zorder=5)
    ax.set_xlabel('Subcarrier index')
    ax.set_ylabel('|H|')
    ax.set_title(f'Channel Magnitude: True vs Estimated (SNR={snr_db} dB)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Phase comparison
    ax = axes[0, 1]
    ax.plot(subcarriers, np.angle(H_true), 'b-', label='True ∠H', linewidth=2)
    ax.plot(subcarriers, np.angle(H_est_avg), 'r--', label='Estimated ∠H', linewidth=2)
    ax.scatter(pilot_indices, np.angle(H_true[pilot_indices]), c='blue', s=50, marker='o',
               label='Pilot positions', zorder=5)
    ax.set_xlabel('Subcarrier index')
    ax.set_ylabel('Phase (rad)')
    ax.set_title(f'Channel Phase: True vs Estimated (SNR={snr_db} dB)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # MSE per subcarrier
    ax = axes[1, 0]
    mse_per_sub = np.mean([np.abs(H_true - H_est) ** 2 for H_est in H_est_all], axis=0)
    ax.plot(subcarriers, mse_per_sub, 'g-', linewidth=2)
    ax.scatter(pilot_indices, mse_per_sub[pilot_indices], c='red', s=50, marker='o',
               label='Pilot positions', zorder=5)
    ax.set_xlabel('Subcarrier index')
    ax.set_ylabel('MSE |H_true - H_est|²')
    ax.set_title('Channel Estimation MSE per Subcarrier')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # Estimation error distribution
    ax = axes[1, 1]
    errors = [np.abs(H_true - H_est) for H_est in H_est_all]
    errors_flat = np.array(errors).flatten()
    ax.hist(errors_flat, bins=50, alpha=0.7, edgecolor='black')
    ax.set_xlabel('|H_true - H_est|')
    ax.set_ylabel('Frequency')
    ax.set_title('Channel Estimation Error Distribution')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    pilots_summary_dir = SimulationConfig.summary_pilots_dir()
    out_path = pilots_summary_dir / f"channel_estimation_accuracy_{config.num_symbols}symbols_snr{snr_db}dB.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_ber_comparison_pilots(
    config: SimulationConfig,
    equalizer: str = "zf",
) -> None:
    """Plot BER vs SNR: Known channel vs Pilot-based estimation."""
    from simulations.run_ber_and_constellation import simulate_ber_monte_carlo
    
    # Known channel
    config_no_pilots = SimulationConfig(
        fft_size=config.fft_size,
        cp_len=config.cp_len,
        num_symbols=config.num_symbols,
        monte_carlo_trials=config.monte_carlo_trials,
        snr_range_db=config.snr_range_db,
        random_seed=config.random_seed,
        channel_type=config.channel_type,
        equalize=equalizer,
        multipath_taps=config.multipath_taps,
        use_pilots=False,
    )
    config_no_pilots.ensure_dirs()
    
    # Pilot-based
    config_with_pilots = SimulationConfig(
        fft_size=config.fft_size,
        cp_len=config.cp_len,
        num_symbols=config.num_symbols,
        monte_carlo_trials=config.monte_carlo_trials,
        snr_range_db=config.snr_range_db,
        random_seed=config.random_seed,
        channel_type=config.channel_type,
        equalize=equalizer,
        multipath_taps=config.multipath_taps,
        use_pilots=True,
        pilot_spacing=getattr(config, "pilot_spacing", 8),
    )
    config_with_pilots.ensure_dirs()
    
    print("Simulating BER with known channel...")
    ber_qpsk_known = simulate_ber_monte_carlo("QPSK", config_no_pilots)
    ber_16qam_known = simulate_ber_monte_carlo("16QAM", config_no_pilots)
    
    print("Simulating BER with pilot-based estimation...")
    ber_qpsk_pilots = simulate_ber_monte_carlo("QPSK", config_with_pilots)
    ber_16qam_pilots = simulate_ber_monte_carlo("16QAM", config_with_pilots)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # QPSK
    ax1.semilogy(config.snr_range_db, ber_qpsk_known, 'o-', label='Known channel', 
                 color='C0', markersize=6, linewidth=2)
    ax1.semilogy(config.snr_range_db, ber_qpsk_pilots, 's--', label='Pilot-based estimation',
                 color='C1', markersize=6, linewidth=2)
    ax1.set_xlabel('SNR (dB)')
    ax1.set_ylabel('BER')
    ax1.set_title(f'BER vs SNR: QPSK ({equalizer.upper()} Equalizer)')
    ax1.legend()
    ax1.grid(True, which='both', alpha=0.3)
    ax1.set_ylim(1e-5, 1)
    
    # 16-QAM
    ax2.semilogy(config.snr_range_db, ber_16qam_known, 'o-', label='Known channel',
                 color='C0', markersize=6, linewidth=2)
    ax2.semilogy(config.snr_range_db, ber_16qam_pilots, 's--', label='Pilot-based estimation',
                 color='C1', markersize=6, linewidth=2)
    ax2.set_xlabel('SNR (dB)')
    ax2.set_ylabel('BER')
    ax2.set_title(f'BER vs SNR: 16-QAM ({equalizer.upper()} Equalizer)')
    ax2.legend()
    ax2.grid(True, which='both', alpha=0.3)
    ax2.set_ylim(1e-5, 1)
    
    plt.tight_layout()
    pilots_summary_dir = SimulationConfig.summary_pilots_dir()
    out_path = pilots_summary_dir / f"ber_comparison_pilots_{config.num_symbols}symbols_{equalizer}.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_evm_comparison_pilots(
    config: SimulationConfig,
    equalizer: str = "zf",
) -> None:
    """Plot EVM vs SNR: Known channel vs Pilot-based estimation."""
    from simulations.run_ber_and_constellation import simulate_evm
    
    config_no_pilots = SimulationConfig(
        fft_size=config.fft_size,
        cp_len=config.cp_len,
        num_symbols=config.num_symbols,
        monte_carlo_trials=config.monte_carlo_trials,
        snr_range_db=config.snr_range_db,
        random_seed=config.random_seed,
        channel_type=config.channel_type,
        equalize=equalizer,
        multipath_taps=config.multipath_taps,
        use_pilots=False,
    )
    config_no_pilots.ensure_dirs()
    
    config_with_pilots = SimulationConfig(
        fft_size=config.fft_size,
        cp_len=config.cp_len,
        num_symbols=config.num_symbols,
        monte_carlo_trials=config.monte_carlo_trials,
        snr_range_db=config.snr_range_db,
        random_seed=config.random_seed,
        channel_type=config.channel_type,
        equalize=equalizer,
        multipath_taps=config.multipath_taps,
        use_pilots=True,
        pilot_spacing=getattr(config, "pilot_spacing", 8),
    )
    config_with_pilots.ensure_dirs()
    
    print("Simulating EVM with known channel...")
    evm_qpsk_known = simulate_evm("QPSK", config_no_pilots)
    evm_16qam_known = simulate_evm("16QAM", config_no_pilots)
    
    print("Simulating EVM with pilot-based estimation...")
    evm_qpsk_pilots = simulate_evm("QPSK", config_with_pilots)
    evm_16qam_pilots = simulate_evm("16QAM", config_with_pilots)
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # QPSK
    ax1.plot(config.snr_range_db, evm_qpsk_known, 'o-', label='Known channel',
             color='C0', markersize=6, linewidth=2)
    ax1.plot(config.snr_range_db, evm_qpsk_pilots, 's--', label='Pilot-based estimation',
             color='C1', markersize=6, linewidth=2)
    ax1.set_xlabel('SNR (dB)')
    ax1.set_ylabel('EVM (%)')
    ax1.set_title(f'EVM vs SNR: QPSK ({equalizer.upper()} Equalizer)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 16-QAM
    ax2.plot(config.snr_range_db, evm_16qam_known, 'o-', label='Known channel',
             color='C0', markersize=6, linewidth=2)
    ax2.plot(config.snr_range_db, evm_16qam_pilots, 's--', label='Pilot-based estimation',
             color='C1', markersize=6, linewidth=2)
    ax2.set_xlabel('SNR (dB)')
    ax2.set_ylabel('EVM (%)')
    ax2.set_title(f'EVM vs SNR: 16-QAM ({equalizer.upper()} Equalizer)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    pilots_summary_dir = SimulationConfig.summary_pilots_dir()
    out_path = pilots_summary_dir / f"evm_comparison_pilots_{config.num_symbols}symbols_{equalizer}.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_constellation_comparison_pilots(
    config: SimulationConfig,
    snr_db: float = 20.0,
    equalizer: str = "zf",
) -> None:
    """Plot constellation: Known channel vs Pilot-based estimation."""
    pilot_indices = generate_pilot_pattern(config.fft_size, pilot_spacing=getattr(config, "pilot_spacing", 8))
    pilot_symbols = generate_pilot_symbols(len(pilot_indices))
    H_true = _multipath_freq_response(config)
    
    bits_per_sub = 2  # QPSK
    num_data_subcarriers = config.fft_size - len(pilot_indices)
    bits = generate_random_bits(num_data_subcarriers * bits_per_sub)
    
    ofdm_stream = generate_ofdm_stream(
        bits, config.fft_size, config.cp_len, "QPSK",
        pilot_indices, pilot_symbols,
    )
    
    noisy = multipath_channel(ofdm_stream, config.multipath_taps, snr_db, config.cp_len)
    freq_rx = fft_ofdm(noisy)
    
    # Known channel
    if equalizer.lower() == "mmse":
        snr_linear = 10.0 ** (snr_db / 10.0)
        freq_eq_known = equalize_mmse(freq_rx, H_true, snr_linear)
    else:
        freq_eq_known = equalize_zf(freq_rx, H_true)
    
    # Pilot-based
    rx_pilots = extract_pilots(freq_rx, pilot_indices)
    H_est = estimate_channel_ls(rx_pilots, pilot_symbols, pilot_indices, config.fft_size)
    if equalizer.lower() == "mmse":
        snr_linear = 10.0 ** (snr_db / 10.0)
        freq_eq_pilots = equalize_mmse(freq_rx, H_est, snr_linear)
    else:
        freq_eq_pilots = equalize_zf(freq_rx, H_est)
    
    # Extract data subcarriers
    data_indices = get_data_indices(config.fft_size, pilot_indices)
    syms_known = freq_eq_known[:, data_indices].flatten()
    syms_pilots = freq_eq_pilots[:, data_indices].flatten()
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    ax1.scatter(syms_known.real, syms_known.imag, s=2, alpha=0.5, c='blue')
    ax1.set_title(f'Known Channel ({equalizer.upper()}, SNR={snr_db} dB)')
    ax1.set_xlabel('Real')
    ax1.set_ylabel('Imag')
    ax1.grid(True, alpha=0.3)
    ax1.axis('equal')
    
    ax2.scatter(syms_pilots.real, syms_pilots.imag, s=2, alpha=0.5, c='red')
    ax2.set_title(f'Pilot-Based Estimation ({equalizer.upper()}, SNR={snr_db} dB)')
    ax2.set_xlabel('Real')
    ax2.set_ylabel('Imag')
    ax2.grid(True, alpha=0.3)
    ax2.axis('equal')
    
    plt.suptitle('QPSK Constellation: Known Channel vs Pilot-Based Estimation', fontsize=14)
    plt.tight_layout()
    pilots_summary_dir = SimulationConfig.summary_pilots_dir()
    out_path = pilots_summary_dir / f"constellation_pilots_comparison_{config.num_symbols}symbols_{equalizer}_snr{snr_db}dB.png"
    plt.savefig(out_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Pilot-based channel estimation comparison")
    parser.add_argument("--symbols", type=int, default=5000, help="OFDM symbols")
    parser.add_argument("--trials", type=int, default=50, help="Monte Carlo trials")
    parser.add_argument("--equalize", type=str, default="zf", choices=("zf", "mmse"), help="Equalizer")
    parser.add_argument("--snr", type=float, default=20.0, help="SNR for channel estimation accuracy plot")
    args = parser.parse_args()
    
    config = SimulationConfig(
        num_symbols=args.symbols,
        monte_carlo_trials=args.trials,
        channel_type="multipath",
        equalize=args.equalize,
        use_pilots=True,  # For output directory
    )
    config.ensure_dirs()
    
    print("=" * 60)
    print("Pilot-Based Channel Estimation Comparison")
    print("=" * 60)
    
    print("\n1. Channel Estimation Accuracy...")
    plot_channel_estimation_accuracy(config, snr_db=args.snr)
    
    print("\n2. BER Comparison (Known vs Pilot-based)...")
    plot_ber_comparison_pilots(config, equalizer=args.equalize)
    
    print("\n3. EVM Comparison (Known vs Pilot-based)...")
    plot_evm_comparison_pilots(config, equalizer=args.equalize)
    
    print("\n4. Constellation Comparison...")
    plot_constellation_comparison_pilots(config, snr_db=args.snr, equalizer=args.equalize)
    
    print("\nDone! Plots saved to:", SimulationConfig.summary_pilots_dir())


if __name__ == "__main__":
    main()
