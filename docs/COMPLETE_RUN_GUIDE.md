# Complete Run Guide — All Simulations and Plots

This document provides a comprehensive checklist of all simulations and plots needed for a complete OFDM project demonstration. For mathematical foundations, modulation and EVM trade-offs, and engineering conclusions (e.g. when to step down to lower-order modulation for better EVM), see `docs/ofdm_overview.md` and `docs/LESSONS_LEARNED.md`.

---

## Prerequisites

**Install dependencies:**
```powershell
py -m pip install -r requirements.txt
```

**Run tests first:**
```powershell
py -m pytest tests/ -v
```

---

## Step 1: Base Simulations (Required)

Run these simulations to generate baseline results:

### AWGN Channel
```powershell
py run_simulation.py --symbols 5000
```
**Outputs:** `results/5000_symbols/`
- BER vs SNR plots (QPSK, 16-QAM)
- EVM vs SNR plots (QPSK, 16-QAM)
- Constellation diagrams (0, 10, 20 dB)
- CSV files (BER, EVM)

### Multipath Channel — No Equalizer
```powershell
py run_simulation.py --channel multipath --equalize none --symbols 5000
```
**Outputs:** `results/5000_symbols_multipath/`
- BER vs SNR plots (shows error floor)
- EVM vs SNR plots
- Constellation diagrams (shows distortion)
- Channel response plots (CIR, CFR)
- CSV files

### Multipath Channel — ZF Equalizer
```powershell
py run_simulation.py --channel multipath --equalize zf --symbols 5000
```
**Outputs:** `results/5000_symbols_multipath_zf/`
- BER vs SNR plots (improved performance)
- EVM vs SNR plots
- Constellation diagrams (restored clusters)
- Channel response plots
- CSV files

### Multipath Channel — MMSE Equalizer
```powershell
py run_simulation.py --channel multipath --equalize mmse --symbols 5000
```
**Outputs:** `results/5000_symbols_multipath_mmse/`
- BER vs SNR plots (best performance at low SNR)
- EVM vs SNR plots
- Constellation diagrams
- Channel response plots
- CSV files

---

## Step 2: Pilot-Based Channel Estimation (Required)

Run these simulations to demonstrate channel estimation from pilots:

### Multipath with Pilots — ZF Equalizer
```powershell
py run_simulation.py --channel multipath --equalize zf --pilots --symbols 5000
```
**Outputs:** `results/5000_symbols_multipath_zf_pilots/`
- BER vs SNR plots (with estimated channel)
- EVM vs SNR plots (with estimated channel)
- Constellation diagrams (with estimated channel)
- CSV files

### Multipath with Pilots — MMSE Equalizer
```powershell
py run_simulation.py --channel multipath --equalize mmse --pilots --symbols 5000
```
**Outputs:** `results/5000_symbols_multipath_mmse_pilots/`
- BER vs SNR plots (with estimated channel)
- EVM vs SNR plots (with estimated channel)
- Constellation diagrams (with estimated channel)
- CSV files

---

## Step 3: Comparison Plots (Required)

Generate summary comparison plots:

### BER Comparison
```powershell
py simulations/plot_ber_comparison.py
```
**Outputs in `results/summary/ber/`:**
- `ber_comparison_awgn_vs_multipath_5000symbols.png` — AWGN vs Multipath (ZF)
- `ber_500_vs_5000_multipath_qpsk.png` — Monte Carlo convergence (QPSK)
- `ber_500_vs_5000_multipath_16qam.png` — Monte Carlo convergence (16-QAM)
- `ber_comparison_zf_vs_mmse_5000symbols.png` — ZF vs MMSE comparison
- `comparison_table.csv` — BER table (all scenarios)
- `comparison_table.md` — BER table (Markdown format)
- `comparison_table_readable.txt` — BER table (plain text)

### EVM Comparison
```powershell
py simulations/plot_evm_comparison.py
```
**Outputs in `results/summary/evm/`:**
- `evm_comparison_awgn_vs_multipath_5000symbols.png` — AWGN vs Multipath
- `evm_comparison_zf_vs_mmse_5000symbols.png` — ZF vs MMSE comparison
- `evm_comparison_all_scenarios_qpsk_5000symbols.png` — All scenarios (QPSK)
- `evm_comparison_all_scenarios_16qam_5000symbols.png` — All scenarios (16-QAM)
- `evm_comparison_table.csv` — EVM table (all scenarios)
- `evm_comparison_table.md` — EVM table (Markdown format)

### Constellation Comparison
```powershell
py simulations/plot_constellation_comparison.py
```
**Outputs in `results/summary/constellation/`:**
- `constellation_comparison_QPSK.png` — 4×3 grid (AWGN, Multipath no eq, ZF, MMSE × 0/10/20 dB)
- `constellation_comparison_16QAM.png` — 4×3 grid (same scenarios)

