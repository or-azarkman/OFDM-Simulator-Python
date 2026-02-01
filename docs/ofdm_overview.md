# OFDM System Overview

## Overview

Orthogonal Frequency Division Multiplexing (**OFDM**) is a multi-carrier modulation technique widely used in modern wireless communication systems such as **Wi-Fi, LTE, and 5G**. In OFDM, a high-rate serial bitstream is divided into multiple parallel low-rate streams, each transmitted over an orthogonal subcarrier. This approach improves spectral efficiency and robustness to channel impairments.

All signals in this project are modeled at the **complex baseband level**, focusing on **PHY-layer digital signal processing** rather than RF front-end implementation.

This document provides a comprehensive overview of the OFDM system, including **system architecture, signal model, modulation, receiver processing, simulation parameters, and key outputs**.

---

## System Block Diagram

![OFDM Block Diagram](images/ofdm_block_diagram.png)

**Block color coding:**
- **Blue** — Transmitter (TX)
- **Gray** — Channel (AWGN)
- **Green** — Receiver (RX)

---

## Mathematical Foundations

### OFDM Time-Domain Symbol Generation

Each OFDM symbol is generated using an **Inverse Fast Fourier Transform (IFFT)**:

$$
x[n] = \frac{1}{N} \sum_{k=0}^{N-1} X_k \cdot e^{j 2 \pi k n / N}, \quad n = 0,1,\dots,N-1
$$

Where:  
- $X_k$ = modulated symbol on subcarrier $k$ (QPSK or 16-QAM)  
- $N$ = FFT size

**Explanation:** The IFFT converts frequency-domain symbols into a time-domain waveform while preserving subcarrier orthogonality. The receiver uses FFT to recover the symbols.

---

### Cyclic Prefix (CP)

To prevent inter-symbol interference (ISI), a cyclic prefix of length $N_{CP}$ is prepended to each OFDM symbol:

$$
x_{\text{CP}}[n] = x[N - N_{CP} + n], \quad n = 0,1,\dots,N_{CP}-1
$$

$$
x_{\text{tx}}[n] = [x_{\text{CP}}[0], \dots, x_{\text{CP}}[N_{CP}-1], x[0], \dots, x[N-1]]
$$

**Explanation:** The CP converts linear convolution with the channel into circular convolution, preserving subcarrier orthogonality and simplifying frequency-domain equalization.

---

## Modulation Schemes

### QPSK

Quadrature Phase Shift Keying maps 2 bits per symbol into a complex constellation point:

$$
s = \frac{1}{\sqrt{2}} \Big( (2b_0 - 1) + j(2b_1 - 1) \Big)
$$

- Unit average symbol energy  
- Gray coding is used to minimize bit errors

### 16-QAM

16-Quadrature Amplitude Modulation maps 4 bits per symbol:

$$
s = \frac{1}{\sqrt{10}} \Big( (2b_0 + b_1 - 1.5) + j(2b_2 + b_3 - 1.5) \Big)
$$

- Gray coding used to minimize bit errors  
- Average symbol power normalized to match QPSK

---

## Receiver Processing

1. **Cyclic Prefix Removal** – remove the CP from each OFDM symbol (for AWGN); for multipath the channel output is already the useful part without CP.  
2. **FFT** – recover frequency-domain subcarrier symbols \(Y_k\).  
3. **Equalization (multipath only)** – one-tap ZF (\(\hat{X}_k = Y_k / H_k\)) or MMSE (\(W_k = H^*_k / (|H_k|^2 + 1/\mathrm{SNR})\)).  
4. **Demodulation** – according to the selected modulation (QPSK / 16-QAM).  
5. **BER Calculation** – compare received bits with transmitted bits.

---

## Channel Models

**AWGN:** Additive White Gaussian Noise; noise power set from SNR (Es/N0). Used as baseline.

**Multipath (frequency-selective):** FIR impulse response \(h[n]\) (taps) plus AWGN. Per OFDM symbol we apply **circular convolution** of the useful part (after CP) with the taps, then AWGN; in frequency domain \(Y_k = H_k X_k + N_k\). The receiver can use **no equalization** (for baseline comparison), **one-tap ZF** (\(Y_k / H_k\)), or **one-tap MMSE** (\(W_k = H^*_k / (|H_k|^2 + 1/\mathrm{SNR})\)). Taps normalized to unit energy; default taps: \([1, 0, 0.4 e^{j0.5}]\). Outputs: CIR and CFR plots.

---

## Simulation Parameters

|       Parameter         |     Value       |              Notes                      |
|-------------------------|-----------------|-----------------------------------------|
| FFT size                | 64              | Number of subcarriers                   |
| Cyclic Prefix length    | 16              | 25% of FFT size                         |
| Modulation schemes      | QPSK / 16-QAM   | Gray-coded                              |
| OFDM symbols per run    | 500 / 5000      | Performance comparison                  |
| Monte-Carlo trials      | 50              | BER averaging                           |
| SNR range               | 0–20 dB         | Step of 2 dB                            |
| Channel                 | AWGN / multipath| Selectable via config or `--channel`    |

---

## Simulation Scope

### Included
- Random bitstream generation; QPSK and 16-QAM (Gray); OFDM IFFT/FFT; cyclic prefix
- AWGN and multipath (circular convolution + AWGN); multipath with **no equalizer**, **ZF**, or **MMSE** (`--equalize none|zf|mmse`)
- BER computation; constellation and BER vs SNR plots; CIR and CFR plots for multipath
- Theoretical BER curves (AWGN); CSV results per run
- **Comparison outputs:** table (BER by scenario per SNR), BER comparison plots, constellation comparison grid (4×3)

### Not Included
- Synchronization (CFO, timing offset); blind or pilot-based channel estimation; FEC; RF/SDR

---

## Key Outputs

- **Per-run:** Constellation diagrams at 0, 10, 20 dB (AWGN and multipath); BER vs SNR curves (simulated; theoretical for AWGN); CIR and CFR plots for multipath; CSV: BER vs SNR per modulation.
- **Summary (after running comparison scripts):**
  - **Comparison table** (`results/summary/comparison_table.csv`, `.md`): BER per SNR for AWGN, Multipath (no eq), Multipath ZF, Multipath MMSE (QPSK and 16-QAM). Generated by `plot_ber_comparison.py`. For "Multipath no eq" run once: `run_simulation.py --channel multipath --equalize none --symbols 5000`.
  - **BER comparison plots** (`results/summary/`): AWGN vs Multipath (ZF); 500 vs 5000 symbols; ZF vs MMSE.
  - **Constellation comparison** (`results/summary/constellation_comparison_QPSK.png`, `constellation_comparison_16QAM.png`): 4 columns (AWGN, Multipath no eq, ZF, MMSE) × 3 rows (0, 10, 20 dB), same signal for direct visual comparison. Generated by `plot_constellation_comparison.py`.

---

## Future Extensions

- Pilot-based channel estimation (simulation currently uses known channel for ZF equalization)
- CFO and timing offset; higher-order modulation (64-QAM); FEC; SDR  

---

## Summary

This document describes the **system-level architecture, mathematical foundations, and simulation boundaries** of the OFDM PHY-layer project.  
It serves as a reference for Python module implementation and simulation experiments, forming a baseline for future extensions.
