"""
equalizers.py

One-tap frequency-domain equalizers for OFDM: ZF and MMSE.
Used after FFT when the channel is frequency-selective (multipath).
"""

import numpy as np


def equalize_zf(freq_symbols: np.ndarray, channel_response: np.ndarray) -> np.ndarray:
    """
    Zero-forcing equalization: Y_k / H_k. Restores X_k up to noise (noise is amplified at nulls).

    Args:
        freq_symbols: (n_symbols, n_subcarriers) or (n_subcarriers,); received symbols after FFT.
        channel_response: (n_subcarriers,) complex channel gain per subcarrier.

    Returns:
        Equalized symbols, same shape as freq_symbols.
    """
    H = np.asarray(channel_response, dtype=complex)
    if H.ndim != 1:
        raise ValueError("channel_response must be 1D.")
    # Avoid division by zero at spectral nulls
    eps = 1e-10
    H_safe = np.where(np.abs(H) < eps, eps, H)
    return freq_symbols / H_safe


def equalize_mmse(
    freq_symbols: np.ndarray,
    channel_response: np.ndarray,
    snr_linear: float,
) -> np.ndarray:
    """
    MMSE one-tap equalization: W_k = H*_k / (|H_k|^2 + 1/SNR). Minimizes MSE at each subcarrier.

    Args:
        freq_symbols: (n_symbols, n_subcarriers) or (n_subcarriers,); received symbols after FFT.
        channel_response: (n_subcarriers,) complex channel gain per subcarrier.
        snr_linear: SNR in linear scale (not dB).

    Returns:
        Equalized symbols, same shape as freq_symbols.
    """
    H = np.asarray(channel_response, dtype=complex)
    if H.ndim != 1:
        raise ValueError("channel_response must be 1D.")
    # W_k = H* / (|H|^2 + 1/snr)
    H_conj = np.conj(H)
    H_sq = np.abs(H) ** 2
    inv_snr = 1.0 / max(snr_linear, 1e-10)
    W = H_conj / (H_sq + inv_snr)
    return freq_symbols * W
