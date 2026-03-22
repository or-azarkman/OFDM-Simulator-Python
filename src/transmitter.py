"""
transmitter.py

Transmitter chain for an OFDM system:
- Bit generation
- QPSK and 16‑QAM modulation with Gray coding
- Subcarrier mapping
- OFDM IFFT and cyclic prefix insertion

This module supports different modulation orders and prepares
OFDM symbols for transmission in a simulation environment.
"""

import numpy as np


def generate_random_bits(num_bits: int) -> np.ndarray:
    """
    Generate a random bit array of 0s and 1s.

    Args:
        num_bits (int): Number of bits to generate.

    Returns:
        np.ndarray: Array of shape (num_bits,) with bits {0,1}.
    """
    return np.random.randint(0, 2, num_bits)


def qpsk_modulate(bits: np.ndarray) -> np.ndarray:
    """
    Map bits to QPSK symbols using Gray coding.

    Each pair of bits [b0,b1] maps to one complex symbol:
        00 ->  1 + 1j
        01 -> -1 + 1j
        11 -> -1 - 1j
        10 ->  1 - 1j

    The result is normalized by sqrt(2) to maintain unit average power.

    Args:
        bits (np.ndarray): 1D array of bits (length divisible by 2).

    Returns:
        np.ndarray: Complex QPSK symbols of length len(bits)//2.
    """
    if len(bits) % 2 != 0:
        raise ValueError("Number of bits must be even for QPSK.")

    bits_reshaped = bits.reshape(-1, 2)
    mapping = {
        (0, 0):  1 + 1j,
        (0, 1): -1 + 1j,
        (1, 1): -1 - 1j,
        (1, 0):  1 - 1j,
    }
    symbols = np.array([mapping[tuple(b)] for b in bits_reshaped], dtype=complex)
    symbols /= np.sqrt(2)  # Normalize average power
    return symbols


def qam16_modulate(bits: np.ndarray) -> np.ndarray:
    """
    Map bits to 16‑QAM symbols using Gray coding.

    Each group of 4 bits maps to one complex symbol.     Gray coding
    ensures adjacent constellation points differ by one bit,
    improving BER performance in noisy channels.

    Args:
        bits (np.ndarray): 1D array of bits (length divisible by 4).

    Returns:
        np.ndarray: Complex 16‑QAM symbols of length len(bits)//4.
    """
    if len(bits) % 4 != 0:
        raise ValueError("Number of bits must be multiple of 4 for 16‑QAM.")

    bits_reshaped = bits.reshape(-1, 4)
    mapping = {
        (0,0,0,0): -3 - 3j,  (0,0,0,1): -3 - 1j,
        (0,0,1,1): -3 + 1j,  (0,0,1,0): -3 + 3j,
        (0,1,1,0): -1 + 3j,  (0,1,1,1): -1 + 1j,
        (0,1,0,1): -1 - 1j,  (0,1,0,0): -1 - 3j,
        (1,1,0,0):  1 - 3j,  (1,1,0,1):  1 - 1j,
        (1,1,1,1):  1 + 1j,  (1,1,1,0):  1 + 3j,
        (1,0,1,0):  3 + 3j,  (1,0,1,1):  3 + 1j,
        (1,0,0,1):  3 - 1j,  (1,0,0,0):  3 - 3j
    }
    symbols = np.array([mapping[tuple(b)] for b in bits_reshaped], dtype=complex)
    symbols /= np.sqrt(10)  # Normalize average power
    return symbols


def map_to_subcarriers(symbols: np.ndarray, fft_size: int) -> np.ndarray:
    """
    Map data symbols into the OFDM subcarrier array.

    The provided symbols fill the first positions of the FFT frame;
    the remainder are set to zero.

    Args:
        symbols (np.ndarray): Modulated symbols to place on subcarriers.
        fft_size (int): Total number of subcarriers (FFT size).

    Returns:
        np.ndarray: Frequency‑domain frame of length fft_size.
    """
    if len(symbols) > fft_size:
        raise ValueError("More symbols than available subcarriers.")

    frame = np.zeros(fft_size, dtype=complex)
    frame[:len(symbols)] = symbols
    return frame


def map_to_subcarriers_with_pilots(
    data_symbols: np.ndarray,
    pilot_indices: np.ndarray,
    pilot_symbols: np.ndarray,
    fft_size: int,
) -> np.ndarray:
    """
    Map data symbols and insert pilots into the OFDM subcarrier array.

    Data symbols are placed on non-pilot subcarriers; pilots are inserted
    at specified indices. This enables channel estimation at the receiver.

    Args:
        data_symbols: Data symbols to place on non-pilot subcarriers.
        pilot_indices: Subcarrier indices where pilots are placed.
        pilot_symbols: Pilot symbol values (length must match pilot_indices).
        fft_size: Total number of subcarriers (FFT size).

    Returns:
        Frequency‑domain frame with pilots inserted.
    """
    from src.pilots import insert_pilots
    return insert_pilots(data_symbols, pilot_indices, pilot_symbols, fft_size)


