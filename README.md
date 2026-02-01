# OFDM-Simulator-Python

**End-to-End OFDM PHY-Layer Simulation in Python (QPSK & 16-QAM)**

A professional-grade OFDM baseband transceiver simulator with **theoretical BER validation**, **Monte Carlo BER curves**, **reproducible experiments**, and **unit tests** — suitable for portfolio and technical interviews.

---

## Quick Start

**Windows (use `py`):**

```powershell
# Clone and enter project
git clone <repo-url>
cd OFDM-Simulator-Python

# Install dependencies (Python 3.9+)
py -m pip install -r requirements.txt

# Run simulation
py run_simulation.py

# Optional: fewer symbols / trials
py run_simulation.py --symbols 500 --trials 20

# Run tests
py -m pytest tests/ -v
```

**Linux/macOS** (if `python` or `python3` is in PATH): use `pip install -r requirements.txt`, `python run_simulation.py`, `pytest tests/ -v`.

**From Cursor:** Open `run_simulation.py` → right-click → **Run Python File**, or run `py run_simulation.py` in the integrated Terminal (project root).

**Where results go:** `results/<num_symbols>_symbols/images/` (plots) and `results/<num_symbols>_symbols/*.csv`.  
Step-by-step (Windows with `py`): **`docs/HOW_TO_RUN.md`**.

**Default run:** 5000 OFDM symbols, 50 Monte Carlo trials, SNR 0–20 dB. Outputs: BER vs SNR (simulated + theoretical), constellation plots, CSV data under `results/5000_symbols/`.

---

## Overview

This project implements a complete **OFDM (Orthogonal Frequency Division Multiplexing) baseband transceiver simulation** in Python, covering:

- **Transmitter:** Bit generation → QPSK/16-QAM (Gray) → subcarrier mapping → IFFT → cyclic prefix
- **Channel:** AWGN with configurable SNR (Es/N0)
- **Receiver:** CP removal → FFT → demodulation → BER computation
- **Validation:** Theoretical BER curves (QPSK, 16-QAM) plotted alongside simulated BER

Supported modulation: **QPSK**, **16-QAM (Gray-coded)**.

---

## Why OFDM?

OFDM is the foundation of modern wireless PHY layers:

| Standard   | Use of OFDM        |
|-----------|--------------------|
| Wi-Fi     | IEEE 802.11 a/g/n/ac/ax |
| LTE / 5G  | Downlink / uplink  |
| DVB-T     | Digital TV         |

By splitting bandwidth into orthogonal subcarriers and using **IFFT/FFT**, OFDM achieves high spectral efficiency and robustness to multipath. This project demonstrates the full chain at **complex baseband** (no RF).

---

## Project Structure

```
OFDM-Simulator-Python/
├── src/                    # Core OFDM modules
│   ├── transmitter.py      # Bits, modulation, IFFT, CP
│   ├── receiver.py         # CP removal, FFT, demod, BER
│   ├── channel.py          # AWGN channel
│   └── theory.py           # Theoretical BER (QPSK, 16-QAM)
├── simulations/
│   ├── config.py           # SimulationConfig, seed, paths
│   └── run_ber_and_constellation.py   # Main pipeline
├── tests/                  # Unit tests (pytest)
│   ├── test_transmitter.py
│   ├── test_receiver.py
│   ├── test_channel.py
│   └── test_theory.py
├── results/
│   ├── <N>_symbols/        # Per-run: CSV + images/
│   └── summary/
├── docs/                   # OFDM overview, block diagram
├── requirements.txt
└── README.md
```

---

## Configuration & Reproducibility

Simulation parameters are centralized in `simulations/config.py`:

| Parameter           | Default   | Description                    |
|--------------------|-----------|--------------------------------|
| `fft_size`         | 64        | Number of subcarriers          |
| `cp_len`           | 16        | Cyclic prefix length           |
| `num_symbols`      | 5000      | OFDM symbols per run          |
| `monte_carlo_trials` | 50      | Trials per SNR point           |
| `snr_range_db`     | 0–20, step 2 | SNR sweep (dB)             |
| `random_seed`      | 42        | Reproducible runs              |

Results are written to `results/<num_symbols>_symbols/` (CSV and `images/`). To change symbol count, instantiate `SimulationConfig(num_symbols=500)` and pass it to `main(config)`.

---

## Simulation Results

- **BER vs SNR:** Simulated (Monte Carlo) and **theoretical** curves for QPSK and 16-QAM. Close match validates the implementation.
- **Constellation diagrams** at 0, 10, 20 dB for both modulations.
- **CSV:** `ber_vs_snr_<N>symbols_qpsk.csv` and `_16qam.csv` for further analysis.

### Key Observations

- **QPSK:** Lower BER at a given SNR; better noise robustness, lower spectral efficiency.
- **16-QAM:** Higher throughput (4 bits/symbol) but needs higher SNR for similar BER.
- **Theoretical vs simulated:** Agreement confirms correct modulation, channel scaling, and BER computation.

---

## Key concepts

Full baseband chain (bits → QPSK/16-QAM → IFFT → CP; receiver: CP removal → FFT → demod → BER). Cyclic prefix enables circular convolution and one-tap equalization. Gray coding minimizes bit errors per symbol error. Theoretical BER curves validate the implementation. Config and seed ensure reproducibility; unit tests cover transmitter, receiver, channel, and theory.

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

```bash
pytest tests/ -v
pytest tests/ -v --cov=src   # with coverage
```

Tests cover: bit generation, QPSK/16-QAM roundtrip (no noise), subcarrier mapping, IFFT/FFT/CP, AWGN behavior, theoretical BER API.

---

## License

MIT License.

---

## Notes

This project is intended as an **educational and professional demonstration** of OFDM PHY-layer concepts. It is suitable for:

- Portfolio and GitHub showcase
- Technical interviews (PHY, wireless, DSP)
- Extensions: multipath channel, CFO/timing, channel estimation, FEC

See `docs/ofdm_overview.md` for mathematical details and system block diagram.
