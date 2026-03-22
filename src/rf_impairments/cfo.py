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


def remove_cfo_from_ofdm_stream(
    ofdm_stream: np.ndarray,
    fft_size: int,
    cfo_subcarrier_fraction: float,
) -> np.ndarray:
    """
    Remove CFO by applying the **inverse** phase ramp of :func:`apply_cfo_to_ofdm_stream`.

    This is appropriate when the CFO value is **known** (e.g. validation / genie bounds)
    or after an estimator returns ``cfo_subcarrier_fraction``.

    Args:
        ofdm_stream: Same shape conventions as ``apply_cfo_to_ofdm_stream``.
        fft_size: IFFT size (subcarriers).
        cfo_subcarrier_fraction: CFO relative to subcarrier spacing (same sign as applied).

    Returns:
        Time-domain samples with CFO rotation removed (up to numerical noise).
    """
    if fft_size <= 0:
        raise ValueError("fft_size must be positive")
    x = np.asarray(ofdm_stream, dtype=complex)
    if x.size == 0:
        return x

    original_shape = x.shape
    flat = x.reshape(-1)
    n = np.arange(flat.size, dtype=float)
    phase = 2.0 * np.pi * float(cfo_subcarrier_fraction) * n / float(fft_size)
    return (flat * np.exp(-1j * phase)).reshape(original_shape)


def estimate_cfo_subcarrier_fraction_from_cp(
    ofdm_stream: np.ndarray,
    fft_size: int,
    cp_len: int,
) -> float:
    """
    Moose-style CFO estimate from cyclic-prefix self-similarity.

    For each OFDM symbol, the CP is a copy of the last ``cp_len`` samples of the
    useful part. With CFO, the phase difference between CP samples and their
    copies ``fft_size`` samples later is approximately ``2*pi*eps`` (one useful
    interval), so ``eps_hat = angle(R) / (2*pi)`` where ``R`` is the summed
    correlation across CP positions (optionally averaged over symbols).

    Args:
        ofdm_stream: Shape ``(n_symbols, cp_len + fft_size)`` or 1D flattened
            stream of concatenated symbols (same layout as TX).
        fft_size: IFFT size.
        cp_len: Cyclic prefix length (must be > 0).

    Returns:
        Estimated ``cfo_subcarrier_fraction`` (same units as
        :func:`apply_cfo_to_ofdm_stream`).

    Note:
        Phase wraps in ``(-pi, pi]``; large |eps| can alias. Prefer moderate CFO
        for stable estimates.
    """
    if cp_len <= 0:
        raise ValueError("cp_len must be positive for CP-based CFO estimation")
    if fft_size <= 0:
        raise ValueError("fft_size must be positive")

    x = np.asarray(ofdm_stream, dtype=complex)
    sym_len = cp_len + fft_size
    if x.ndim == 1:
        if x.size % sym_len != 0:
            raise ValueError(
                f"1D stream length {x.size} not divisible by symbol length {sym_len}"
            )
        x = x.reshape(-1, sym_len)
    elif x.ndim == 2:
        if x.shape[1] != sym_len:
            raise ValueError(
                f"Expected last dim {sym_len}, got shape {x.shape}"
            )
    else:
        raise ValueError("ofdm_stream must be 1D or 2D")

    acc = 0.0j
    for row in x:
        acc += np.sum(row[0:cp_len] * np.conj(row[fft_size : fft_size + cp_len]))

    phi = float(np.angle(acc))
    return phi / (2.0 * np.pi)
