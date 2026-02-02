"""
pilots.py

Pilot subcarriers and channel estimation for OFDM systems.

Pilots are known symbols inserted at specific subcarrier positions
to enable channel estimation at the receiver. This module provides:
- Pilot pattern generation (which subcarriers carry pilots)
- Pilot symbol insertion into frequency-domain frames
- Least Squares (LS) channel estimation from received pilots
"""

import numpy as np
from typing import Optional, Sequence, Union


def generate_pilot_pattern(
    fft_size: int,
    pilot_spacing: int = 8,
    num_pilots: Optional[int] = None,
) -> np.ndarray:
    """
    Generate pilot subcarrier indices.

    Pilots are evenly spaced across the frequency grid. Common patterns:
    - Every Nth subcarrier (e.g., every 8th for fft_size=64 → 8 pilots)
    - Or specify exact number of pilots

    Args:
        fft_size: Total number of subcarriers.
        pilot_spacing: Spacing between pilots (e.g., 8 means pilots at 0, 8, 16, ...).
        num_pilots: If specified, use this many evenly-spaced pilots instead of spacing.

    Returns:
        Array of pilot subcarrier indices (sorted, 0-indexed).
    """
    if num_pilots is not None:
        if num_pilots > fft_size:
            raise ValueError(f"num_pilots ({num_pilots}) cannot exceed fft_size ({fft_size})")
        indices = np.linspace(0, fft_size - 1, num_pilots, dtype=int)
    else:
        indices = np.arange(0, fft_size, pilot_spacing, dtype=int)
    return np.unique(indices)


def generate_pilot_symbols(num_pilots: int, pilot_value: complex = 1.0 + 0j) -> np.ndarray:
    """
    Generate pilot symbols (known values transmitted on pilot subcarriers).

    Args:
        num_pilots: Number of pilot symbols needed.
        pilot_value: Complex value for all pilots (default: 1+0j, unit amplitude).

    Returns:
        Array of pilot symbols (all equal to pilot_value).
    """
    return np.full(num_pilots, pilot_value, dtype=complex)


def insert_pilots(
    data_symbols: np.ndarray,
    pilot_indices: np.ndarray,
    pilot_symbols: np.ndarray,
    fft_size: int,
) -> np.ndarray:
    """
    Insert pilot symbols into frequency-domain frame at specified indices.

    Args:
        data_symbols: Data symbols to place on non-pilot subcarriers.
        pilot_indices: Subcarrier indices where pilots are placed.
        pilot_symbols: Pilot symbol values (length must match pilot_indices).
        fft_size: Total FFT size.

    Returns:
        Frequency-domain frame with pilots inserted.
    """
    if len(pilot_symbols) != len(pilot_indices):
        raise ValueError(
            f"pilot_symbols length ({len(pilot_symbols)}) must match pilot_indices ({len(pilot_indices)})"
        )
    if np.any(pilot_indices >= fft_size) or np.any(pilot_indices < 0):
        raise ValueError(f"pilot_indices must be in range [0, {fft_size})")
    
    num_data_subcarriers = fft_size - len(pilot_indices)
    if len(data_symbols) != num_data_subcarriers:
        raise ValueError(
            f"data_symbols length ({len(data_symbols)}) must equal num_data_subcarriers ({num_data_subcarriers})"
        )
    
    frame = np.zeros(fft_size, dtype=complex)
    pilot_set = set(pilot_indices)
    data_idx = 0
    
    for k in range(fft_size):
        if k in pilot_set:
            pilot_pos = np.where(pilot_indices == k)[0][0]
            frame[k] = pilot_symbols[pilot_pos]
        else:
            frame[k] = data_symbols[data_idx]
            data_idx += 1
    
    return frame


def extract_pilots(
    freq_frame: np.ndarray,
    pilot_indices: np.ndarray,
) -> np.ndarray:
    """
    Extract pilot symbols from received frequency-domain frame.

    Args:
        freq_frame: Received frequency-domain symbols (1D: length = fft_size, or 2D: [num_symbols, fft_size]).
        pilot_indices: Subcarrier indices where pilots are located.

    Returns:
        Array of received pilot symbols (1D: [num_pilots]).
        For 2D input, returns average over symbols for better channel estimation (channel is constant across symbols).
    """
    freq_frame = np.asarray(freq_frame)
    if freq_frame.ndim == 1:
        return freq_frame[pilot_indices]
    elif freq_frame.ndim == 2:
        # For 2D input (multiple symbols), average pilots across symbols for better channel estimation
        return np.mean(freq_frame[:, pilot_indices], axis=0)
    else:
        raise ValueError(f"freq_frame must be 1D or 2D, got {freq_frame.ndim}D")


def estimate_channel_ls(
    received_pilots: np.ndarray,
    transmitted_pilots: np.ndarray,
    pilot_indices: np.ndarray,
    fft_size: int,
    interpolation: str = "linear",
) -> np.ndarray:
    """
    Estimate channel frequency response using Least Squares (LS) from pilots.

    LS estimate: H_est[k] = Y_pilot[k] / X_pilot[k] for pilot subcarriers.
    Then interpolate to estimate H for all subcarriers.

    Args:
        received_pilots: Received pilot symbols Y_pilot (after FFT).
        transmitted_pilots: Known transmitted pilot symbols X_pilot.
        pilot_indices: Subcarrier indices where pilots are located.
        fft_size: Total FFT size.
        interpolation: Interpolation method ("linear", "zero", or "nearest").
                      "linear" uses linear interpolation between pilots.

    Returns:
        Estimated channel frequency response H_est (length = fft_size).
    """
    if len(received_pilots) != len(transmitted_pilots) or len(received_pilots) != len(pilot_indices):
        raise ValueError("received_pilots, transmitted_pilots, and pilot_indices must have same length")
    
    # LS estimate at pilot positions: H_est[k] = Y[k] / X[k]
    H_pilot = received_pilots / transmitted_pilots
    
    # Interpolate to all subcarriers
    all_indices = np.arange(fft_size)
    H_est = np.zeros(fft_size, dtype=complex)
    
    if interpolation == "linear":
        # Linear interpolation in complex domain (interpolate real and imag separately)
        H_est.real = np.interp(all_indices, pilot_indices, H_pilot.real)
        H_est.imag = np.interp(all_indices, pilot_indices, H_pilot.imag)
    elif interpolation == "zero":
        # Zero-order hold (nearest pilot)
        for k in range(fft_size):
            idx = np.argmin(np.abs(pilot_indices - k))
            H_est[k] = H_pilot[idx]
    elif interpolation == "nearest":
        # Nearest neighbor
        for k in range(fft_size):
            idx = np.argmin(np.abs(pilot_indices - k))
            H_est[k] = H_pilot[idx]
    else:
        raise ValueError(f"Unsupported interpolation: {interpolation}")
    
    return H_est


def get_data_indices(fft_size: int, pilot_indices: np.ndarray) -> np.ndarray:
    """
    Get indices of subcarriers that carry data (non-pilot).

    Args:
        fft_size: Total FFT size.
        pilot_indices: Subcarrier indices used for pilots.

    Returns:
        Array of data subcarrier indices.
    """
    all_indices = np.arange(fft_size)
    return np.setdiff1d(all_indices, pilot_indices)
