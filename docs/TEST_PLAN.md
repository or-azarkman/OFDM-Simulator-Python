# Test Plan — OFDM PHY Validation Harness (Simulator)

**Scope:** Baseband OFDM transceiver **simulation** with RF-style impairments modeled digitally, plus **requirement-based** PASS/FAIL checks suitable for portfolio / interview discussion.

**Out of scope:** Real hardware, lab instruments, regulatory certification.

---

## 1. Objectives

| ID | Objective |
|----|-----------|
| O1 | Demonstrate **repeatable** validation runs from **config files** (YAML). |
| O2 | Report **EVM**, **BER**, and **average power** (dB relative to unity mean \|x\|²). |
| O3 | Compare measurements to **limits** with **margins** and overall **PASS/FAIL**. |
| O4 | Support **multiple test cases** (matrix) in one run with CSV output. |

---

## 2. Features under test (current)

- **AWGN** channel after TX (existing `awgn_channel`).
- **CFO** impairment: digital phase ramp on time-domain samples (`apply_cfo_to_ofdm_stream`).
- **Modulation:** QPSK, 16-QAM (existing mod/demod).

**Not yet covered (future):** CFO correction, phase noise, PA nonlinearity, STO, multipath inside validation matrix (can be added incrementally).

---

## 3. Pass / fail criteria

Defined per case in `configs/validation/*.yaml`:

- `max_evm_percent` — RMS EVM (%) vs **ideal TX** frequency-domain reference (uncorrected CFO increases EVM).
- `max_ber` — bit error rate after hard decisions.

**Global pass:** Smoke = single scenario all checks pass; Matrix = **all** cases pass.

**Matrix note (CFO):** Set **`cfo_correction: true`** in the scenario to apply **known-CFO** inverse phase ramp (genie / oracle) before FFT/demod — suitable for validation bounds and for a **PASS** on the default `cfo_mild_qpsk` case. With **`cfo_correction: false`** (or omitted), CFO is **not** removed; EVM can be very high and BER can approach **0.5**. A future step is **estimated** CFO (CP/pilots) instead of oracle.

---

## 4. Test execution

| Run | Command |
|-----|---------|
| Unit tests | `py -m pytest tests/ -v` |
| Smoke validation | `py simulations/validation_runs/run_validation_smoke.py` |
| Validation matrix | `py simulations/validation_runs/run_validation_matrix.py` |

On **Windows**, prefer the **`py`** launcher (`py -m pytest`, `py simulations/...`) if `python` / `pytest` are not on `PATH`.

**Artifacts:** CSV under `results/validation/` (matrix); JSON summaries may be gitignored — regenerate anytime.

---

## 5. Maintenance

- After changing impairments or demodulation, **re-baseline** YAML limits using measured columns + margin review.
- Keep at least one **loose** regression case in tests (`tests/test_validation_matrix_config.py`) so CI catches API breakage, not tuning noise.

---

*Version: aligned with repo `docs/VALIDATION_OVERVIEW.md` and `README.md`.*
