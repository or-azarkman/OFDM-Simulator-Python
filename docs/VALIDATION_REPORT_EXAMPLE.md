# Example Validation Report (Simulator)

This is a **template** for what you would attach in a real project (Word/Confluence/PDF). Here we mirror the **machine outputs** from this repo.

---

## Metadata

| Field | Example |
|--------|---------|
| Build / commit | `main` @ `<git_sha>` |
| Config | `configs/validation/test_matrix_default.yaml` |
| Date (UTC) | From JSON `timestamp_utc` |

---

## Summary

| Metric | Result |
|--------|--------|
| Overall | **PASS** or **FAIL** (matrix: all cases must PASS) |
| Cases executed | N (see CSV) |

---

## Per-case results (from CSV)

Columns typically include:

- `case_id` — test name  
- `pass` — True/False  
- `evm_percent`, `ber` — measured  
- `evm_limit_pct`, `evm_margin_pct` — limit and **margin** (limit − measured)  
- `ber_limit`, `ber_margin`  
- `tx_power_db`, `rx_power_db` — mean \|x\|² reported as 10·log10(mean power), ref 1.0 → 0 dB  

**Interpretation:** Negative EVM margin means **failure** for the EVM requirement (measured above limit). Same idea for BER.

---

## Limitations (simulator)

- **No CFO correction** in the current measurement chain — CFO is an impairment only.  
- Power is **average digital baseband power**, not calibrated dBm at antenna.  
- Results depend on `seed`, `num_symbols`, and SNR definition (noise vs. signal power in `awgn_channel`).

---

## Suggested one-liner for interviews

> “I run a YAML-driven validation matrix: each case produces EVM/BER/power, compares to limits with margins, exports CSV/JSON, and fails the job if any case fails — same structure as RF bring-up, in simulation.”
