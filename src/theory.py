"""
theory.py

Theoretical Bit Error Rate (BER) expressions for AWGN channel.

Used to validate the OFDM simulator by comparing simulated BER
against closed-form analytical results. References:
- Proakis & Salehi, "Digital Communications", 5th ed.
- Gray-coded QPSK and 16-QAM bit mappings.
"""

import numpy as np
from scipy.special import erfc


def ber_qpsk_awgn(snr_db: np.ndarray) -> np.ndarray:
    """
    Theoretical BER for QPSK in AWGN (Gray mapping).

    BER = (1/2) * erfc(sqrt(Eb/N0)), where Eb/N0 = (Es/N0)/2 for QPSK
    (2 bits per symbol). The simulation uses Es/N0 as SNR, so
    Eb/N0_linear = 10^(snr_db/10) / 2.

    Args:
        snr_db: SNR in dB (Es/N0 in this codebase).

    Returns:
        Theoretical BER array (same shape as snr_db).
    """
    snr_linear = 10.0 ** (np.asarray(snr_db, dtype=float) / 10.0)
    eb_n0_linear = snr_linear / 2.0  # 2 bits per symbol
    return 0.5 * erfc(np.sqrt(eb_n0_linear))


def ber_16qam_awgn(snr_db: np.ndarray) -> np.ndarray:
    """
    Theoretical BER for Gray-coded 16-QAM in AWGN.

    Approximate expression (upper bound): 
    BER ≈ (3/8) * erfc(sqrt(2*Eb/(5*N0))).
    With Es/N0 = SNR and Eb = Es/4: Eb/N0 = SNR/4, so
    argument = sqrt(2*SNR/(20)) = sqrt(SNR/10).

    Args:
        snr_db: SNR in dB (Es/N0).

    Returns:
        Theoretical BER array (same shape as snr_db).
    """
    snr_linear = 10.0 ** (np.asarray(snr_db, dtype=float) / 10.0)
    # 16-QAM Gray: BER ≈ (3/8)*erfc(sqrt(Es/(10*N0))) = (3/8)*erfc(sqrt(SNR/10))
    return (3.0 / 8.0) * erfc(np.sqrt(snr_linear / 10.0))


def theoretical_ber(snr_db: np.ndarray, modulation: str) -> np.ndarray:
    """
    Return theoretical BER for the given modulation and SNR range.

    Args:
        snr_db: SNR values in dB.
        modulation: "QPSK" or "16QAM".

    Returns:
        Theoretical BER array.
    """
    mod = modulation.upper()
    if mod == "QPSK":
        return ber_qpsk_awgn(snr_db)
    if mod == "16QAM":
        return ber_16qam_awgn(snr_db)
    raise ValueError(f"Unsupported modulation: {modulation}")
