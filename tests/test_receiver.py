"""
Unit tests for OFDM receiver (CP removal, FFT, demodulation, BER).
"""

import numpy as np
import pytest

from src.receiver import (
    remove_cyclic_prefix,
    fft_ofdm,
    qpsk_demodulate,
    qam16_demodulate,
    demodulate_ofdm_symbols,
    compute_ber,
)
from src.transmitter import qpsk_modulate, qam16_modulate


class TestRemoveCyclicPrefix:
    def test_shape(self):
        stream = np.random.randn(10, 80) + 1j * np.random.randn(10, 80)
        out = remove_cyclic_prefix(stream, 16)
        assert out.shape == (10, 64)
        np.testing.assert_array_equal(out[0], stream[0, 16:])


class TestFFTOFDM:
    def test_shape(self):
        x = np.random.randn(5, 64) + 1j * np.random.randn(5, 64)
        out = fft_ofdm(x)
        assert out.shape == (5, 64)


class TestQPSKRoundtrip:
    def test_no_noise(self):
        np.random.seed(1)
        bits = np.random.randint(0, 2, 200)
        syms = qpsk_modulate(bits)
        bits_rx = qpsk_demodulate(syms)
        np.testing.assert_array_equal(bits_rx, bits)

    def test_demodulate_single_points(self):
        # (1+1j)/sqrt(2) -> 00
        syms = np.array([(1 + 1j) / np.sqrt(2)])
        np.testing.assert_array_equal(qpsk_demodulate(syms), [0, 0])


class TestQAM16Roundtrip:
    def test_no_noise(self):
        np.random.seed(2)
        bits = np.random.randint(0, 2, 64)
        syms = qam16_modulate(bits)
        bits_rx = qam16_demodulate(syms)
        np.testing.assert_array_equal(bits_rx, bits)


class TestDemodulateOFDMSymbols:
    def test_unsupported_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            demodulate_ofdm_symbols(np.array([1.0]), "64QAM")


class TestComputeBER:
    def test_perfect_match(self):
        b = np.array([0, 1, 1, 0])
        assert compute_ber(b, b) == 0.0

    def test_half_errors(self):
        # Exactly 2 out of 4 bits differ → BER = 0.5
        a = np.array([0, 0, 1, 1])
        b = np.array([0, 1, 1, 0])  # positions 1 and 3 differ
        assert compute_ber(a, b) == 0.5

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError, match="length"):
            compute_ber(np.array([0, 1]), np.array([0, 1, 0]))
