"""
evm.py

Error Vector Magnitude (EVM) for OFDM quality assessment.

EVM measures the deviation of received constellation points from
their ideal (transmitted) locations, normalized by the reference
signal power. It is commonly reported as a percentage and used
alongside BER to characterize modulation accuracy and channel effects.
"""

import numpy as np


def compute_evm(
    received_symbols: np.ndarray,
    reference_symbols: np.ndarray,
    percent: bool = True,
) -> float:
    """
    Compute RMS Error Vector Magnitude between received and reference symbols.

    EVM_RMS = sqrt( E[|r - t|^2] / E[|t|^2] )
    where r = received, t = reference (transmitted). When percent=True,
    returns 100 * EVM_RMS.

    Args:
        received_symbols: Complex received (e.g. equalized) symbols.
        reference_symbols: Complex reference (transmitted) symbols.
        percent: If True, return EVM as percentage (0–100); else return fraction.

    Returns:
        EVM as percentage or fraction. Returns 0.0 if reference power is zero.
    """
    r = np.asarray(received_symbols, dtype=complex).flatten()
    t = np.asarray(reference_symbols, dtype=complex).flatten()
    if len(r) != len(t):
        raise ValueError(
            f"received_symbols and reference_symbols must have the same length; got {len(r)} and {len(t)}"
        )
    ref_power = np.mean(np.abs(t) ** 2)
    if ref_power <= 0:
        return 0.0
    error_power = np.mean(np.abs(r - t) ** 2)
    evm_rms = np.sqrt(error_power / ref_power)
    return 100.0 * evm_rms if percent else evm_rms
