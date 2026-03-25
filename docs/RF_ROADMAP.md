# RF impairment roadmap — ordered steps

This file complements `docs/next_phase_plan.md` with a **sequential** checklist for extending the validation harness.

---

## Phase 1 — CFO (complete the story)

| Step | What | Status |
|------|------|--------|
| 1 | CFO **impairment** (`apply_cfo_to_ofdm_stream`) | Done |
| 2 | **Known-CFO removal** (`remove_cfo_from_ofdm_stream`) + YAML `cfo_correction_mode: genie` (legacy: `cfo_correction: true`) | Done |
| 3 | **CP-based CFO estimate** (`estimate_cfo_subcarrier_fraction_from_cp`) + YAML `cfo_correction_mode: cp` | Done |
| 4 | Pilot-based CFO / residual tracking (optional refinement) | Planned |
| 5 | Document **limits**: genie = upper bound; CP estimate = blind sync narrative | Ongoing |

**Next:** pilot-based CFO refinement (optional) — see `src/pilots.py` and CP structure in `src/transmitter.py` / `receiver.py`.

---

## Phase 2 — Phase noise

| Step | What | Status |
|------|------|--------|
| 1 | `apply_wiener_phase_noise_to_stream` + `apply_independent_phase_noise_per_ofdm_symbol` in `src/rf_impairments/phase_noise.py` | Done |
| 2 | `measure_awgn_cfo_once` + `parse_phase_noise` (`phase_noise_mode`, `phase_noise_std_rad`) | Done |
| 3 | Matrix YAML + `TEST_PLAN.md`; smoke/matrix runners pass phase-noise keys through | Done |

**Models:** **Wiener** (increment σ per sample, continuous phase on flat stream) vs **symbol** (one φ_k per OFDM symbol). Order: CFO → phase noise → AWGN. **No RX phase tracking** in harness (EVM vs ideal TX ref — phase noise shows up as rotation error).

---

## Phase 3 — Time sync (STO / timing)

| Step | What |
|------|------|
| 1 | Model **integer sample shift** (misaligned CP removal) or fractional via interpolation (simpler: integer first). |
| 2 | **Detection**: CP autocorrelation peak (Schmidl–Cox style) or energy detector — educational scope. |
| 3 | Wire “best CP offset” into `remove_cyclic_prefix` path in measurements. |

**Prerequisite:** clear CP length and symbol boundaries in `generate_ofdm_stream` output.

---

## Phase 4 — PA / nonlinearity (optional)

- AM/AM, AM/PM or memoryless polynomial; validate EVM/ACPR-style metrics if needed.

---

## Phase 5 — Automation

- GitHub Actions: `py -m pytest` on push/PR; optional nightly `run_validation_matrix.py` (artifact upload).

---

## How to stay “ready” between phases

1. After each feature: **`py -m pytest`**, **`run_validation_smoke.py`**, **`run_validation_matrix.py`** (exit 0).  
2. Keep **YAML** as the contract: new knobs → document in `docs/TEST_PLAN.md`.  
3. Prefer **one PR per phase** (CFO estimate → phase noise → STO) for clean history.
