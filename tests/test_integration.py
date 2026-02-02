"""
Integration tests for end-to-end OFDM system.

Tests the full chain: transmitter → channel → receiver → EVM/BER
to ensure components work together correctly.
"""

import numpy as np
import pytest

from src.transmitter import generate_random_bits, generate_ofdm_stream
from src.receiver import remove_cyclic_prefix, fft_ofdm, demodulate_ofdm_symbols, compute_ber
from src.channel import awgn_channel, multipath_channel
from src.equalizers import equalize_zf, equalize_mmse
from src.evm import compute_evm


class TestEndToEndAWGN:
    """End-to-end tests for AWGN channel."""

    def test_qpsk_awgn_high_snr(self):
        """High SNR should give low BER and low EVM."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        bits_tx = generate_random_bits(fft_size * 2)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "QPSK")
        noisy_stream = awgn_channel(ofdm_stream, snr_db=25.0)
        ofdm_no_cp = remove_cyclic_prefix(noisy_stream, cp_len)
        freq_symbols = fft_ofdm(ofdm_no_cp)
        bits_rx = demodulate_ofdm_symbols(freq_symbols, "QPSK")
        ber = compute_ber(bits_tx, bits_rx)
        assert ber < 1e-3

    def test_16qam_awgn_high_snr(self):
        """High SNR should give low BER for 16-QAM."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        bits_tx = generate_random_bits(fft_size * 4)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "16QAM")
        noisy_stream = awgn_channel(ofdm_stream, snr_db=25.0)
        ofdm_no_cp = remove_cyclic_prefix(noisy_stream, cp_len)
        freq_symbols = fft_ofdm(ofdm_no_cp)
        bits_rx = demodulate_ofdm_symbols(freq_symbols, "16QAM")
        ber = compute_ber(bits_tx, bits_rx)
        assert ber < 1e-2

    def test_evm_decreases_with_snr_awgn(self):
        """EVM should decrease as SNR increases in AWGN."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        bits_tx = generate_random_bits(fft_size * 2)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "QPSK")
        # Get transmitted frequency symbols
        tx_freq = fft_ofdm(remove_cyclic_prefix(ofdm_stream, cp_len))
        # Test at two SNR levels
        noisy_5db = awgn_channel(ofdm_stream, snr_db=5.0)
        noisy_20db = awgn_channel(ofdm_stream, snr_db=20.0)
        rx_freq_5db = fft_ofdm(remove_cyclic_prefix(noisy_5db, cp_len))
        rx_freq_20db = fft_ofdm(remove_cyclic_prefix(noisy_20db, cp_len))
        evm_5db = compute_evm(rx_freq_5db.flatten(), tx_freq.flatten(), percent=True)
        evm_20db = compute_evm(rx_freq_20db.flatten(), tx_freq.flatten(), percent=True)
        assert evm_20db < evm_5db
        assert evm_5db > 0.0
        assert evm_20db > 0.0


class TestEndToEndMultipath:
    """End-to-end tests for multipath channel with equalization."""

    def test_multipath_zf_equalization(self):
        """ZF equalization should improve BER in multipath."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        taps = np.array([1.0, 0.0, 0.4 * np.exp(1j * 0.5)], dtype=complex)
        bits_tx = generate_random_bits(fft_size * 2)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "QPSK")
        # Multipath channel
        multipath_output = multipath_channel(ofdm_stream, taps, snr_db=15.0, cp_len=cp_len)
        freq_symbols = fft_ofdm(multipath_output)
        # Channel frequency response
        h_pad = np.zeros(fft_size, dtype=complex)
        h_pad[:len(taps)] = taps
        H = np.fft.fft(h_pad)
        # Equalize
        freq_equalized = equalize_zf(freq_symbols, H)
        bits_rx = demodulate_ofdm_symbols(freq_equalized, "QPSK")
        ber = compute_ber(bits_tx, bits_rx)
        assert ber < 0.1  # Should be reasonable with equalization

    def test_multipath_mmse_equalization(self):
        """MMSE equalization should work in multipath."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        taps = np.array([1.0, 0.0, 0.4 * np.exp(1j * 0.5)], dtype=complex)
        bits_tx = generate_random_bits(fft_size * 2)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "QPSK")
        multipath_output = multipath_channel(ofdm_stream, taps, snr_db=15.0, cp_len=cp_len)
        freq_symbols = fft_ofdm(multipath_output)
        h_pad = np.zeros(fft_size, dtype=complex)
        h_pad[:len(taps)] = taps
        H = np.fft.fft(h_pad)
        freq_equalized = equalize_mmse(freq_symbols, H, snr_linear=10.0 ** (15.0 / 10.0))
        bits_rx = demodulate_ofdm_symbols(freq_equalized, "QPSK")
        ber = compute_ber(bits_tx, bits_rx)
        assert ber < 0.1

    def test_evm_with_equalization(self):
        """EVM should improve with equalization in multipath."""
        np.random.seed(42)
        fft_size, cp_len = 64, 16
        taps = np.array([1.0, 0.0, 0.4 * np.exp(1j * 0.5)], dtype=complex)
        bits_tx = generate_random_bits(fft_size * 2)
        ofdm_stream = generate_ofdm_stream(bits_tx, fft_size, cp_len, "QPSK")
        tx_freq = fft_ofdm(remove_cyclic_prefix(ofdm_stream, cp_len))
        # Multipath
        multipath_output = multipath_channel(ofdm_stream, taps, snr_db=10.0, cp_len=cp_len)
        freq_symbols = fft_ofdm(multipath_output)
        h_pad = np.zeros(fft_size, dtype=complex)
        h_pad[:len(taps)] = taps
        H = np.fft.fft(h_pad)
        # Compare EVM with and without equalization
        evm_no_eq = compute_evm(freq_symbols.flatten(), tx_freq.flatten(), percent=True)
        freq_zf = equalize_zf(freq_symbols, H)
        evm_zf = compute_evm(freq_zf.flatten(), tx_freq.flatten(), percent=True)
        freq_mmse = equalize_mmse(freq_symbols, H, snr_linear=10.0)
        evm_mmse = compute_evm(freq_mmse.flatten(), tx_freq.flatten(), percent=True)
        # Equalization should improve EVM
        assert evm_zf < evm_no_eq
        assert evm_mmse < evm_no_eq
        assert evm_no_eq > 0.0
        assert evm_zf > 0.0
        assert evm_mmse > 0.0
