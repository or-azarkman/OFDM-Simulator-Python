# OFDM‑Simulator‑Python  
**OFDM PHY‑layer simulation in Python including QPSK & 16‑QAM, FFT/IFFT, Cyclic Prefix (CP), and BER analysis**

## Overview
This project implements an end‑to‑end **OFDM (Orthogonal Frequency Division Multiplexing) transceiver simulation** in Python, focusing on PHY‑layer signal processing concepts used in modern wireless communication systems.

The goal of this project is to design, implement, and evaluate a modular OFDM system including bit generation, modulation, transmission, channel effects, and receiver processing. The focus is on performance analysis and clear system‑level understanding of core OFDM components.

---

## Project Objectives
- Implement a complete OFDM transmitter and receiver chain  
- Support multiple digital modulation schemes (**QPSK** and **16‑QAM (Gray coded)**)  
- Simulate realistic channel conditions using **AWGN**  
- Evaluate system performance using **BER vs. SNR**  
- Visualize signal behavior using **constellation diagrams and performance plots**  
- Provide clean, modular, and well‑documented code suitable for engineering review

---

## Why OFDM?
Orthogonal Frequency Division Multiplexing (OFDM) is a multi‑carrier modulation technique widely used in modern communication standards such as:
- Wi‑Fi (IEEE 802.11 family)  
- LTE / 5G  
- DVB‑T and other broadcast standards

The key idea in OFDM is to divide the available bandwidth into multiple orthogonal subcarriers, each modulated with its own set of data symbols. A guard interval known as a cyclic prefix is added to mitigate inter‑symbol interference.

Implementing OFDM from scratch demonstrates:
- Understanding of DSP fundamentals such as FFT/IFFT and sampling  
- Practical realization of modulation and demodulation chains for communication systems  
- Ability to integrate modulation schemes, noise modeling, and performance evaluation

---

## Tools & Technologies
This project is developed using:
- **Python 3.x**  
- NumPy — numerical array processing  
- SciPy — scientific computing support  
- Matplotlib — for plotting and visualization

The simulation operates at baseband and does **not** include real‑time hardware or SDR integration.

---

## Project Scope

### Included Features
- Random bitstream generation  
- Digital modulation: **QPSK** and **16‑QAM (Gray coded)**  
- OFDM modulation using **IFFT**  
- Cyclic Prefix (CP) insertion and removal  
- AWGN channel modeling (complex baseband noise according to specified SNR)
- OFDM demodulation using **FFT**  
- Bit Error Rate (BER) computation  
- Constellation and performance visualization

### Receiver Processing
After cyclic prefix removal, the receiver applies an **FFT** to convert time‑domain OFDM symbols back to the frequency domain. These frequency‑domain symbols are then demodulated using the same modulation scheme used at the transmitter (QPSK or 16‑QAM). Finally, the Bit Error Rate (BER) is calculated by comparing the recovered bits to the transmitted bits — matching the standard OFDM demodulation chain.

### Not Included (Stage 1)
- SDR or real‑hardware implementation  
- Synchronization algorithms (CFO, timing offset)  
- Multipath fading channels (future extension)  
- Forward Error Correction (FEC)

---

## Planned Project Structure

```
OFDM‑Simulator‑Python/
│
├── src/             # Core OFDM transmitter and receiver modules
│ ├── transmitter.py # OFDM transmitter implementation
│ ├── receiver.py    # OFDM receiver implementation
│ └── (future utils) # e.g., channel models, plotting helpers
├── simulations/     # Scripts to run experiments (e.g., BER vs SNR, plots)
├── results/         # Generated plots and performance figures
├── docs/            # Documentation and explanations
│ ├── ofdm_overview.md
│ └── images/        # Block diagrams and illustrations
├── README.md        # Project overview and instructions
└── .gitignore
```

---

## Simulation Outputs (Planned)
The simulation produces:
- Time‑domain OFDM waveforms  
- Transmit and receive constellation diagrams  
- BER vs SNR performance curves

These outputs help visualize and compare modulation performance (e.g., QPSK vs 16‑QAM).

---

## Usage Workflow (High‑Level)
A typical experiment flow might include:
1. Generate a random bitstream  
2. Choose a modulation type (QPSK or 16‑QAM)  
3. Use the transmitter module to generate OFDM symbols  
4. Pass symbols through an AWGN channel model  
5. Use the receiver module to recover bits  
6. Plot constellation diagrams and BER vs SNR curves  

Concrete example scripts for these workflows are located in the `simulations/` directory.

---

## Project Status
**Stage 1 – System definition and documentation** is complete.

Upcoming/ongoing work:
- Scripts for performance evaluation and analysis  
- Optional enhancements such as synchronization and advanced channel models

---

## License
This project is licensed under the **MIT License**.

---

## Notes & References
This README reflects standard OFDM system components and simulation methodology based on established OFDM implementations and educational descriptions.
