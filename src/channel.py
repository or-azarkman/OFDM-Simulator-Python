"""
channel.py

Channel models for OFDM system simulation:
- AWGN (Additive White Gaussian Noise)
- Multipath (frequency-selective fading via FIR taps + AWGN)
"""

import numpy as np
from typing import Union, Sequence


def awgn_channel(
    signal: np.ndarray,
    snr_db: float
) -> np.ndarray:
    """
    Apply Additive White Gaussian Noise (AWGN) to a complex baseband
    signal to simulate channel noise under a specified signal‑to‑noise
    ratio (SNR).

    The AWGN channel model adds noise samples drawn from a zero‑mean
    Gaussian distribution to the input signal. AWGN is a basic channel
    impairment model widely used in communication theory and system
    performance evaluation.

    Args:
        signal (np.ndarray): Complex baseband signal samples.
        snr_db (float): Desired SNR in decibels (dB). Higher values
                          correspond to less noise.

    Returns:
        np.ndarray: Noisy signal after channel effect.
    """
    # Calculate signal power
    sig_power = np.mean(np.abs(signal)**2)

    # Convert SNR from dB to linear scale
    snr_linear = 10 ** (snr_db / 10)

    # Compute noise power based on desired SNR
    noise_power = sig_power / snr_linear

    # Generate white Gaussian noise (complex)
    noise = np.sqrt(noise_power / 2) * (
        np.random.randn(*signal.shape) +
        1j * np.random.randn(*signal.shape)
    )

    return signal + noise


def multipath_channel(
    signal: np.ndarray,
    taps: Union[Sequence[complex], np.ndarray],
    snr_db: float,
    cp_len: int = 0,
) -> np.ndarray:
    """
    Frequency-selective channel for OFDM: circular convolution of the useful
    part (after CP) of each symbol with the impulse response (taps), then AWGN.

    In OFDM, after removing the cyclic prefix the effective channel is
    circular convolution in time, so in frequency domain Y_k = H_k * X_k + N_k.
    This preserves the per-subcarrier flat-fading model and allows BER to
    improve with SNR when equalization is applied (or when H_k is mild).

    Signal is (n_symbols, n_samples) with n_samples = N + cp_len per symbol.
    Output is (n_symbols, N), i.e. symbols without CP (receiver must not
    remove CP again when using this channel).

    Taps are normalized to unit energy so SNR refers to the faded signal.
    """
    taps = np.asarray(taps, dtype=complex)
    taps = taps / np.sqrt(np.sum(np.abs(taps) ** 2))
    if signal.ndim == 1:
        signal = signal.reshape(1, -1)
        squeeze = True
    else:
        squeeze = False
    n_sym, full_len = signal.shape
    n_fft = full_len - cp_len
    if n_fft <= 0:
        raise ValueError("cp_len must be less than symbol length (samples per row).")
    # Zero-pad taps to FFT length for circular convolution
    h_pad = np.zeros(n_fft, dtype=complex)
    h_pad[: len(taps)] = taps
    H = np.fft.fft(h_pad)
    out = np.zeros((n_sym, n_fft), dtype=complex)
    for i in range(n_sym):
        useful = signal[i, cp_len:]
        out[i] = np.fft.ifft(np.fft.fft(useful) * H)
    if squeeze:
        out = out.flatten()
    return awgn_channel(out, snr_db)


def multipath_channel_linear(
    signal: np.ndarray,
    taps: Union[Sequence[complex], np.ndarray],
    snr_db: float,
    cp_len: int,
    n_fft: int,
) -> np.ndarray:
    """
    Multipath channel with true linear convolution over the full stream.
    When CP is shorter than the channel delay spread, the receiver's
    "useful" window contains ISI from the previous symbol, so BER/EVM degrade.

    Signal is (n_symbols, n_fft + cp_len). Output is (n_symbols, n_fft).
    Taps are normalized to unit energy.
    """
    taps = np.asarray(taps, dtype=complex)
    taps = taps / np.sqrt(np.sum(np.abs(taps) ** 2))
    if signal.ndim == 1:
        signal = signal.reshape(1, -1)
        squeeze = True
    else:
        squeeze = False
    n_sym, full_len = signal.shape
    assert full_len == n_fft + cp_len, "full_len must equal n_fft + cp_len"
    stream_flat = signal.flatten()
    conv_out = np.convolve(stream_flat, taps, mode="full")
    sym_len = n_fft + cp_len
    out = np.zeros((n_sym, n_fft), dtype=complex)
    for i in range(n_sym):
        start = i * sym_len + cp_len
        out[i] = conv_out[start : start + n_fft]
    if squeeze:
        out = out.flatten()
    return awgn_channel(out, snr_db)