### Pilot-Based Channel Estimation Comparison
```powershell
py simulations/plot_pilots_comparison.py --symbols 5000 --equalize zf
py simulations/plot_pilots_comparison.py --symbols 5000 --equalize mmse
```
**Outputs in `results/summary/pilots/`:**
- `channel_estimation_accuracy_5000symbols_snr20.0dB.png` — 4 subplots:
  - Channel magnitude: True |H| vs Estimated |H|
  - Channel phase: True ∠H vs Estimated ∠H
  - MSE per subcarrier
  - Error distribution
- `ber_comparison_pilots_5000symbols_zf.png` — BER: Known channel vs Pilot-based (QPSK + 16-QAM)
- `ber_comparison_pilots_5000symbols_mmse.png` — Same for MMSE
- `evm_comparison_pilots_5000symbols_zf.png` — EVM: Known channel vs Pilot-based (QPSK + 16-QAM)
- `evm_comparison_pilots_5000symbols_mmse.png` — Same for MMSE
- `constellation_pilots_comparison_5000symbols_zf_snr20.0dB.png` — Constellation: Known vs Pilot-based
- `constellation_pilots_comparison_5000symbols_mmse_snr20.0dB.png` — Same for MMSE

---

## Complete Checklist

### Simulations (Step 1 + 2)
- [ ] AWGN: `py run_simulation.py --symbols 5000`
- [ ] Multipath (no eq): `py run_simulation.py --channel multipath --equalize none --symbols 5000`
- [ ] Multipath (ZF): `py run_simulation.py --channel multipath --equalize zf --symbols 5000`
- [ ] Multipath (MMSE): `py run_simulation.py --channel multipath --equalize mmse --symbols 5000`
- [ ] Multipath + Pilots (ZF): `py run_simulation.py --channel multipath --equalize zf --pilots --symbols 5000`
- [ ] Multipath + Pilots (MMSE): `py run_simulation.py --channel multipath --equalize mmse --pilots --symbols 5000`

### Comparison Plots (Step 3)
- [ ] BER comparison: `py simulations/plot_ber_comparison.py`
- [ ] EVM comparison: `py simulations/plot_evm_comparison.py`
- [ ] Constellation comparison: `py simulations/plot_constellation_comparison.py`
- [ ] Pilots comparison (ZF): `py simulations/plot_pilots_comparison.py --symbols 5000 --equalize zf`
- [ ] Pilots comparison (MMSE): `py simulations/plot_pilots_comparison.py --symbols 5000 --equalize mmse`

### Expected Output Files

**In `results/summary/` (organized by metric type):**
- `ber/` — BER comparison plots and tables (4 plots + 3 tables)
- `evm/` — EVM comparison plots and tables (4 plots + 2 tables)
- `constellation/` — Constellation comparison plots (2 plots)
- `pilots/` — Pilot-based channel estimation comparison (8 plots: 4 per equalizer)
- `docs/` — Summary documentation files

**In `results/<N>_symbols*/images/` (per-run outputs):**
- `ber_vs_snr_*.png` — BER plots per run
- `evm_vs_snr_*.png` — EVM plots per run
- `constellation_*.png` — Constellation plots per run
- `channel_response_*.png` — Channel response (multipath only)

---

## Quick Run (Faster, Less Accurate)

For quick testing, use `--symbols 500 --trials 20`:

```powershell
py run_simulation.py --symbols 500 --trials 20
py run_simulation.py --channel multipath --equalize zf --symbols 500 --trials 20
py run_simulation.py --channel multipath --equalize zf --pilots --symbols 500 --trials 20
py simulations/plot_pilots_comparison.py --symbols 500 --trials 20 --equalize zf
```

---

## Summary

After completing all steps, you will have:
- **6 simulation runs** (AWGN, Multipath no eq/ZF/MMSE, Multipath ZF/MMSE with pilots)
- **Summary outputs** in `results/summary/` organized by metric:
  - `ber/` — 4 BER comparison plots + 3 tables
  - `evm/` — 4 EVM comparison plots + 2 tables
  - `constellation/` — 2 constellation grids
  - `pilots/` — 8 pilot-specific plots (4 per equalizer: channel estimation accuracy, BER/EVM/Constellation comparisons)
  - `docs/` — Summary documentation
- **Per-run outputs** in `results/<N>_symbols*/images/` — BER, EVM, constellation, channel response plots
- **Complete CSV data** for all scenarios
- **Professional documentation** demonstrating the full OFDM system with channel estimation

**Total:** Multiple plots and data files per run and in summary (see Expected Output Files above for the full list).

**Note:** To organize existing files in `results/summary/`, run: `py results/summary/ORGANIZE_EXISTING.py`

This provides a comprehensive demonstration of OFDM system performance, equalization techniques, and pilot-based channel estimation.
