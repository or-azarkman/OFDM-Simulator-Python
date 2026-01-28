# OFDM Simulation – Results Summary

## Simulation Configuration
The OFDM system was evaluated under identical conditions using two different simulation lengths in order to assess performance stability and modulation sensitivity.

**Common parameters:**
- Modulation schemes: QPSK, 16-QAM (Gray-coded)
- Channel model: AWGN (complex baseband)
- Receiver: Ideal synchronization (no CFO / timing offset)
- Evaluation metric: Bit Error Rate (BER)

**Simulation lengths:**
- 500 OFDM symbols
- 5000 OFDM symbols

---

## Constellation Analysis

### QPSK
- Constellation points remain well separated under AWGN.
- Even at moderate SNR values, symbol clustering is tight.
- Decision regions are robust, resulting in low BER.

### 16-QAM
- Higher constellation density leads to increased sensitivity to noise.
- At lower SNRs, visible symbol spreading causes decision ambiguity.
- Requires higher SNR to achieve BER comparable to QPSK.

Increasing the number of OFDM symbols significantly improves constellation stability and reduces visual noise dispersion.

---

## BER Performance Comparison

| Modulation | Noise Robustness | Spectral Efficiency | BER Stability |
|-----------|------------------|---------------------|---------------|
| QPSK      | High             | Low                 | Very Stable   |
| 16-QAM    | Moderate         | High                | SNR Dependent |

Key observations:
- QPSK consistently achieves lower BER at a given SNR.
- 16-QAM shows higher BER variance, especially with fewer symbols.
- BER curves become smoother and more reliable when using 5000 symbols compared to 500 symbols.

---

## Impact of Number of Symbols
- **500 symbols**:  
  - Faster simulation  
  - Higher statistical variance in BER  
  - Suitable for quick validation and debugging

- **5000 symbols**:  
  - More accurate BER estimation  
  - Reduced randomness effects  
  - Preferred for performance evaluation and comparison

---

## Engineering Conclusions
- There is a clear trade-off between **spectral efficiency** and **noise robustness**.
- QPSK is suitable for low-SNR or reliability-critical links.
- 16-QAM provides higher throughput but demands better channel conditions.
- Increasing the number of simulated symbols is essential for reliable BER analysis.

---

## Notes
These results reflect an ideal OFDM PHY layer without synchronization errors, fading, or channel estimation imperfections.  
Future simulations should include multipath channels and synchronization impairments to approach real-world behavior.
