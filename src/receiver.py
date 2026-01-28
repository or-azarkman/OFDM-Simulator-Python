"""
receiver.py

OFDM receiver functions for recovering transmitted bits:
- Cyclic Prefix removal
- FFT to convert time-domain OFDM symbols to frequency-domain
- QPSK and 16‑QAM demodulation with Gray decoding
- Bit Error Rate (BER) computation

This module is designed to match the transmitter implementation
in transmitter.py, with consistent naming and data formats.
"""

import numpy as np


def remove_cyclic_prefix(ofdm_stream: np.ndarray, cp_len: int) -> np.ndarray:
    """
    Remove the cyclic prefix from each OFDM symbol.

    In OFDM systems the cyclic prefix is a copy of the last part
    of the OFDM symbol that was added at the beginning to mitigate
    inter-symbol interference (ISI). The receiver discards these
    prefix samples before performing FFT.

    Args:
        ofdm_stream (np.ndarray):
            2D array of OFDM symbols with CP.
        cp_len (int):
            Length of cyclic prefix that was added at the transmitter.

    Returns:
        np.ndarray:
            2D array of OFDM time-domain symbols without CP.
    """
    return ofdm_stream[:, cp_len:]


def fft_ofdm(ofdm_no_cp: np.ndarray) -> np.ndarray:
    """
    Apply FFT to each OFDM time-domain symbol to recover
    frequency-domain subcarrier values.

    The FFT is the inverse operation to the IFFT in the transmitter.

    Args:
        ofdm_no_cp (np.ndarray):
            OFDM symbols after CP removal.

    Returns:
        np.ndarray:
            Frequency-domain symbols of shape (num_symbols, fft_size).
    """
    return np.fft.fft(ofdm_no_cp)


def qpsk_demodulate(symbols: np.ndarray) -> np.ndarray:
    """
    Demodulate QPSK symbols into bits (Gray-coded mapping).

    This function matches the exact mapping used in the transmitter:
        00 ->  1 + 1j
        01 -> -1 + 1j
        11 -> -1 - 1j
        10 ->  1 - 1j

    Args:
        symbols (np.ndarray):
            Complex frequency-domain symbols.

    Returns:
        np.ndarray:
            1D array of demodulated bits.
    """
    bits_out = []
    for sym in symbols.flatten():
        # Map back to original bit pattern
        if sym.real >= 0 and sym.imag >= 0:
            bits_out.extend([0, 0])
        elif sym.real < 0 and sym.imag >= 0:
            bits_out.extend([0, 1])
        elif sym.real < 0 and sym.imag < 0:
            bits_out.extend([1, 1])
        elif sym.real >= 0 and sym.imag < 0:
            bits_out.extend([1, 0])
    return np.array(bits_out)


def qam16_demodulate(symbols: np.ndarray) -> np.ndarray:
    """
    Demodulate 16‑QAM symbols into bits using Gray decoding.

    The Gray coded 16‑QAM constellation assigns bit patterns so that
    adjacent signal points differ in only one bit, which improves BER
    in the presence of noise.

    Args:
        symbols (np.ndarray):
            Complex frequency-domain 16‑QAM symbols.

    Returns:
        np.ndarray:
            1D array of demodulated bits.
    """
    # Gray mapping table for 16 QAM
    ideal = {
        -3 - 3j: (0,0,0,0),  -3 - 1j: (0,0,0,1),
        -3 + 1j: (0,0,1,1),  -3 + 3j: (0,0,1,0),
        -1 + 3j: (0,1,1,0),  -1 + 1j: (0,1,1,1),
        -1 - 1j: (0,1,0,1),  -1 - 3j: (0,1,0,0),
         1 - 3j: (1,1,0,0),   1 - 1j: (1,1,0,1),
         1 + 1j: (1,1,1,1),   1 + 3j: (1,1,1,0),
         3 + 3j: (1,0,1,0),   3 + 1j: (1,0,1,1),
         3 - 1j: (1,0,0,1),   3 - 3j: (1,0,0,0)
    }

    # Normalize to match transmitter scaling
    ideal_norm = {pt/np.sqrt(10): bits for pt, bits in ideal.items()}

    bits_out = []
    for sym in symbols.flatten():
        # Choose closest constellation point by Euclidean distance
        closest = min(ideal_norm.keys(), key=lambda c: abs(sym - c))
        bits_out.extend(ideal_norm[closest])
    return np.array(bits_out)


def demodulate_ofdm_symbols(
    freq_symbols: np.ndarray,
    modulation: str = "QPSK"
) -> np.ndarray:
    """
    Convert frequency-domain symbols into a 1D array of bits.

    Depending on the modulation ("QPSK" or "16QAM"), this function
    applies the correct demodulation method.

    Args:
        freq_symbols (np.ndarray):
            Frequency-domain symbols from FFT.
        modulation (str):
            "QPSK" or "16QAM".

    Returns:
        np.ndarray:
            Demodulated bitstream.
    """
    if modulation.upper() == "QPSK":
        return qpsk_demodulate(freq_symbols)
    elif modulation.upper() == "16QAM":
        return qam16_demodulate(freq_symbols)
    else:
        raise ValueError(f"Unsupported modulation: {modulation}")


def compute_ber(original_bits: np.ndarray, received_bits: np.ndarray) -> float:
    """
    Compute the Bit Error Rate (BER) between transmitted and received bits.

    BER is the fraction of bit positions that differ
    between the transmitted and received streams.

    Args:
        original_bits (np.ndarray):
            The original transmitted bit array.
        received_bits (np.ndarray):
            The bit array recovered at the receiver.

    Returns:
        float:
            BER (0.0 -> perfect match, up to 1.0 -> all bits incorrect).
    """
    if len(original_bits) != len(received_bits):
        raise ValueError("Original and received bit sequences must match in length.")

    return np.sum(original_bits != received_bits) / len(original_bits)
