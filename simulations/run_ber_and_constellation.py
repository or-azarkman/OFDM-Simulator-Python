import numpy as np
import matplotlib.pyplot as plt
import os

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
NUM_SYMBOLS = 5000 
MONTE_CARLO_TRIALS = 50  

# SNR range for BER curves
SNR_RANGE = np.arange(0, 21, 2)  # 0–20 dB

# Ensure results directories exist
os.makedirs("results", exist_ok=True)
os.makedirs("results/images", exist_ok=True)

# ----------------------------------
# BER Simulation (with Monte Carlo)
# ----------------------------------
def simulate_ber_monte_carlo(modulation: str) -> np.ndarray:
    ber_out_avg = []
    bits_per_sub = 2 if modulation == "QPSK" else 4

    for snr in SNR_RANGE:
        ber_trials = []
        for _ in range(MONTE_CARLO_TRIALS):
            total_bits = NUM_SYMBOLS * FFT_SIZE * bits_per_sub
            bits_tx = generate_random_bits(total_bits)

            ofdm_stream = generate_ofdm_stream(bits_tx, FFT_SIZE, CP_LEN, modulation)
            noisy_stream = awgn_channel(ofdm_stream, snr)
            ofdm_no_cp = remove_cyclic_prefix(noisy_stream, CP_LEN)
            freq_symbols = fft_ofdm(ofdm_no_cp)
            bits_rx = demodulate_ofdm_symbols(freq_symbols, modulation)

            ber_value = compute_ber(bits_tx, bits_rx)
            ber_trials.append(ber_value)

        avg_ber = np.mean(ber_trials)
        print(f"{modulation} @ {snr} dB → avg BER = {avg_ber:.6e}")
        ber_out_avg.append(avg_ber)

    return np.array(ber_out_avg)

# ----------------------------------
# Constellation Plot Function
# ----------------------------------
def plot_constellations(modulation: str, snr_list=(0, 10, 20)):
    plt.figure(figsize=(len(snr_list) * 4, 4))
    
    bits_per_sub = 2 if modulation == "QPSK" else 4
    total_bits = FFT_SIZE * bits_per_sub

    for idx, snr in enumerate(snr_list):
        bits_tx = generate_random_bits(total_bits)
        ofdm_symbol = generate_ofdm_stream(bits_tx, FFT_SIZE, CP_LEN, modulation)
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

    plt.suptitle(f"{modulation} Constellation\n{NUM_SYMBOLS} OFDM symbols, FFT={FFT_SIZE}, CP={CP_LEN}")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(f"results/images/constellation_{modulation}_{NUM_SYMBOLS}symbols.png", dpi=300)
    plt.show()
    plt.close()

# ----------------------------------
# Main Execution
# ----------------------------------
def main():
    # Run BER for both modulations with Monte Carlo
    ber_qpsk = simulate_ber_monte_carlo("QPSK")
    ber_16qam = simulate_ber_monte_carlo("16QAM")

    # ---------------------------
    # Plot BER vs SNR
    # ---------------------------
    plt.figure()
    plt.semilogy(SNR_RANGE, ber_qpsk, 'o-', label="QPSK")
    plt.semilogy(SNR_RANGE, ber_16qam, 's-', label="16‑QAM")
    plt.title(f"BER vs SNR for OFDM (AWGN Channel)\n{NUM_SYMBOLS} symbols, {MONTE_CARLO_TRIALS} trials, FFT={FFT_SIZE}, CP={CP_LEN}")
    plt.xlabel("SNR (dB)")
    plt.ylabel("Bit Error Rate (BER)")
    plt.grid(True, which='both')
    plt.legend()
    plt.savefig(f"results/images/ber_vs_snr_{NUM_SYMBOLS}symbols.png", dpi=300)
    plt.show()
    plt.close()

    # ---------------------------
    # Constellations at selected SNRs
    # ---------------------------
    plot_constellations("QPSK", snr_list=(0, 10, 20))
    plot_constellations("16QAM", snr_list=(0, 10, 20))

    # ---------------------------
    # Save BER results to CSV with SNR as integer
    # ---------------------------
    snr_ber_qpsk = np.column_stack((SNR_RANGE.astype(int), ber_qpsk))
    snr_ber_16qam = np.column_stack((SNR_RANGE.astype(int), ber_16qam))
    
    np.savetxt(f"results/ber_vs_snr_{NUM_SYMBOLS}symbols_qpsk.csv",
               snr_ber_qpsk,
               delimiter=",",
               header="SNR(dB),BER",
               comments="",
               fmt=['%d', '%.6e'])
    np.savetxt(f"results/ber_vs_snr_{NUM_SYMBOLS}symbols_16qam.csv",
               snr_ber_16qam,
               delimiter=",",
               header="SNR(dB),BER",
               comments="",
               fmt=['%d', '%.6e'])

if __name__ == "__main__":
    main()
