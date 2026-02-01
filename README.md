# OFDM-Simulator-Python

**End-to-End OFDM PHY-Layer Simulation in Python (QPSK & 16-QAM)**

OFDM baseband transceiver: theoretical BER (AWGN), Monte Carlo BER vs SNR, QPSK and 16-QAM, AWGN and multipath channels, ZF/MMSE equalization, unit tests.

---

## Quick Start

**Windows (use `py`):**

```powershell
git clone https://github.com/or-azarkman/OFDM-Simulator-Python.git
cd OFDM-Simulator-Python

py -m pip install -r requirements.txt

py run_simulation.py

py run_simulation.py --symbols 500 --trials 20
py run_simulation.py --channel multipath
py run_simulation.py --channel multipath --equalize mmse
py run_simulation.py --channel multipath --equalize none --symbols 5000   # for full comparison table

# Comparison outputs (after simulations)
py simulations/plot_ber_comparison.py
py simulations/plot_constellation_comparison.py

# Run tests
py -m pytest tests/ -v
```

**Linux/macOS** (if `python` or `python3` is in PATH): use `pip install -r requirements.txt`, `python run_simulation.py`, `pytest tests/ -v`.

From the project root: run `run_simulation.py`.

Results: `results/5000_symbols/` (AWGN), `results/5000_symbols_multipath_zf/` or `_mmse/` (multipath); each has `images/` and CSV. Comparison: `py simulations/plot_ber_comparison.py` (BER plots + table), `py simulations/plot_constellation_comparison.py` (4×3 constellation grid). Commands: `docs/RUN_AND_TEST.md`.

---

## Overview

This project implements a complete **OFDM (Orthogonal Frequency Division Multiplexing) baseband transceiver simulation** in Python, covering:

- **Transmitter:** Bit generation → QPSK/16-QAM (Gray) → subcarrier mapping → IFFT → cyclic prefix
- **Channel:** AWGN or multipath (FIR taps + AWGN). Multipath: circular convolution then AWGN; Y_k = H_k·X_k + N_k in frequency.
- **Receiver:** CP removal (or use channel output for multipath) → FFT → one-tap equalization (ZF or MMSE when multipath) → demodulation → BER
- **Validation:** Theoretical BER (AWGN); simulated BER and constellation for AWGN and multipath; CIR/CFR plots for multipath

Supported modulation: **QPSK**, **16-QAM (Gray-coded)**.

---

## Why OFDM?

OFDM is the foundation of modern wireless PHY layers:

| Standard   | Use of OFDM        |
|-----------|--------------------|
| Wi-Fi     | IEEE 802.11 a/g/n/ac/ax |
| LTE / 5G  | Downlink / uplink  |
| DVB-T     | Digital TV         |

By splitting bandwidth into orthogonal subcarriers and using **IFFT/FFT**, OFDM achieves high spectral efficiency and robustness to multipath. This project demonstrates the full chain at **complex baseband** (no RF); all processing is baseband-only, with no RF front-end or SDR.

---

## Project Structure

```
OFDM-Simulator-Python/
├── src/
│   ├── transmitter.py
│   ├── receiver.py
│   ├── channel.py          # AWGN + multipath
│   ├── theory.py
│   └── equalizers.py       # ZF, MMSE one-tap
├── simulations/
│   ├── config.py
│   ├── run_ber_and_constellation.py
│   ├── plot_ber_comparison.py      # BER plots + comparison table
│   └── plot_constellation_comparison.py  # 4×3 constellation grid
├── tests/
│   ├── test_transmitter.py
│   ├── test_receiver.py
│   ├── test_channel.py
│   ├── test_theory.py
│   └── test_equalizers.py
├── results/
│   ├── <N>_symbols/                 # AWGN
│   ├── <N>_symbols_multipath/       # multipath, no equalizer
│   ├── <N>_symbols_multipath_zf/
│   ├── <N>_symbols_multipath_mmse/
│   └── summary/                     # comparison table, BER plots, constellation grid
├── docs/
├── requirements.txt
└── README.md
```

