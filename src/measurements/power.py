"""
Average signal power metrics for complex baseband (normalized reporting).

Uses **mean** power per sample: P = E[|x[n]|²]. Reported in dB relative to 1.0 (linear),
i.e. 10·log10(P), often labeled as **dB (relative)** or **dBFS-style** when the
reference is unity average power.
"""

from __future__ import annotations

import numpy as np


def average_power_linear(signal: np.ndarray) -> float:
    """Mean |x|² over all samples."""
    x = np.asarray(signal, dtype=complex)
    return float(np.mean(np.abs(x) ** 2))


def average_power_db(signal: np.ndarray) -> float:
    """10·log10(mean |x|²); reference 1.0 → 0 dB."""
    p = average_power_linear(signal)
    return float(10.0 * np.log10(p + 1e-30))
