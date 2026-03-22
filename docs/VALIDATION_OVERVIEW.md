# RF Validation & Test Platform — Overview

This document describes the **validation layer** added on top of the existing OFDM PHY simulator. The goal is to move from “how OFDM works” to **“does the modeled transceiver meet stated requirements under impairments?”**

---

## Architecture (target)

```
Transmitter → RF impairments (baseband models) → Channel → Receiver → Measurements → Validation (PASS/FAIL)
```

**Current implementation (Phase 1):**

| Layer | Location | Status |
|--------|-----------|--------|
| RF impairments | `src/rf_impairments/` | CFO (digital phase ramp); composable `RFImpairmentChain` |
| Measurements | `src/measurements/` | `measure_awgn_cfo_once` — EVM + BER, AWGN + optional CFO (no CFO correction) |
| Validation | `src/validation/` | YAML thresholds → `evaluate_metrics` → `ValidationReport` |
| Config | `configs/validation/*.yaml` | Example: `default_smoke.yaml` |
| Runs | `simulations/validation_runs/` | `run_validation_smoke.py` → JSON under `results/validation/` |

**Not yet in scope (later phases):** phase noise, PA nonlinearity, noise figure, CFO **correction**, STO, automated multi-case sweeps, formal Test Plan PDFs.

---

## How to run a smoke validation

From project root (Windows):

```powershell
py -m pip install -r requirements.txt
py simulations/validation_runs/run_validation_smoke.py
py simulations/validation_runs/run_validation_smoke.py --config configs/validation/default_smoke.yaml
```

Exit code: **0** = PASS, **1** = FAIL (useful for CI later).

Reports: `results/validation/validation_report_<timestamp>.json`

---

## Configuration format

YAML root keys:

- **`thresholds`:** `max_evm_percent`, `max_ber` (optional; omit or `null` to skip a check)
- **`scenario`:** `fft_size`, `cp_len`, `num_symbols`, `modulation`, `snr_db`, `cfo_subcarrier_fraction`, `seed`

Adjust thresholds after you baseline metrics for your scenario (seed, SNR, CFO).

---

## Relationship to the legacy simulator

- **`run_simulation.py`** — unchanged educational / portfolio BER+EVM runs.
- **Validation runs** — separate entry point, explicit requirements file, PASS/FAIL and JSON artifacts.

---

## Roadmap (short)

1. More impairments (phase noise, AM/AM…) + optional correction blocks  
2. Richer measurements (power, estimated SNR)  
3. Test matrices + CSV summaries + CI  
4. Test Plan / Test Report docs under `docs/`

See also `README.md` (Validation section) and `docs/next_phase_plan.md`.
