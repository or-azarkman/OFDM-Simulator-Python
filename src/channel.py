# channel.py

"""
channel.py

Channel models for OFDM system simulation:
- Additive White Gaussian Noise (AWGN) channel model

This module defines functions that model the transmission channel
impairments in baseband OFDM systems. It can be extended later
to include multipath fading, Doppler effects, and other real
wireless channel models.
"""

import numpy as np

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
    performance evaluation. :contentReference[oaicite:1]{index=1}

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

    # Add noise to original signal
    return signal + noise
