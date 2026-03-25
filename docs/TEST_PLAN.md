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
- **CFO correction** (validation path): `cfo_correction_mode` — `none` / `genie` / `cp` (see matrix note below).
- **Phase noise** (optional): `phase_noise_mode` — `none` / `wiener` / `symbol`, with `phase_noise_std_rad` (meaning depends on mode; see `parse_phase_noise` in `src/measurements/ofdm_metrics.py`). Applied after CFO, before AWGN.
- **Modulation:** QPSK, 16-QAM (existing mod/demod).

**Not yet covered (future):** PA nonlinearity, STO, multipath inside validation matrix (can be added incrementally).

---

## 3. Pass / fail criteria

Defined per case in `configs/validation/*.yaml`:

- `max_evm_percent` — RMS EVM (%) vs **ideal TX** frequency-domain reference (uncorrected CFO increases EVM).
- `max_ber` — bit error rate after hard decisions.

**Global pass:** Smoke = single scenario all checks pass; Matrix = **all** cases pass.

**Matrix note (CFO):** Use **`cfo_correction_mode`** in the scenario:

- **`none`** — no CFO removal (uncorrected CFO can drive BER ~0.5).
- **`genie`** — known CFO (oracle); legacy **`cfo_correction: true`** maps to this.
- **`cp`** — **CP-based CFO estimate** (Moose-style), then inverse ramp (realistic blind sync).

Measured **`cfo_estimated_subcarrier_fraction`** appears in matrix CSV when mode is **`cp`**.

**Matrix note (phase noise):** Optional keys **`phase_noise_mode`** and **`phase_noise_std_rad`**. CSV includes **`phase_noise_mode`** (0/1/2 = none/wiener/symbol) and **`phase_noise_std_rad`**.

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
