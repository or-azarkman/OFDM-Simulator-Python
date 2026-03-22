# RF impairment roadmap — ordered steps

This file complements `docs/next_phase_plan.md` with a **sequential** checklist for extending the validation harness.

---

## Phase 1 — CFO (complete the story)

| Step | What | Status |
|------|------|--------|
| 1 | CFO **impairment** (`apply_cfo_to_ofdm_stream`) | Done |
| 2 | **Known-CFO removal** (`remove_cfo_from_ofdm_stream`) + YAML flag `cfo_correction: true` | Done |
| 3 | **Estimated CFO** (optional next): CP correlation or pilot-based phase difference between symbols → feed `remove_cfo_from_ofdm_stream` with estimated ε (not oracle) | Planned |
| 4 | Document **limits**: genie = upper bound; estimator = realistic RF test narrative | Ongoing |

**Be ready for step 3:** review CP structure in `src/transmitter.py` / `receiver.py`, and how pilots are placed (`src/pilots.py`).

---

## Phase 2 — Phase noise

| Step | What |
|------|------|
| 1 | Add `apply_phase_noise` (or similar) in `src/rf_impairments/` — Wiener phase on samples or per-OFDM-symbol. |
| 2 | Extend `measure_awgn_cfo_once` (or a new measurement helper) with optional phase noise parameters. |
| 3 | Add YAML cases + thresholds; update `TEST_PLAN.md`. |

**Prerequisite:** math model choice (AWGN phase vs piecewise constant per symbol).

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
