"""
Carrier Frequency Offset (CFO) — baseband digital model.

Applies a cumulative phase rotation to each time-domain sample:
    y[n] = x[n] * exp(j * 2*pi * eps * n / N_fft)

where ``eps`` is the CFO expressed as a **fraction of one subcarrier spacing**
(Δf / Δf_sub), and ``N_fft`` is the IFFT size. This matches the common OFDM
normalization where adjacent subcarriers are spaced by 1/N in normalized frequency.
"""

from __future__ import annotations

import numpy as np


def apply_cfo_to_ofdm_stream(
    ofdm_stream: np.ndarray,
    fft_size: int,
    cfo_subcarrier_fraction: float,
) -> np.ndarray:
    """
    Apply CFO to a stream of OFDM symbols (with cyclic prefix).

    Args:
        ofdm_stream: Shape (n_symbols, cp_len + fft_size) or 1D length n*(cp+fft).
        fft_size: Number of subcarriers (IFFT size).
        cfo_subcarrier_fraction: CFO relative to subcarrier spacing, e.g. 0.02 = 2%.

    Returns:
        Same shape as input, with CFO applied sample-by-sample in order across
        the full stream (phase is continuous across symbols).
    """
    if fft_size <= 0:
        raise ValueError("fft_size must be positive")
    x = np.asarray(ofdm_stream, dtype=complex)
    if x.size == 0:
        return x

    original_shape = x.shape
    flat = x.reshape(-1)
    n = np.arange(flat.size, dtype=float)
    # Phase increment per sample: 2*pi * eps / N (one subcarrier spacing = 1/N)
    phase = 2.0 * np.pi * float(cfo_subcarrier_fraction) * n / float(fft_size)
    return (flat * np.exp(1j * phase)).reshape(original_shape)
