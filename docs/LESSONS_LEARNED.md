# Lessons Learned — OFDM Simulator

Short reflection on what was learned, current limitations, and planned improvements. Next-phase roadmap: `docs/NEXT_PHASE_PLAN.md`.

---

## Lessons learned

- **Cyclic prefix and circular convolution:** The CP turns linear convolution with the channel into circular convolution in the useful part of the symbol. That preserves orthogonality between subcarriers and allows one-tap equalization in the frequency domain:
  $$Y_k = H_k X_k + N_k$$
  Without CP, multipath would cause inter-symbol and inter-carrier interference.

- **BER vs spectral efficiency:** QPSK is more robust to noise (lower BER at the same SNR) but carries fewer bits per symbol. 16-QAM doubles the bit rate per symbol at the cost of higher BER for the same SNR. The comparison table and BER vs SNR plots make this trade-off visible across AWGN and multipath scenarios.

- **Modulation choice when BER or EVM is too high:** In real systems (3GPP, Wi‑Fi), if the chosen modulation yields BER or EVM above the link budget or standard mask, the designer **steps down to a lower-order modulation** (e.g. 64‑QAM → 16‑QAM → QPSK). Lower-order modulations have **wider decision regions** and fewer constellation points, so they tolerate more noise and channel/estimation error while meeting EVM and BER targets—at the cost of spectral efficiency. This is especially important for **64‑QAM and 256‑QAM**, where EVM requirements are strict and channel estimation errors have a larger impact; the simulator’s QPSK vs. 16‑QAM comparison illustrates the same principle.

- **Why equalization matters in multipath:** Without equalization, the frequency-selective channel distorts the constellation (amplitude and phase per subcarrier). BER stays high even when SNR increases (error floor), especially for 16-QAM. One-tap ZF or MMSE after FFT restores the constellation and brings BER down with SNR.

- **ZF vs MMSE:** ZF inverts the channel $$\hat{X}_k = Y_k / H_k$$, which amplifies noise at subcarriers where $$|H_k|$$ is small. MMSE balances channel inversion and noise:
  $$W_k^{\text{MMSE}} = \frac{H_k^*}{|H_k|^2 + 1/\mathrm{SNR}}$$
  often giving better BER and EVM at low SNR. The ZF vs MMSE comparison plots illustrate this.

- **Validation:** Comparing simulated BER with theoretical BER (AWGN) and checking constellations at several SNRs helped catch scaling and indexing issues. The 4×3 constellation grid (scenarios × 0/10/20 dB) gives a clear visual comparison of AWGN, multipath without equalizer, ZF, and MMSE. EVM provides an additional validation metric that quantifies symbol-level accuracy independently of hard decisions.

- **Pilot-based channel estimation:** In real systems, the channel is unknown and must be estimated from pilots. The comparison plots (`plot_pilots_comparison.py`) demonstrate that estimation errors degrade performance compared to perfect channel knowledge, especially at low SNR. The degradation depends on pilot density (more pilots → better estimation but lower data rate) and interpolation quality. At high SNR, pilot-based estimation approaches known-channel performance, validating the LS estimation approach. Channel estimation accuracy plots show that interpolation introduces errors between pilot positions, which is expected and demonstrates realistic system behavior.

---

## Limitations (what this project does not cover)

- **Synchronization:** Ideal timing and frequency are assumed. No carrier frequency offset (CFO), no symbol timing offset (STO). In a real system, CFO and STO must be estimated and corrected before equalization.

- **Channel knowledge:** When pilots are disabled, the receiver uses the true channel response H for ZF/MMSE. When pilots are enabled, the receiver estimates H from pilots using Least Squares (LS) estimation. Blind channel estimation is not implemented.

- **Forward error correction (FEC):** No coding (e.g. convolutional or LDPC). BER results are for uncoded transmission.

- **Other:** No multi-antenna (MIMO), no RF/SDR; simulation is complex baseband only.

---

## Future improvements (planned or optional)

In order of priority (see `docs/NEXT_PHASE_PLAN.md` for details):

1. ~~**EVM (Error Vector Magnitude):**~~ **Done.** EVM computation and plots implemented (`src/evm.py`); EVM vs SNR per run; comparison plots and table in `results/summary/evm/`. EVM is a standard metric in 3GPP and Wi-Fi that complements BER by quantifying symbol-level accuracy.

2. ~~**Pilots and channel estimation:**~~ **Done.** Pilot subcarrier insertion (`src/pilots.py`), LS channel estimation from pilots, integration into transmitter/receiver; comparison plots in `results/summary/pilots/`. When pilots are enabled, the receiver estimates H from pilots and uses it in ZF/MMSE equalization. Moves from “known channel” to “estimated channel.”

3. **CFO (Carrier frequency offset):** Model phase drift (e.g. $$\exp(j \cdot 2\pi \cdot \Delta f \cdot n)$$), then correct using correlation with preamble or pilots. Document as a synchronization impairment and correction step.

4. **STO (Symbol timing offset):** Model symbol delay, then detect and correct (e.g. using CP or preamble correlation). Complements CFO in a “sync” story.

5. **64-QAM:** Optional; QPSK and 16-QAM already demonstrate the modulation and BER trade-off.

6. **FEC:** Optional; larger scope. Can be listed as long-term future work.

---

## Summary

The project implements a full OFDM baseband chain with AWGN and multipath, ZF/MMSE equalization, pilot-based channel estimation, and systematic validation (BER, EVM, constellations, comparison tables). The main remaining gaps are synchronization (CFO/STO); these are documented as limitations and as the next steps to implement. This document serves as a concise reference for what was learned and what comes next.
