# Next Phase Plan — OFDM Simulator

This document tracks what is done and what remains optional for the OFDM simulator. All core steps and the main optional extensions (EVM, Pilots) are **done**.

---

## 0. RF Validation & Test Platform (new direction — `rf-validation-layer`)

**Goal:** Treat the simulator as a **validation harness**: impairments → measurements → requirements (YAML) → **PASS/FAIL** → JSON reports (and later sweeps / CI).

| Item | Status |
|------|--------|
| Package layout: `src/rf_impairments/`, `src/measurements/`, `src/validation/` | **Done** |
| CFO impairment (digital baseband, no correction yet) | **Done** |
| YAML thresholds + smoke runner `run_validation_smoke.py` | **Done** |
| **Test matrix** + CSV + margins + `run_validation_matrix.py` | **Done** |
| **Average power** (dB ref. unity mean \|x\|²) in measurements | **Done** |
| **Test Plan** + example validation report | **`docs/TEST_PLAN.md`**, **`docs/VALIDATION_REPORT_EXAMPLE.md`** |
| Overview | **`docs/VALIDATION_OVERVIEW.md`** |
| Phase noise, PA nonlinearity, noise figure, **CFO correction**, STO | Planned |
| CI (GitHub Actions) running `pytest` + matrix | Optional |
| Merge validation work to `main` (local fast-forward + `git push origin main`) | **Done** (as of merge bringing `1e1bf46` to `main`) |

Legacy OFDM tutorial flow (`run_simulation.py`, BER/EVM plots) remains; validation is an **additional** entry point.

---

## 1. Status confirmation

| Step | Description | Status |
|------|-------------|--------|
| 0 | Branch workflow | Documented |
| **1** | Multipath channel | **Done** |
| **2** | ZF/MMSE equalizer | **Done** |
| **3** | Simulation scripts (--channel, --equalize) | **Done** |
| **4** | Config + docs | **Done** |
| **5** | Lessons learned | **Done** (`docs/lessons_learned.md`) |
| **EVM** | Error Vector Magnitude | **Done** (`src/evm.py`, `results/summary/evm/`) |
| **Pilots** | Pilot-based channel estimation | **Done** (`src/pilots.py`, `results/summary/pilots/`) |

**Step 0 — Branch workflow (Documented):** The project uses Git branches for features (e.g. `feature/pilots`); the workflow is documented here and in the README (clone, branch, run, push). No separate "branch workflow" deliverable is required; the status means the process is defined and ready to use.

**Current state:** Steps 1–5, EVM, and Pilots are complete. **CFO:** impairment + validation integration **done**; **CFO correction** in RX still optional next. **STO** (synchronization); 64‑QAM and FEC remain optional.

---

## 2. Recommended order of work

### Phase A: Step 5 — Lessons learned (**done**)

**Deliverable:** `docs/lessons_learned.md` — technical notes on CP and circular convolution, BER vs spectral efficiency, modulation choice when BER/EVM is too high (step down for wider decision regions), equalization (ZF vs MMSE), validation (BER, EVM, constellations), pilot-based channel estimation. Limitations: ideal sync (no CFO/STO); no FEC. Future: CFO/STO, 64‑QAM, FEC.

---

### Phase B: Optional extensions (by priority)

| Extension | Description | Effort | Impact | Status |
|-----------|-------------|--------|--------|--------|
| **EVM** | Error Vector Magnitude — standard metric (3GPP, Wi-Fi); symbol-level accuracy | Low | High | **Done.** `src/evm.py`; EVM vs SNR per run; comparison plots and table in `results/summary/evm/`. |
| **Pilots** | Pilot subcarriers + LS channel estimation; known vs estimated channel | Medium | High | **Done.** `src/pilots.py`; pattern, insertion, LS estimation; integrated in TX/RX; comparison plots in `results/summary/pilots/`. |
| **CFO** | Carrier frequency offset: **impairment** in validation harness (`apply_cfo_to_ofdm_stream`) — **done**; **correction** in RX (preamble/pilots / de-rotation) — **next** for RF-style sync story. | Medium | High | Impairment **done**; correction **planned**. |
| **STO** | Symbol timing offset + coarse/fine sync (e.g. CP or preamble correlation) | Medium–High | High | Optional. Complements CFO. |
| 64-QAM | Higher-order modulation (QPSK and 16-QAM already in place) | Low | Medium | Optional. |
| FEC | Forward error correction (e.g. convolutional, LDPC) | High | High | Optional; larger scope. |

**Suggested order for extensions (EVM and Pilots are done):**

1. ~~**EVM**~~ — **Done.** EVM vs SNR per run; comparison plots and table in `results/summary/evm/`; `plot_evm_comparison.py`.
2. ~~**Pilots**~~ — **Done.** Pilot pattern (`generate_pilot_pattern`), insertion (`insert_pilots`), LS channel estimation (`estimate_channel_ls`); integrated into transmitter/receiver; tests in `tests/test_pilots.py`.
3. **CFO** — add phase drift per sample (e.g. $$\exp(j \cdot 2\pi \cdot \Delta f \cdot n)$$), then correct (e.g. correlation with known preamble or pilots). Document as sync impairment and correction.
4. **STO** — model delay (shift), then detect/estimate and correct (e.g. correlation with CP or preamble). Document alongside CFO.

EVM and Pilots are done. The project is in a strong state; CFO/STO are optional next steps if you continue.

---

## 3. What to skip or defer

- **Full SDR / real RF:** Out of scope — this repo is baseband simulation only; no RF hardware or SDR.
- **Full FEC chain:** High effort; list as "future work" in Lessons learned unless you add a dedicated FEC step.
- **Too many modulations:** 64-QAM is optional; QPSK + 16-QAM already demonstrate the trade-off.

---

## 4. Summary

- **Status:** Steps 1–5, EVM, and Pilots are complete. Optional next: CFO/STO (synchronization); 64‑QAM and FEC as time allows.
- **Scope:** OFDM baseband transceiver with multipath, ZF/MMSE equalization, pilot-based channel estimation, BER and EVM validation, modulation vs. EVM trade-off (step down to lower-order modulation when BER/EVM is too high). Remaining optional work: CFO, STO.
