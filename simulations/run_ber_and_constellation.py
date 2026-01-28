import numpy as np
import matplotlib.pyplot as plt

from src.transmitter import (
    generate_random_bits,
    generate_ofdm_stream
)
from src.receiver import (
    remove_cyclic_prefix, fft_ofdm,
    demodulate_ofdm_symbols, compute_ber
)
from src.channel import awgn_channel

# ----------------------------------
# Simulation parameters
# ----------------------------------
FFT_SIZE = 64
CP_LEN = 16
NUM_SYMBOLS = 5000           # number of OFDM symbols per run
MONTE_CARLO_TRIALS = 50     # how many random runs per SNR point

# SNR range for BER curves
SNR_RANGE = np.arange(0, 21, 2)  # e.g. 0–20 dB

# ----------------------------------
# BER Simulation (with Monte Carlo)
# ----------------------------------
def simulate_ber_monte_carlo(modulation: str) -> np.ndarray:
    """
    Simulate BER vs. SNR for a given modulation type using Monte Carlo.
    """
    ber_out_avg = []
    bits_per_sub = 2 if modulation == "QPSK" else 4

    for snr in SNR_RANGE:
        ber_trials = []
        for trial in range(MONTE_CARLO_TRIALS):
            # random bits
            total_bits = NUM_SYMBOLS * FFT_SIZE * bits_per_sub
            bits_tx = generate_random_bits(total_bits)

            # TX
            ofdm_stream = generate_ofdm_stream(
                bits_tx, FFT_SIZE, CP_LEN, modulation=modulation
            )

            # Channel: AWGN
            noisy_stream = awgn_channel(ofdm_stream, snr)

            # RX
            ofdm_no_cp = remove_cyclic_prefix(noisy_stream, CP_LEN)
            freq_symbols = fft_ofdm(ofdm_no_cp)
            bits_rx = demodulate_ofdm_symbols(freq_symbols, modulation)

            # compute BER
            ber_value = compute_ber(bits_tx, bits_rx)
            ber_trials.append(ber_value)

        # average BER over Monte Carlo trials
        avg_ber = np.mean(ber_trials)
        print(f"{modulation} @ {snr} dB → avg BER = {avg_ber:.4e}")
        ber_out_avg.append(avg_ber)

    return np.array(ber_out_avg)


# ----------------------------------
# Constellation Plot Function
# ----------------------------------
def plot_constellations(modulation: str, snr_list=(0, 10, 20)):
    """
    Plot constellation diagrams for selected SNR levels.
    """
    plt.figure(figsize=(len(snr_list) * 4, 4))
    
    bits_per_sub = 2 if modulation == "QPSK" else 4
    total_bits = FFT_SIZE * bits_per_sub

    for idx, snr in enumerate(snr_list):
        bits_tx = generate_random_bits(total_bits)
        ofdm_symbol = generate_ofdm_stream(
            bits_tx, FFT_SIZE, CP_LEN, modulation
        )

        noisy = awgn_channel(ofdm_symbol, snr)
        base_no_cp = remove_cyclic_prefix(noisy, CP_LEN)
        freq_syms = fft_ofdm(base_no_cp)

        plt.subplot(1, len(snr_list), idx + 1)
        plt.scatter(freq_syms.real.flatten(),
                    freq_syms.imag.flatten(),
                    s=2, alpha=0.5)
        plt.title(f"{modulation} @ {snr} dB")
        plt.xlabel("Real")
        plt.ylabel("Imag")
        plt.grid(True)

    plt.tight_layout()
    plt.show()


# ----------------------------------
# Main Execution
# ----------------------------------
def main():
    # Run BER for both modulations with Monte Carlo
    ber_qpsk = simulate_ber_monte_carlo("QPSK")
    ber_16qam = simulate_ber_monte_carlo("16QAM")

    # Plot BER vs SNR curve
    plt.figure()
    plt.semilogy(SNR_RANGE, ber_qpsk, 'o-', label="QPSK")
    plt.semilogy(SNR_RANGE, ber_16qam, 's-', label="16‑QAM")
    plt.title("BER vs SNR for OFDM (AWGN Channel) — Monte Carlo")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.grid(True, which='both')
    plt.legend()
    plt.show()

    # Constellations at selected SNRs
    plot_constellations("QPSK", snr_list=(0, 10, 20))
    plot_constellations("16QAM", snr_list=(0, 10, 20))


if __name__ == "__main__":
    main()