def ofdm_ifft(frame: np.ndarray) -> np.ndarray:
    """
    Perform Inverse FFT (IFFT) to generate time‑domain OFDM symbol.

    Args:
        frame (np.ndarray): Frequency‑domain samples (length = fft_size).

    Returns:
        np.ndarray: Time‑domain OFDM samples.
    """
    return np.fft.ifft(frame)


def add_cyclic_prefix(time_signal: np.ndarray, cp_len: int) -> np.ndarray:
    """
    Add a cyclic prefix to the time‑domain OFDM symbol.

    The cyclic prefix is a copy of the last cp_len samples
    added at the beginning of the symbol.

    Args:
        time_signal (np.ndarray): OFDM time‑domain samples.
        cp_len (int): Cyclic prefix length.

    Returns:
        np.ndarray: OFDM symbol with cyclic prefix.
    """
    if cp_len <= 0:
        return time_signal
    cp = time_signal[-cp_len:]
    return np.concatenate([cp, time_signal])


def generate_ofdm_symbol(
    bits: np.ndarray,
    fft_size: int,
    cp_len: int,
    modulation: str = "QPSK",
    pilot_indices: np.ndarray = None,
    pilot_symbols: np.ndarray = None,
) -> np.ndarray:
    """
    Create one OFDM symbol with the specified modulation.

    Args:
        bits (np.ndarray): Input bits for this OFDM symbol.
        fft_size (int): FFT size (number of subcarriers).
        cp_len (int): Cyclic prefix length.
        modulation (str): "QPSK" or "16QAM"
        pilot_indices (np.ndarray, optional): Subcarrier indices for pilots.
        pilot_symbols (np.ndarray, optional): Pilot symbol values.

    Returns:
        np.ndarray: Time‑domain OFDM symbol including CP.
    """
    if modulation.upper() == "QPSK":
        syms = qpsk_modulate(bits)
    elif modulation.upper() == "16QAM":
        syms = qam16_modulate(bits)
    else:
        raise ValueError(f"Unsupported modulation: {modulation}")

    if pilot_indices is not None and pilot_symbols is not None:
        freq_frame = map_to_subcarriers_with_pilots(syms, pilot_indices, pilot_symbols, fft_size)
    else:
        freq_frame = map_to_subcarriers(syms, fft_size)
    
    time_signal = ofdm_ifft(freq_frame)
    return add_cyclic_prefix(time_signal, cp_len)


def generate_ofdm_stream(
    bits: np.ndarray,
    fft_size: int,
    cp_len: int,
    modulation: str = "QPSK",
    pilot_indices: np.ndarray = None,
    pilot_symbols: np.ndarray = None,
) -> np.ndarray:
    """
    Convert a full bitstream into multiple OFDM symbols.

    The bits_per_symbol depends on the modulation order and number of data subcarriers:
        - QPSK: 2 bits per data subcarrier
        - 16‑QAM: 4 bits per data subcarrier
    If pilots are used, only data subcarriers carry information bits.

    Args:
        bits (np.ndarray): Full bitstream.
        fft_size (int): FFT size.
        cp_len (int): Cyclic prefix length.
        modulation (str): Modulation type ("QPSK" or "16QAM").
        pilot_indices (np.ndarray, optional): Subcarrier indices for pilots.
        pilot_symbols (np.ndarray, optional): Pilot symbol values.

    Returns:
        np.ndarray: 2D array [num_symbols, symbol_length_with_cp].
    """
    if pilot_indices is not None:
        num_data_subcarriers = fft_size - len(pilot_indices)
    else:
        num_data_subcarriers = fft_size
    
    bits_per_symbol = num_data_subcarriers * (2 if modulation.upper()=="QPSK" else 4)
    if len(bits) % bits_per_symbol != 0:
        raise ValueError(f"Bitstream length ({len(bits)}) must be a multiple of bits_per_symbol ({bits_per_symbol}).")

    ofdm_symbols = []
    for i in range(len(bits) // bits_per_symbol):
        start = i * bits_per_symbol
        segment = bits[start:start+bits_per_symbol]
        ofdm_symbols.append(
            generate_ofdm_symbol(segment, fft_size, cp_len, modulation, pilot_indices, pilot_symbols)
        )
    return np.array(ofdm_symbols)
