# Lessons Learned — OFDM Simulator

Short reflection on what was learned, current limitations, and planned improvements. Next-phase roadmap: `docs/NEXT_PHASE_PLAN.md`.

---

## Lessons learned

- **Cyclic prefix and circular convolution:** The CP turns linear convolution with the channel into circular convolution in the useful part of the symbol. That preserves orthogonality between subcarriers and allows one-tap equalization in the frequency domain (Y_k = H_k X_k + N_k). Without CP, multipath would cause inter-symbol and inter-carrier interference.

- **BER vs spectral efficiency:** QPSK is more robust to noise (lower BER at the same SNR) but carries fewer bits per symbol. 16-QAM doubles the bit rate per symbol at the cost of higher BER for the same SNR. The comparison table and BER vs SNR plots make this trade-off visible across AWGN and multipath scenarios.

- **Why equalization matters in multipath:** Without equalization, the frequency-selective channel distorts the constellation (amplitude and phase per subcarrier). BER stays high even when SNR increases (error floor), especially for 16-QAM. One-tap ZF or MMSE after FFT restores the constellation and brings BER down with SNR.

- **ZF vs MMSE:** ZF inverts the channel (X̂_k = Y_k / H_k), which amplifies noise at subcarriers where |H_k| is small. MMSE balances channel inversion and noise (W_k = H*_k / (|H_k|² + 1/SNR)), often giving better BER at low SNR. The ZF vs MMSE comparison plots illustrate this.

- **Validation:** Comparing simulated BER with theoretical BER (AWGN) and checking constellations at several SNRs helped catch scaling and indexing issues. The 4×3 constellation grid (scenarios × 0/10/20 dB) gives a clear visual comparison of AWGN, multipath without equalizer, ZF, and MMSE.

---

## Limitations (what this project does not cover)

- **Synchronization:** Ideal timing and frequency are assumed. No carrier frequency offset (CFO), no symbol timing offset (STO). In a real system, CFO and STO must be estimated and corrected before equalization.

- **Channel knowledge:** The receiver uses the true channel response H for ZF/MMSE. There is no pilot-based or blind channel estimation. Real receivers estimate H from pilots or preambles.

- **Forward error correction (FEC):** No coding (e.g. convolutional or LDPC). BER results are for uncoded transmission.

- **Other:** No multi-antenna (MIMO), no RF/SDR; simulation is complex baseband only.

---

## Future improvements (planned or optional)

In order of priority (see `docs/NEXT_PHASE_PLAN.md` for details):

1. **EVM (Error Vector Magnitude):** Add computation and plots of EVM vs SNR (and optionally vs scenario). EVM is a standard metric in 3GPP and Wi-Fi; easy to add from existing symbols.

2. **Pilots and channel estimation:** Insert pilot subcarriers, estimate H from pilots (e.g. least-squares), use estimated H in ZF/MMSE. Moves from “known channel” to “estimated channel.”

3. **CFO (Carrier frequency offset):** Model phase drift (e.g. exp(j·2π·Δf·n)), then correct using correlation with preamble or pilots. Document as a synchronization impairment and correction step.

4. **STO (Symbol timing offset):** Model symbol delay, then detect and correct (e.g. using CP or preamble correlation). Complements CFO in a “sync” story.

5. **64-QAM:** Optional; QPSK and 16-QAM already demonstrate the modulation and BER trade-off.

6. **FEC:** Optional; larger scope. Can be listed as long-term future work.

---

## Summary

The project implements a full OFDM baseband chain with AWGN and multipath, ZF/MMSE equalization, and systematic validation (BER, constellations, comparison table). The main gaps are synchronization (CFO/STO) and channel estimation (pilots); these are documented as limitations and as the next steps to implement. This document serves as a concise reference for what was learned and what comes next.
