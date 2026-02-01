# Next Phase Plan — OFDM Simulator

## 1. Status confirmation (IMPLEMENTATION_PLAN.md)

| Step | Description | Status |
|------|-------------|--------|
| 0 | Branch workflow | Ready (documented) |
| **1** | Multipath channel | **Done** |
| **2** | ZF/MMSE equalizer | **Done** |
| **3** | Simulation scripts (--channel, --equalize) | **Done** |
| **4** | Config + docs | **Done** |
| **5** | Lessons learned | **Not done** |

**You are correct:** steps 1, 2, and 3 (and 4) are complete. The only remaining item from the original plan is **Step 5: Lessons learned**.

---

## 2. Recommended order of work

### Phase A: Step 5 — Lessons learned (quick win, high impact)

**Goal:** One short document that shows engineering reflection. No new code; strengthens the narrative for interviews.

**Deliverable:** `docs/LESSONS_LEARNED.md` (or a section in README) with:

- **Lessons learned:** e.g. CP and circular convolution, BER vs spectral efficiency trade-off, why equalization matters in multipath, ZF vs MMSE (noise amplification at nulls vs noise-aware).
- **Limitations:** e.g. ideal sync (no CFO/STO), known channel (no pilot-based estimation), no FEC.
- **Future improvements:** Short list (e.g. EVM, pilots, CFO/STO, 64-QAM, FEC).

**Effort:** Low. **Impact:** High for an interviewer (shows maturity and self-awareness).

---

### Phase B: Optional extensions (by priority and fit)

| Extension | What it is | Fit for “grad, no experience” | Effort | Impact | Recommendation |
|-----------|------------|--------------------------------|--------|--------|----------------|
| **EVM** | Error Vector Magnitude — standard metric (3GPP, Wi-Fi) | Very good | Low | High | **Do first.** Easy to add from existing symbols; shows you know industry metrics. |
| **Pilots** | Pilot subcarriers + simple channel estimation | Very good | Medium | High | **Strong second.** Moves from “known channel” to “estimated channel”; very relevant to real systems. |
| **CFO** | Carrier frequency offset + correction (e.g. phase rotation, correction loop) | Good | Medium | High | **Good third.** Clearly shows understanding of real-world impairments. |
| **STO** | Symbol timing offset + coarse/fine sync | Good | Medium–High | High | **Good fourth.** Complements CFO; both are “synchronization” story. |
| 64-QAM | Add modulation (you already have 16-QAM) | Nice to have | Low | Medium | Optional. |
| FEC | Forward error correction (e.g. convolutional code) | Nice to have | High | High | Optional; larger scope. |

**Suggested order for extensions:**

1. **EVM** — compute and plot EVM vs SNR (and optionally vs scenario: AWGN, multipath, ZF, MMSE). Add to `results/summary/` and docs.
2. **Pilots** — insert pilots in frequency grid, estimate channel from pilots (e.g. LS), use estimated H in ZF/MMSE. Enables “unknown channel” scenario.
3. **CFO** — add phase drift per sample (e.g. `exp(j*2*pi*delta_f*n)`), then correct (e.g. correlation with known preamble or pilots). Document as “sync impairment + correction.”
4. **STO** — model delay (shift), then detect/estimate and correct (e.g. correlation with CP or preamble). Document alongside CFO.

Do not feel obliged to implement all of them; **EVM + Lessons learned** alone already raise the bar. Pilots + one of CFO/STO would make the project stand out clearly.

---

## 3. Concrete next steps (action list)

1. **Create `docs/LESSONS_LEARNED.md`** (Step 5).  
   - Branch: e.g. `feature/docs-lessons-learned` or commit on current branch.  
   - Content: lessons learned, limitations, future work (including EVM, pilots, CFO, STO).

2. **Optional — EVM:**  
   - Add `src/evm.py`: e.g. `compute_evm(received_symbols, transmitted_symbols)` (per symbol or average).  
   - In simulation: compute EVM per SNR (and per scenario if desired).  
   - Plot EVM vs SNR (and add to `results/summary/` if you want).  
   - Mention in README and `ofdm_overview.md`.

3. **Optional — Pilots / CFO / STO:**  
   - Plan in small steps (e.g. pilots first, then CFO or STO).  
   - Keep existing tests passing; add tests for new functions.  
   - Update IMPLEMENTATION_PLAN.md (or this doc) with “Phase C” when you start.

---

## 4. What to skip or defer

- **Full SDR / real RF:** Out of scope for this repo; keep it baseband simulation.
- **Full FEC chain:** High effort; mention as “future work” in Lessons learned unless you want a dedicated FEC step later.
- **Too many modulations:** 64-QAM is optional; QPSK + 16-QAM is enough to show understanding.

---

## 5. Summary

- **Confirmed:** Steps 1–4 done; only Step 5 (Lessons learned) is left from the original plan.
- **Next:** Do Step 5 (LESSONS_LEARNED.md). Then, if you want to extend: EVM first, then pilots, then CFO/STO as time allows.
- **Interview narrative:** “I built an OFDM sim with multipath and equalization, validated with BER and constellations, then reflected on limitations and added EVM / pilots / sync as next steps.” That is a strong, coherent story for a grad with no industry experience.
