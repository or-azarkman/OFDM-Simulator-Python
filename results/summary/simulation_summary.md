# OFDM Simulation – Results Summary

## Simulation Configuration
The OFDM system was evaluated under identical conditions using two simulation lengths and two channel types: AWGN and multipath, with optional one-tap ZF or MMSE equalization.

**Common parameters:**
- Modulation schemes: QPSK, 16-QAM (Gray-coded)
- Channel models: **AWGN** (complex baseband) and **multipath** (FIR taps, circular convolution; optional no eq, ZF, or MMSE equalization)
- Receiver: Ideal synchronization (no CFO / timing offset); for multipath, no equalizer, ZF, or MMSE after FFT (`src/equalizers.py`); config: `--equalize none|zf|mmse`
- Evaluation metrics: Bit Error Rate (BER) and Error Vector Magnitude (EVM)
- **Validation:** Theoretical BER curves (QPSK, 16-QAM in AWGN) alongside simulated BER; multipath BER decreases with SNR when ZF or MMSE is applied. EVM quantifies symbol-level accuracy and complements BER analysis.

**Simulation lengths:**
- 500 OFDM symbols
- 5000 OFDM symbols

**Outputs:**
- AWGN: `results/<N>_symbols/` — BER vs SNR, EVM vs SNR, constellation, CSV (BER + EVM).
- Multipath: `results/<N>_symbols_multipath_zf/` or `results/<N>_symbols_multipath_mmse/` — BER vs SNR, EVM vs SNR, constellation, CIR/CFR plots, CSV (BER + EVM).
- **Comparison plots (run after simulations):** 
  - `py simulations/plot_ber_comparison.py` → `results/summary/`: BER plots (AWGN vs Multipath, 500 vs 5000, ZF vs MMSE).
  - `py simulations/plot_evm_comparison.py` → `results/summary/`: EVM plots (AWGN vs Multipath, ZF vs MMSE, all scenarios).
- **Comparison tables:** 
  - `plot_ber_comparison.py` → `comparison_table.csv` and `comparison_table.md` with BER per SNR for AWGN, Multipath (no eq), ZF, MMSE (QPSK and 16-QAM).
  - `plot_evm_comparison.py` → `evm_comparison_table.csv` and `evm_comparison_table.md` with EVM (%) per SNR for all scenarios.
  - For "Multipath no eq" run once: `py run_simulation.py --channel multipath --equalize none --symbols 5000`.
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
- At 10 dB and above, symbol clustering is tight and decision regions are clear; BER drops sharply.
- Under multipath without equalization, points spread into rings at high SNR; ZF/MMSE restores tight clusters.

### 16-QAM
- Higher constellation density leads to increased sensitivity to noise; at low SNR (0–6 dB) spreading is visible.
- Requires higher SNR than QPSK for comparable BER; at 10–20 dB with equalization, clusters become well separated.
- With 5000 symbols, constellation stability and BER curves are more reliable than with 500 symbols.

Increasing the number of OFDM symbols significantly improves constellation stability and reduces visual noise dispersion.

---

## BER and EVM Performance Comparison

| Modulation | Noise Robustness | Spectral Efficiency | BER Stability |
|-----------|------------------|---------------------|---------------|
| QPSK      | High             | Low                 | Very Stable   |
| 16-QAM    | Moderate         | High                | SNR Dependent |

Key observations:
- QPSK consistently achieves lower BER at a given SNR.
- 16-QAM shows higher BER variance, especially with fewer symbols.
- BER curves become smoother and more reliable when using 5000 symbols compared to 500 symbols.
- **EVM:** Lower EVM indicates better symbol accuracy. AWGN shows decreasing EVM with SNR (e.g., ~10% at 20 dB). Multipath without equalization shows high EVM floor; ZF and MMSE reduce EVM, with MMSE typically outperforming ZF at low SNR due to noise-aware equalization.

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
- **Multipath:** Without equalization, multipath causes a high BER floor (especially for 16-QAM); one-tap ZF or MMSE restores performance. ZF vs MMSE trade-off: see `docs/LESSONS_LEARNED.md`. The comparison table and constellation grid illustrate the scenarios.

---

## Outputs reference (plots and parameters)

**Per-run:** `results/<run_dir>/images/` — BER vs SNR, EVM vs SNR, constellation (QPSK, 16-QAM at 0/10/20 dB), CIR/CFR (multipath only). CSV files: `ber_vs_snr_*.csv` and `evm_vs_snr_*.csv`.

**Summary:** `results/summary/` — BER comparison table (CSV, MD, TXT), EVM comparison table (CSV, MD), BER comparison plots (AWGN vs Multipath, 500 vs 5000, ZF vs MMSE), EVM comparison plots (AWGN vs Multipath, ZF vs MMSE, all scenarios), constellation comparison (4×3 grid). Key variables: `fft_size`, `cp_len`, `num_symbols`, `snr_range_db`, `monte_carlo_trials`, `channel_type`, `equalize`, `multipath_taps`.

**Commands:** See `docs/RUN_AND_TEST.md`.

---

## Notes
These results reflect an OFDM PHY layer with AWGN and multipath (ZF or MMSE equalization). Multipath uses circular convolution and one-tap ZF/MMSE so BER and EVM improve with SNR. Metrics: BER (`src/receiver.py`) and EVM (`src/evm.py`). Equalizers: `src/equalizers.py` (ZF, MMSE); CLI: `--equalize none|zf|mmse`. Not included: synchronization (CFO, timing), pilot-based channel estimation, FEC.
