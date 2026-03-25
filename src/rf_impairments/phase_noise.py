"""
Phase noise — baseband multiplicative model.

Typical use in OFDM validation:

- **Wiener** (cumulative): φ[n] = φ[n−1] + w[n], w ~ N(0, σ²) — continuous LO phase;
  variance grows with time (non-stationary).
- **Per-OFDM-symbol** (piecewise constant): each symbol multiplied by exp(j φ_k),
  φ_k ~ N(0, σ_φ²) — simple, stationary statistics across symbols.

Both are applied **after** CFO (if any) and **before** AWGN in the measurement chain.
"""

from __future__ import annotations

import numpy as np


def apply_wiener_phase_noise_to_stream(
    signal: np.ndarray,
    sigma_inc_rad: float,
    *,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    Sample-wise Wiener phase noise on the flattened sample order.

    φ[0] = 0, φ[n] = φ[n−1] + w[n], w ~ N(0, σ_inc²). Output y[n] = x[n] * exp(j φ[n]).

    Args:
        signal: Complex baseband (1D or 2D); processed in row-major / C order.
        sigma_inc_rad: Standard deviation of the **phase increment** per sample (radians).
        rng: Optional ``numpy.random.Generator``. If ``None``, uses ``numpy.random``
            (respects ``np.random.seed`` set by the caller).

    Returns:
        Same shape as ``signal``. If ``sigma_inc_rad <= 0``, returns the array
        (view/cast) without adding noise.
    """
    if sigma_inc_rad <= 0.0:
        return np.asarray(signal, dtype=complex)
    x = np.asarray(signal, dtype=np.complex128)
    if x.size == 0:
        return x
    original_shape = x.shape
    flat = x.reshape(-1)
    if rng is not None:
        inc = rng.standard_normal(flat.size, dtype=np.float64) * float(sigma_inc_rad)
    else:
        # Use global RNG so ``np.random.seed`` in callers (e.g. measure_awgn_cfo_once) applies.
        inc = np.random.standard_normal(flat.size).astype(np.float64) * float(sigma_inc_rad)
    phi = np.cumsum(inc)
    return (flat * np.exp(1j * phi)).reshape(original_shape)


def apply_independent_phase_noise_per_ofdm_symbol(
    ofdm_stream: np.ndarray,
    fft_size: int,
    cp_len: int,
    sigma_phi_rad: float,
    *,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """
    One random phase per OFDM symbol (constant over CP + useful part).

    For each symbol row, multiply by exp(j φ_k) with φ_k ~ N(0, σ_φ²).

    Args:
        ofdm_stream: Shape ``(n_symbols, cp_len + fft_size)`` or 1D concatenated symbols.
        fft_size: IFFT size.
        cp_len: Cyclic prefix length.
        sigma_phi_rad: Standard deviation of φ_k (radians).
        rng: Optional ``numpy.random.Generator``; if ``None``, uses ``numpy.random``.

    Returns:
        Same shape as input. If ``sigma_phi_rad <= 0``, returns input as complex array.
    """
    if sigma_phi_rad <= 0.0:
        return np.asarray(ofdm_stream, dtype=complex)
    if fft_size <= 0:
        raise ValueError("fft_size must be positive")
    sym_len = cp_len + fft_size
    x = np.asarray(ofdm_stream, dtype=np.complex128)
    if x.size == 0:
        return x
    original_shape = x.shape
    if x.ndim == 1:
        if x.size % sym_len != 0:
            raise ValueError(
                f"1D stream length {x.size} not divisible by symbol length {sym_len}"
            )
        x = x.reshape(-1, sym_len)
    elif x.ndim == 2:
        if x.shape[1] != sym_len:
            raise ValueError(f"Expected last dim {sym_len}, got shape {x.shape}")
    else:
        raise ValueError("ofdm_stream must be 1D or 2D")

    n_sym = x.shape[0]
    if rng is not None:
        phi = rng.standard_normal(n_sym, dtype=np.float64) * float(sigma_phi_rad)
    else:
        phi = np.random.standard_normal(n_sym).astype(np.float64) * float(sigma_phi_rad)
    rot = np.exp(1j * phi)[:, np.newaxis]
    out = x * rot
    return out.reshape(original_shape)
