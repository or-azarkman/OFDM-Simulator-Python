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
- **Comparison plots (run after simulations):** Summary outputs are organized by metric in `results/summary/`:
  - **BER:** `py simulations/plot_ber_comparison.py` → `results/summary/ber/`: BER plots (AWGN vs Multipath, 500 vs 5000, ZF vs MMSE), comparison tables (CSV, MD, TXT).
  - **EVM:** `py simulations/plot_evm_comparison.py` → `results/summary/evm/`: EVM plots (AWGN vs Multipath, ZF vs MMSE, all scenarios), comparison tables (CSV, MD).
  - **Constellation:** `py simulations/plot_constellation_comparison.py` → `results/summary/constellation/`: 4×3 grid (AWGN, Multipath no eq, ZF, MMSE × 0, 10, 20 dB) for QPSK and 16‑QAM.
  - **Pilots:** `py simulations/plot_pilots_comparison.py` → `results/summary/pilots/`: Channel estimation accuracy (true H vs estimated H, MSE per subcarrier), BER/EVM/constellation comparison (known channel vs pilot-based).
- For "Multipath no eq" run once: `py run_simulation.py --channel multipath --equalize none --symbols 5000`.

---

## Validation (before running comparison scripts)

**AWGN:** Simulated BER matches theoretical curves (QPSK, 16-QAM); both decrease with SNR. No mismatch.

**Multipath (no equalizer):** QPSK BER can still decrease with SNR (fewer constellation points → more robust to channel distortion). **16-QAM shows an error floor (BER ~10–15%) — this is expected**, not a bug: without equalization the channel distorts the constellation; 16-QAM (16 points) is much more sensitive than QPSK (4 points), so the nearest-neighbor demodulator sees a smeared constellation and errors saturate. With ZF or MMSE equalization, both modulations show BER decreasing with SNR as expected. **Constellation 4×3:** In "Multipath (no eq)" at 20 dB, QPSK/16-QAM can show **rings** (circular spread around each point) — this is **normal**: at high SNR the dominant effect is multipath (phase/amplitude distortion), not noise; without equalization the channel spreads each constellation point into a ring. With ZF or MMSE the rings collapse back to tight clusters.

**Multipath (ZF / MMSE):** BER decreases with SNR for both QPSK and 16-QAM; equalization restores performance.

**Pilot-based channel estimation:** When pilots are enabled (`--pilots`), the receiver estimates the channel from pilot subcarriers using Least Squares (LS) estimation. Comparison plots (`plot_pilots_comparison.py`) show that estimation errors degrade BER and EVM compared to perfect channel knowledge, especially at low SNR. At high SNR (≥18 dB), pilot-based estimation approaches known-channel performance, validating the LS approach. Channel estimation accuracy plots demonstrate that interpolation introduces errors between pilot positions, which is expected in real systems. The degradation depends on pilot density (more pilots → better estimation but lower data rate) and SNR.

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

| Modulation | Noise Robustness | Spectral Efficiency | BER Stability | Decision regions |
|-----------|------------------|---------------------|---------------|------------------|
| QPSK      | High             | Low (2 b/sym)       | Very stable   | Widest (4 points) |
| 16-QAM    | Moderate         | High (4 b/sym)     | SNR dependent | Tighter (16 points) |

**Key observations:**
- QPSK consistently achieves lower BER and better EVM at a given SNR; wider decision regions tolerate more noise and channel/estimation error.
- 16-QAM shows higher BER and EVM for the same SNR; tighter constellation spacing increases sensitivity to distortion.
- BER and EVM curves become smoother and more reliable when using 5000 symbols compared to 500 symbols.
- **EVM:** Lower EVM indicates better symbol accuracy. EVM (RMS) is defined as
  $$\mathrm{EVM}_{\mathrm{RMS}} = \sqrt{ \frac{\mathbb{E}[|R_k - X_k|^2]}{\mathbb{E}[|X_k|^2]} }$$
  where $$R_k$$ are the received (equalized) symbols and $$X_k$$ the transmitted symbols; reported as a percentage (100 × EVM_RMS). AWGN shows decreasing EVM with SNR (e.g. ~10% at 20 dB). Multipath without equalization shows a high EVM floor; ZF and MMSE reduce EVM, with MMSE typically outperforming ZF at low SNR due to noise-aware equalization.

**Modulation choice in practice:** When BER or EVM exceeds the link budget or standard mask (e.g. 3GPP/Wi‑Fi EVM limits), the usual approach is to **step down to a lower-order modulation** (e.g. 64‑QAM → 16‑QAM → QPSK). Lower-order modulations have **wider, clearer decision regions**, so they meet EVM and BER targets at the cost of spectral efficiency—especially relevant for 64‑QAM and 256‑QAM, where EVM requirements are strict and channel estimation errors have a larger impact.

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
- There is a clear trade-off between **spectral efficiency** and **noise robustness**: higher-order modulation (e.g. 16‑QAM) gives more bits per symbol but requires better SNR and lower EVM to achieve acceptable BER.
- **QPSK** is suitable for low-SNR or reliability-critical links; wider decision regions make it tolerant to channel and estimation errors.
- **16‑QAM** provides higher throughput but demands better channel conditions and is more sensitive to EVM and channel estimation errors.
- When **BER or EVM is too high**, stepping down to a lower-order modulation (wider decision regions) is the standard way to meet EVM and BER targets—especially for precision applications and high-order QAM (64/256‑QAM).
- Increasing the number of simulated symbols is essential for reliable BER and EVM analysis.
- **Multipath:** Without equalization, multipath causes a high BER floor (especially for 16‑QAM); one-tap ZF or MMSE restores performance. ZF vs MMSE trade-off: see `docs/LESSONS_LEARNED.md`. The comparison table and constellation grid illustrate the scenarios.
- **Pilot-based channel estimation:** Estimation errors degrade BER and EVM compared to perfect channel knowledge; at high SNR, pilot-based performance approaches known-channel. Channel estimation accuracy plots show the impact of interpolation between pilot positions.

---

## Outputs reference (plots and parameters)

**Per-run:** `results/<run_dir>/images/` — BER vs SNR, EVM vs SNR, constellation (QPSK, 16-QAM at 0/10/20 dB), CIR/CFR (multipath only). CSV files: `ber_vs_snr_*.csv` and `evm_vs_snr_*.csv`.

**Summary:** `results/summary/` — organized by metric: `ber/` (BER plots and tables), `evm/` (EVM plots and tables), `constellation/` (4×3 grid), `pilots/` (channel estimation accuracy and known vs pilot-based comparisons), `docs/` (this summary and run instructions). Key variables: `fft_size`, `cp_len`, `num_symbols`, `snr_range_db`, `monte_carlo_trials`, `channel_type`, `equalize`, `multipath_taps`, `use_pilots`.

**Commands:** See `docs/RUN_AND_TEST.md`.

---

## Notes
These results reflect an OFDM PHY layer with AWGN and multipath (ZF or MMSE equalization). Multipath uses circular convolution and one-tap ZF/MMSE so BER and EVM improve with SNR. Metrics: BER (`src/receiver.py`) and EVM (`src/evm.py`). Equalizers: `src/equalizers.py` (ZF, MMSE); CLI: `--equalize none|zf|mmse`. **Pilot-based channel estimation** is implemented (`src/pilots.py`); use `--pilots` flag or set `use_pilots=True` in config. Comparison plots (`plot_pilots_comparison.py`) demonstrate the impact of channel estimation errors. Not included: synchronization (CFO, timing), FEC.
