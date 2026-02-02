# Next Phase Plan — OFDM Simulator

## 1. Status confirmation

| Step | Description | Status |
|------|-------------|--------|
| 0 | Branch workflow | Ready (documented) |
| **1** | Multipath channel | **Done** |
| **2** | ZF/MMSE equalizer | **Done** |
| **3** | Simulation scripts (--channel, --equalize) | **Done** |
| **4** | Config + docs | **Done** |
| **5** | Lessons learned | **Done** (`docs/LESSONS_LEARNED.md`) |

Steps 1–5 are complete. **EVM** (Phase B) is implemented. Remaining Phase B: pilots, CFO, STO as in the table below.

---

## 2. Recommended order of work

### Phase A: Step 5 — Lessons learned (**done**)

**Goal:** One short document that shows engineering reflection. No new code; strengthens the narrative for interviews.

**Deliverable:** `docs/LESSONS_LEARNED.md` — created. Contains:

- **Lessons learned:** e.g. CP and circular convolution, BER vs spectral efficiency trade-off, why equalization matters in multipath, ZF vs MMSE (noise amplification at nulls vs noise-aware).
- **Limitations:** e.g. ideal sync (no CFO/STO), known channel (no pilot-based estimation), no FEC.
- **Future improvements:** Short list (e.g. EVM, pilots, CFO/STO, 64-QAM, FEC).

**Effort:** Low. **Impact:** High for an interviewer (shows maturity and self-awareness).

---

### Phase B: Optional extensions (by priority and fit)

| Extension | What it is | Fit for “grad, no experience” | Effort | Impact | Recommendation |
|-----------|------------|--------------------------------|--------|--------|----------------|
| **EVM** | Error Vector Magnitude — standard metric (3GPP, Wi-Fi) | Very good | Low | High | **Done.** Implemented in `src/evm.py`; EVM vs SNR per run; comparison plots and table in `results/summary/`. |
| **Pilots** | Pilot subcarriers + simple channel estimation | Very good | Medium | High | **Strong second.** Moves from “known channel” to “estimated channel”; very relevant to real systems. |
| **CFO** | Carrier frequency offset + correction (e.g. phase rotation, correction loop) | Good | Medium | High | **Good third.** Clearly shows understanding of real-world impairments. |
| **STO** | Symbol timing offset + coarse/fine sync | Good | Medium–High | High | **Good fourth.** Complements CFO; both are “synchronization” story. |
| 64-QAM | Add modulation (you already have 16-QAM) | Nice to have | Low | Medium | Optional. |
| FEC | Forward error correction (e.g. convolutional code) | Nice to have | High | High | Optional; larger scope. |

**Suggested order for extensions:**

1. ~~**EVM**~~ — **Done.** EVM vs SNR per run; comparison plots (AWGN vs Multipath, ZF vs MMSE, all scenarios) and table in `results/summary/`; `plot_evm_comparison.py`.
2. **Pilots** — insert pilots in frequency grid, estimate channel from pilots (e.g. LS), use estimated H in ZF/MMSE. Enables “unknown channel” scenario.
3. **CFO** — add phase drift per sample (e.g. $$\exp(j \cdot 2\pi \cdot \Delta f \cdot n)$$), then correct (e.g. correlation with known preamble or pilots). Document as “sync impairment + correction.”
4. **STO** — model delay (shift), then detect/estimate and correct (e.g. correlation with CP or preamble). Document alongside CFO.

Do not feel obliged to implement all of them; **EVM + Lessons learned** alone already raise the bar. Pilots + one of CFO/STO would make the project stand out clearly.

---

## 3. Concrete next steps (action list)

1. **Step 5 done:** `docs/LESSONS_LEARNED.md` — lessons learned, limitations, future work (EVM, pilots, CFO, STO).

2. **Optional — EVM:**  
   - Add `src/evm.py`: e.g. `compute_evm(received_symbols, transmitted_symbols)` (per symbol or average).  
   - In simulation: compute EVM per SNR (and per scenario if desired).  
   - Plot EVM vs SNR (and add to `results/summary/` if you want).  
   - Mention in README and `ofdm_overview.md`.

3. **Optional — Pilots / CFO / STO:**  
   - Plan in small steps (e.g. pilots first, then CFO or STO).  
   - Keep existing tests passing; add tests for new functions.  
   - Update this doc with progress when you start.

---

## 4. What to skip or defer

- **Full SDR / real RF:** Out of scope — this repo is baseband simulation only; no RF hardware or SDR.
- **Full FEC chain:** High effort; list as “future work” in Lessons learned unless you add a dedicated FEC step.
- **Too many modulations:** 64-QAM is optional; QPSK + 16-QAM already demonstrate the trade-off.

---

## 5. Summary

- **Status:** Steps 1–5 complete. Next: Phase B optional extensions — EVM first, then pilots, then CFO/STO as time allows.
- **Interview narrative:** “I built an OFDM sim with multipath and equalization, validated with BER and constellations, wrote lessons learned, and plan to add EVM / pilots / sync as next steps.” Strong, coherent story for a grad with no industry experience.
