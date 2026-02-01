# OFDM Simulation – Results Summary

## Simulation Configuration
The OFDM system was evaluated under identical conditions using two simulation lengths and two channel types: AWGN and multipath, with optional one-tap ZF or MMSE equalization.

**Common parameters:**
- Modulation schemes: QPSK, 16-QAM (Gray-coded)
- Channel models: **AWGN** (complex baseband) and **multipath** (FIR taps, circular convolution; optional no eq, ZF, or MMSE equalization)
- Receiver: Ideal synchronization (no CFO / timing offset); for multipath, no equalizer, ZF, or MMSE after FFT (`src/equalizers.py`); config: `--equalize none|zf|mmse`
- Evaluation metric: Bit Error Rate (BER)
- **Validation:** Theoretical BER curves (QPSK, 16-QAM in AWGN) alongside simulated BER; multipath BER decreases with SNR when ZF or MMSE is applied.

**Simulation lengths:**
- 500 OFDM symbols
- 5000 OFDM symbols

**Outputs:**
- AWGN: `results/<N>_symbols/` — BER vs SNR, constellation, CSV.
- Multipath: `results/<N>_symbols_multipath_zf/` or `results/<N>_symbols_multipath_mmse/` — BER vs SNR, constellation, CIR/CFR plots, CSV.
- **Comparison plots (run after simulations):** `py simulations/plot_ber_comparison.py` → `results/summary/`: AWGN vs Multipath (ZF), 500 vs 5000 symbols (multipath), ZF vs MMSE.
- **Comparison table:** same script → `comparison_table.csv` and `comparison_table.md` with BER per SNR for AWGN, Multipath (no eq), ZF, MMSE (QPSK and 16-QAM). For "Multipath no eq" run once: `py run_simulation.py --channel multipath --equalize none --symbols 5000`.
- **Constellation comparison:** `py simulations/plot_constellation_comparison.py` → `constellation_comparison_QPSK.png`, `constellation_comparison_16QAM.png`: 4 columns (AWGN, Multipath no eq, ZF, MMSE) × 3 rows (0, 10, 20 dB), same signal for direct visual comparison.

---

## Validation (before running comparison scripts)

**AWGN:** Simulated BER matches theoretical curves (QPSK, 16-QAM); both decrease with SNR. No mismatch.

**Multipath (no equalizer):** QPSK BER can still decrease with SNR (fewer constellation points → more robust to channel distortion). **16-QAM shows an error floor (BER ~10–15%) — this is expected**, not a bug: without equalization the channel distorts the constellation; 16-QAM (16 points) is much more sensitive than QPSK (4 points), so the nearest-neighbor demodulator sees a smeared constellation and errors saturate. With ZF or MMSE equalization, both modulations show BER decreasing with SNR as expected. **Constellation 4×3:** In "Multipath (no eq)" at 20 dB, QPSK/16-QAM can show **rings** (circular spread around each point) — this is **normal**: at high SNR the dominant effect is multipath (phase/amplitude distortion), not noise; without equalization the channel spreads each constellation point into a ring. With ZF or MMSE the rings collapse back to tight clusters.

**Multipath (ZF / MMSE):** BER decreases with SNR for both QPSK and 16-QAM; equalization restores performance.

---

## Constellation Analysis

### QPSK
- Constellation points remain well separated under AWGN.
- Even at moderate SNR values, symbol clustering is tight.
- Decision regions are robust, resulting in low BER.

### 16-QAM
- Higher constellation density leads to increased sensitivity to noise.
- At lower SNRs, visible symbol spreading causes decision ambiguity.
- Requires higher SNR to achieve BER comparable to QPSK.

Increasing the number of OFDM symbols significantly improves constellation stability and reduces visual noise dispersion.

---

## BER Performance Comparison

| Modulation | Noise Robustness | Spectral Efficiency | BER Stability |
|-----------|------------------|---------------------|---------------|
| QPSK      | High             | Low                 | Very Stable   |
| 16-QAM    | Moderate         | High                | SNR Dependent |

Key observations:
- QPSK consistently achieves lower BER at a given SNR.
- 16-QAM shows higher BER variance, especially with fewer symbols.
- BER curves become smoother and more reliable when using 5000 symbols compared to 500 symbols.

---

## Impact of Number of Symbols
- **500 symbols**:  
  - Faster simulation  
  - Higher statistical variance in BER  
  - Suitable for quick validation and debugging

- **5000 symbols**:  
  - More accurate BER estimation  
  - Reduced randomness effects  
  - Preferred for performance evaluation and comparison

---

## Engineering Conclusions
- There is a clear trade-off between **spectral efficiency** and **noise robustness**.
- QPSK is suitable for low-SNR or reliability-critical links.
- 16-QAM provides higher throughput but demands better channel conditions.
- Increasing the number of simulated symbols is essential for reliable BER analysis.
- **Multipath:** Without equalization, multipath causes a high BER floor (especially visible for 16-QAM; QPSK may still improve with SNR). One-tap ZF or MMSE restores performance. ZF inverts the channel (noise amplification at nulls); MMSE balances channel inversion and noise (often better at low SNR). The comparison table and constellation grid (AWGN vs Multipath no eq vs ZF vs MMSE) illustrate the trade-offs.

---

## Outputs reference (plots and parameters)

**Plots (per run):** `results/<run_dir>/images/` — BER vs SNR, constellation (QPSK, 16-QAM at 0/10/20 dB), CIR/CFR (multipath only).

**Summary outputs (after `plot_ber_comparison.py` and `plot_constellation_comparison.py`):**
- `results/summary/comparison_table.csv` (long format: SNR_dB, Scenario, Modulation, BER), `comparison_table.md` (4 tables), `comparison_table_readable.txt` (same 4 tables, plain text).
- `results/summary/ber_comparison_awgn_vs_multipath_<N>symbols.png`, `ber_500_vs_5000_multipath_qpsk.png`, `ber_500_vs_5000_multipath_16qam.png`, `ber_comparison_zf_vs_mmse_<N>symbols.png`.
- `results/summary/constellation_comparison_QPSK.png`, `constellation_comparison_16QAM.png` — 4×3 grid (scenarios × 0/10/20 dB).

**Key variables:** `fft_size`, `cp_len`, `num_symbols`, `snr_range_db`, `monte_carlo_trials`, `channel_type`, `equalize`, `multipath_taps` (config); BER, SNR (dB); theoretical BER (AWGN).

**Commands:** `py run_simulation.py`; `py run_simulation.py --channel multipath --equalize none|zf|mmse`; `py simulations/plot_ber_comparison.py` (includes table); `py simulations/plot_constellation_comparison.py`; `py -m pytest tests/ -v`.

---

## Notes
These results reflect an OFDM PHY layer with AWGN and multipath (ZF or MMSE equalization). Multipath uses circular convolution and one-tap ZF/MMSE so BER improves with SNR. Equalizers: `src/equalizers.py` (ZF, MMSE); CLI: `--equalize none|zf|mmse`. Not included: synchronization (CFO, timing), pilot-based channel estimation, FEC.
