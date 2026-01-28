# OFDM-Simulator-Python  
**End-to-End OFDM PHY-Layer Simulation in Python (QPSK & 16-QAM)**

---

## Overview
This project implements a complete **OFDM (Orthogonal Frequency Division Multiplexing) baseband transceiver simulation** in Python, covering both transmitter and receiver chains.

The simulator focuses on PHY-layer signal processing concepts used in modern wireless systems and provides quantitative performance evaluation through **BER analysis** and **constellation visualization**.

Supported modulation schemes:
- **QPSK**
- **16-QAM (Gray-coded)**

---

## Project Objectives
- Design and implement a full OFDM transmitter and receiver
- Support multiple digital modulation schemes
- Model realistic noise conditions using **AWGN**
- Evaluate performance using **BER vs. SNR**
- Compare modulation performance under identical channel conditions
- Produce clean, modular, and well-documented code suitable for engineering review

---

## Why OFDM?
OFDM is a multi-carrier modulation technique used in modern communication standards such as:
- Wi-Fi (IEEE 802.11)
- LTE / 5G
- DVB-T

By dividing the available bandwidth into orthogonal subcarriers and using FFT/IFFT processing, OFDM enables efficient spectrum usage and robustness to channel impairments.

This project demonstrates:
- Practical application of FFT/IFFT in communication systems
- End-to-end modulation and demodulation chains
- Performance trade-offs between modulation orders

---

## Tools & Technologies
- **Python 3.x**
- **NumPy** — numerical processing
- **SciPy** — scientific utilities
- **Matplotlib** — constellation and BER visualization

Simulation is performed entirely at **complex baseband** (no RF or SDR hardware).

---

## Implemented System Features

### Transmitter
- Random bitstream generation
- Symbol mapping (QPSK / 16-QAM, Gray-coded)
- OFDM modulation using **IFFT**
- Cyclic Prefix (CP) insertion

### Channel
- **AWGN channel** with configurable SNR
- Complex Gaussian noise scaled according to signal power

### Receiver
- Cyclic Prefix removal
- OFDM demodulation using **FFT**
- Symbol demapping
- Bit Error Rate (BER) calculation

---

## Simulation Results & Analysis

Simulations were executed using:
- **500 OFDM symbols**
- **5000 OFDM symbols**

For each configuration, results include:
- Transmit and receive constellation diagrams
- BER measurements under AWGN
- Visual comparison between QPSK and 16-QAM

### Key Observations
- **QPSK** exhibits strong noise robustness with tighter constellation clustering and lower BER at a given SNR.
- **16-QAM** provides higher spectral efficiency but shows increased sensitivity to noise, requiring higher SNR for comparable BER.
- Increasing the number of OFDM symbols improves BER estimation stability and reduces statistical variance.

---

## Project Structure

```
OFDM-Simulator-Python/
│
├── src/             # Core OFDM system modules
│ ├── transmitter.py # Bit generation, modulation, IFFT, CP insertion
│ ├── receiver.py    # CP removal, FFT, demodulation, BER
│ └── channel.py     # AWGN channel model
│
├── simulations/     # Simulation scripts (BER & constellation runs)
│
├── results/         # Simulation outputs
│ ├── 500_SYMBOLS/
│ │ └── images/      # Constellation & BER plots (500 symbols)
│ │
│ ├── 5000_SYMBOLS/
│ │ └── images/      # Constellation & BER plots (5000 symbols)
│ │
│ └── summary/       # Optional aggregated results / comparisons
│
├── README.md
└── .gitignore
```


---

## Usage Workflow
1. Select modulation scheme (QPSK or 16-QAM)
2. Configure number of OFDM symbols and SNR
3. Run simulation script from `simulations/`
4. Generated plots are saved automatically under `results/`
5. Analyze BER and constellation behavior

---

## Project Status
**Stage: Core PHY-Layer Simulation – Completed**

Implemented and validated:
- OFDM TX/RX chain
- QPSK & 16-QAM modulation
- AWGN channel
- BER computation
- Result visualization

Planned future extensions:
- Multipath fading channels
- Synchronization (CFO, timing offset)
- Channel estimation
- Forward Error Correction (FEC)

---

## License
MIT License

---

## Notes
This project is intended as an educational and professional demonstration of OFDM PHY-layer concepts and is suitable for portfolio presentation and technical interviews.