---

## Configuration & Reproducibility

Simulation parameters are centralized in `simulations/config.py`:

| Parameter            | Default          | Description                            |
|----------------------|------------------|----------------------------------------|
| `fft_size`           | 64               | Number of subcarriers                  |
| `cp_len`             | 16               | Cyclic prefix length                   |
| `num_symbols`        | 5000             | OFDM symbols per run                   |
| `monte_carlo_trials` | 50               | Trials per SNR point                   |
| `snr_range_db`       | 0–20, step 2     | SNR sweep (dB)                         |
| `random_seed`        | 42               | Reproducible runs                      |
| `channel_type`       | "awgn"           | "awgn" or "multipath"                  |
| `equalize`           | "zf"             | "none", "zf", or "mmse" (for multipath)|
| `multipath_taps`     | [1,0,0.4·e^j0.5] | FIR taps (multipath only)              |

Results: `results/<N>_symbols/` (AWGN), `results/<N>_symbols_multipath_zf/` or `_multipath_mmse/` (multipath); each has CSV and `images/`. Example: `run_simulation.py --symbols 500 --channel multipath --equalize zf`.

---

## Simulation Results

- **BER vs SNR:** Simulated (Monte Carlo) and **theoretical** curves for QPSK and 16-QAM. Close match validates the implementation.
- **Constellation diagrams** at 0, 10, 20 dB for both modulations.
- **CSV:** `ber_vs_snr_<N>symbols_qpsk.csv` and `_16qam.csv` for further analysis.
- **Comparison table:** `results/summary/comparison_table.csv` (long format), `comparison_table.md` (4 tables), `comparison_table_readable.txt` — BER per SNR for AWGN, Multipath (no eq), ZF, MMSE. Generated by `plot_ber_comparison.py`.
- **Constellation comparison:** `results/summary/constellation_comparison_*.png` — 4 columns (AWGN, Multipath no eq, ZF, MMSE) × 3 rows (0, 10, 20 dB). Generated by `plot_constellation_comparison.py`.

### Key Observations

- **QPSK:** Lower BER at a given SNR; better noise robustness, lower spectral efficiency.
- **16-QAM:** Higher throughput (4 bits/symbol) but needs higher SNR for similar BER.
- **Theoretical vs simulated (AWGN):** Agreement confirms correct modulation, channel scaling, and BER computation.
- **Multipath:** Circular convolution + one-tap ZF or MMSE equalization; BER decreases with SNR. Without equalization, multipath gives a high BER floor.

---

## Key concepts

Baseband chain: bits → modulation → IFFT → CP; receiver: CP removal → FFT → ZF/MMSE equalization (multipath) → demod → BER. CP enables circular convolution and one-tap equalization. Gray coding; theoretical BER (AWGN). Tests: transmitter, receiver, channel, theory, equalizers. For lessons learned and next-phase roadmap, see `docs/LESSONS_LEARNED.md` and `docs/NEXT_PHASE_PLAN.md`.

---

## Tools & Technologies

- **Python 3.9+**
- **NumPy** — arrays, FFT/IFFT
- **SciPy** — `erfc` for theoretical BER
- **Matplotlib** — BER and constellation plots
- **pytest** — unit tests

---

## Running Tests

From the project root:

```powershell
py -m pytest tests/ -v
py -m pytest tests/ -v --cov=src   # with coverage (requires pytest-cov)
```

On Linux/macOS: `pytest tests/ -v`. Full run/test reference: **`docs/RUN_AND_TEST.md`**.

Tests cover: transmitter, receiver, channel (AWGN + multipath), theory, equalizers (ZF, MMSE).

---

## License

MIT License.

---

## Notes

OFDM PHY-layer simulation. Mathematical details: `docs/ofdm_overview.md`. Lessons learned, limitations, and future work: `docs/LESSONS_LEARNED.md`. Next phase (EVM, pilots, CFO, STO): `docs/NEXT_PHASE_PLAN.md`.
