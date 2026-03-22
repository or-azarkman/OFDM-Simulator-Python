# RF Validation & Test Platform — Overview

This document describes the **validation layer** added on top of the existing OFDM PHY simulator. The goal is to move from “how OFDM works” to **“does the modeled transceiver meet stated requirements under impairments?”**

---

## Architecture (target)

```
Transmitter → RF impairments (baseband models) → Channel → Receiver → Measurements → Validation (PASS/FAIL)
```

**Current implementation:**

| Layer | Location | Status |
|--------|-----------|--------|
| RF impairments | `src/rf_impairments/` | CFO (digital phase ramp); composable `RFImpairmentChain` |
| Measurements | `src/measurements/` | `measure_awgn_cfo_once` — EVM, BER, **TX/RX average power (dB ref. unity mean \|x\|²)**; AWGN + optional CFO (no CFO correction yet) |
| Validation | `src/validation/` | YAML thresholds → `evaluate_metrics` / **`evaluate_metrics_with_margins`** → `ValidationReport`; **`load_matrix_cases`** for multi-case YAML |
| Config | `configs/validation/*.yaml` | `default_smoke.yaml` (single scenario); **`test_matrix_default.yaml`** (matrix) |
| Runs | `simulations/validation_runs/` | `run_validation_smoke.py` (JSON); **`run_validation_matrix.py`** (CSV + JSON summary) |
| Docs | `docs/` | **`TEST_PLAN.md`**, **`VALIDATION_REPORT_EXAMPLE.md`** |

**Next (later phases):** pilot-based CFO refinement (optional); phase noise; PA nonlinearity; STO; CI on GitHub Actions (optional). CP CFO estimate is available via **`cfo_correction_mode: cp`**. See **`docs/RF_ROADMAP.md`**.

---

## How to run

**Smoke (single scenario):**

```powershell
py simulations/validation_runs/run_validation_smoke.py
py simulations/validation_runs/run_validation_smoke.py --config configs/validation/default_smoke.yaml
```

**Matrix (multiple cases → CSV):**

```powershell
py simulations/validation_runs/run_validation_matrix.py
py simulations/validation_runs/run_validation_matrix.py --config configs/validation/test_matrix_default.yaml
```

Exit code: **0** = PASS, **1** = FAIL (smoke: one scenario; matrix: **all** cases must pass).  
If the default matrix includes **CFO without RX correction**, a CFO case may fail until correction is added or thresholds/scenario are tuned — see **`docs/TEST_PLAN.md`** (matrix note).

Artifacts:

- Smoke: `results/validation/validation_report_<timestamp>.json` (gitignored pattern for `*.json`)
- Matrix: `results/validation/validation_matrix.csv` + `validation_matrix_summary_<timestamp>.json` (summary JSON gitignored)

---

## YAML formats

### Single scenario (`default_smoke.yaml`)

- **`thresholds`:** `max_evm_percent`, `max_ber`
- **`scenario`:** `fft_size`, `cp_len`, `num_symbols`, `modulation`, `snr_db`, `cfo_subcarrier_fraction`, `seed`

### Matrix (`test_matrix_default.yaml`)

- **`defaults`:** shared `scenario` fields (e.g. `fft_size`, `num_symbols`, `seed`)
- **`defaults_thresholds`:** global limits unless a case overrides
- **`cases`:** list of `{ id, scenario, thresholds }`

CSV columns include measured **EVM/BER**, **limits**, **margins** (limit − measured), and **tx_power_db / rx_power_db**.

---

## Relationship to the legacy simulator

- **`run_simulation.py`** — unchanged educational / portfolio BER+EVM runs.
- **Validation runs** — separate entry points, explicit requirements, PASS/FAIL, tabular output for “validation engineer” storytelling.

---

## Roadmap (short)

1. CFO correction (or pilot-based de-rotation) + before/after metrics  
2. Phase noise & PA (optional)  
3. CI: `pytest` + matrix job on push (optional)  

See `README.md`, `docs/TEST_PLAN.md`, and `docs/next_phase_plan.md`.
