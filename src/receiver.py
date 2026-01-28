"""
receiver.py

OFDM receiver functions for recovering transmitted bits:
- Cyclic Prefix removal
- FFT to convert time-domain OFDM symbols to frequency-domain
- QPSK demodulation
- Bit Error Rate (BER) computation

This module is designed to match the transmitter implementation
in transmitter.py with consistent variable names and expected data
formats.
"""

import numpy as np

def remove_cyclic_prefix(ofdm_stream: np.ndarray, cp_len: int) -> np.ndarray:
    """
    Remove the cyclic prefix from each OFDM symbol.

    In OFDM systems the cyclic prefix is a copy of the last part
    of the symbol added at the beginning to mitigate ISI. The
    receiver discards these prefix samples before FFT.

    Args:
        ofdm_stream (np.ndarray): 2D array of shape (num_symbols, symbol_length_with_cp)
        cp_len (int): Cyclic prefix length that was added at the transmitter

    Returns:
        np.ndarray: 2D array of OFDM time-domain symbols without CP
    """
    return ofdm_stream[:, cp_len:]


def fft_ofdm(ofdm_no_cp: np.ndarray) -> np.ndarray:
    """
    Apply FFT to each OFDM time-domain symbol to recover
    frequency-domain subcarrier values.

    In OFDM, the FFT is the inverse operation to the IFFT done
    in the transmitter. The FFT returns complex values representing
    each subcarrier's modulated symbol.

    Args:
        ofdm_no_cp (np.ndarray): OFDM symbols after CP removal

    Returns:
        np.ndarray: Frequency-domain symbols of shape (num_symbols, fft_size)
    """
    return np.fft.fft(ofdm_no_cp)


def qpsk_demodulate(symbols: np.ndarray) -> np.ndarray:
    """
    Demodulate QPSK symbols into bits.

    QPSK decision rule used here:
        real(sym) >= 0 -> b0 = 0
        real(sym) <  0 -> b0 = 1
        imag(sym) >= 0 -> b1 = 0
        imag(sym) <  0 -> b1 = 1

    Args:
        symbols (np.ndarray): Complex frequency-domain symbols

    Returns:
        np.ndarray: 1D array of demodulated bits
    """
    bits_out = []
    for sym in symbols.flatten():
        bit0 = 0 if sym.real >= 0 else 1
        bit1 = 0 if sym.imag >= 0 else 1
        bits_out.extend([bit0, bit1])
    return np.array(bits_out)


def compute_ber(original_bits: np.ndarray, received_bits: np.ndarray) -> float:
    """
    Compute the Bit Error Rate (BER) between transmitted and received bits.

    The BER is calculated as the fraction of bit positions where
    original and received bits differ.

    Args:
        original_bits (np.ndarray): The original transmitted bit array
        received_bits (np.ndarray): The bit array recovered at the receiver

    Returns:
        float: BER (0.0 -> perfect, up to 1.0 -> all bits incorrect)
    """
    if len(original_bits) != len(received_bits):
        raise ValueError("Original and received bit sequences must match in length.")

    num_errors = np.sum(original_bits != received_bits)
    return num_errors / len(original_bits)
