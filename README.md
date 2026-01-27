# OFDM-Simulator-Python
**OFDM PHY-layer simulation in Python including QAM, FFT/IFFT, CP and BER analysis**


## Overview
This project implements an end-to-end **OFDM (Orthogonal Frequency Division Multiplexing) transceiver simulation** in Python, focusing on PHY-layer concepts used in modern wireless communication systems.

The goal of the project is to design, implement, and evaluate a modular OFDM system, including modulation, transmission, channel effects, and receiver processing, with an emphasis on performance analysis and clear system-level understanding.

---

## Project Objectives
- Implement a complete OFDM transmitter and receiver chain
- Support digital modulation schemes (e.g. QPSK / QAM)
- Simulate realistic channel conditions (AWGN)
- Evaluate system performance using **BER vs SNR**
- Visualize signal behavior using **constellation diagrams and plots**
- Write clean, modular, and well-documented code suitable for engineering review

---

## Why OFDM?
OFDM is a fundamental modulation technique used in modern communication standards such as:
- Wi-Fi (IEEE 802.11)
- LTE / 5G
- DVB-T

Implementing OFDM from scratch demonstrates:
- Understanding of DSP fundamentals (FFT/IFFT, sampling, noise)
- Ability to design and analyze communication systems
- Practical PHY-layer engineering skills relevant to industry roles

---

## Tools & Technologies
- **Python 3.x**
- NumPy
- SciPy
- Matplotlib

The project focuses on simulation and analysis only, without SDR or hardware integration.

---

## Project Scope
### Included:
- Bitstream generation
- Digital modulation (QPSK / QAM)
- OFDM modulation (IFFT)
- Cyclic Prefix insertion and removal
- AWGN channel modeling
- OFDM demodulation (FFT)
- BER computation
- Constellation and performance plots

### Not Included:
- SDR or real-time hardware implementation
- Synchronization algorithms (CFO, timing offset) — optional future extension
- Multipath fading (may be added in later stages)

---
```

## Planned Project Structure

OFDM-Simulator-Python/
│
├── src/         # Core OFDM transmitter and receiver modules
├── simulations/ # Scripts for running simulations and experiments
├── results/     # Generated plots and performance figures
├── docs/        # Theory, design decisions, and explanations
├── README.md    # Project documentation
└── .gitignore

```
---

## Simulation Outputs (Planned)
- Time-domain OFDM signals
- Constellation diagrams (TX and RX)
- BER vs SNR performance curves

---

## Project Status
**Stage 1 – System definition and documentation**

Upcoming stages:
- OFDM transmitter implementation
- Channel modeling and receiver design
- Performance evaluation and analysis

---

## License
This project is licensed under the MIT License.

