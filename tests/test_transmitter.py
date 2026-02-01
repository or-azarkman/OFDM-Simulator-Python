"""
Unit tests for OFDM transmitter (modulation, IFFT, CP).
"""

import numpy as np
import pytest

from src.transmitter import (
    generate_random_bits,
    qpsk_modulate,
    qam16_modulate,
    map_to_subcarriers,
    ofdm_ifft,
    add_cyclic_prefix,
    generate_ofdm_symbol,
    generate_ofdm_stream,
)


class TestGenerateRandomBits:
    def test_length(self):
        bits = generate_random_bits(100)
        assert bits.shape == (100,)
        assert np.isin(bits, [0, 1]).all()

    def test_deterministic_with_seed(self):
        np.random.seed(42)
        a = generate_random_bits(20)
        np.random.seed(42)
        b = generate_random_bits(20)
        np.testing.assert_array_equal(a, b)


class TestQPSKModulate:
    def test_shape(self):
        bits = np.array([0, 0, 1, 1, 1, 0, 0, 1])
        syms = qpsk_modulate(bits)
        assert len(syms) == 4
        assert np.iscomplexobj(syms)

    def test_odd_bits_raises(self):
        with pytest.raises(ValueError, match="even"):
            qpsk_modulate(np.array([0, 1, 0]))

    def test_mapping_and_power(self):
        # 00 -> (1+1j)/sqrt(2)
        bits = np.array([0, 0])
        syms = qpsk_modulate(bits)
        expected = (1 + 1j) / np.sqrt(2)
        np.testing.assert_allclose(syms[0], expected)
        # Average power ~ 1
        bits_long = generate_random_bits(1000)
        syms_long = qpsk_modulate(bits_long)
        assert 0.9 <= np.mean(np.abs(syms_long) ** 2) <= 1.1


class TestQAM16Modulate:
    def test_shape(self):
        bits = np.zeros(16, dtype=int)
        syms = qam16_modulate(bits)
        assert len(syms) == 4
        assert np.iscomplexobj(syms)

    def test_not_multiple_of_four_raises(self):
        with pytest.raises(ValueError, match="multiple of 4"):
            qam16_modulate(np.array([0, 1, 0]))

    def test_average_power(self):
        bits = generate_random_bits(400)
        syms = qam16_modulate(bits)
        # Normalized 16-QAM has avg power 1
        assert 0.9 <= np.mean(np.abs(syms) ** 2) <= 1.1


class TestMapToSubcarriers:
    def test_fft_size(self):
        syms = np.array([1 + 0j, -1 + 0j])
        frame = map_to_subcarriers(syms, 64)
        assert len(frame) == 64
        np.testing.assert_allclose(frame[:2], syms)
        assert np.all(frame[2:] == 0)

    def test_too_many_symbols_raises(self):
        syms = np.zeros(65, dtype=complex)
        with pytest.raises(ValueError, match="More symbols"):
            map_to_subcarriers(syms, 64)


class TestOFDMIFFT:
    def test_length_preserved(self):
        frame = np.fft.fft(np.random.randn(64))
        time_sig = ofdm_ifft(frame)
        assert len(time_sig) == 64

    def test_roundtrip_with_fft(self):
        frame = np.random.randn(64) + 1j * np.random.randn(64)
        time_sig = ofdm_ifft(frame)
        back = np.fft.fft(time_sig)
        np.testing.assert_allclose(back, frame)


class TestAddCyclicPrefix:
    def test_length(self):
        x = np.arange(64, dtype=complex)
        y = add_cyclic_prefix(x, 16)
        assert len(y) == 80
        np.testing.assert_array_equal(y[:16], x[-16:])
        np.testing.assert_array_equal(y[16:], x)


class TestGenerateOFDMSymbol:
    def test_qpsk_symbol_shape(self):
        np.random.seed(0)
        bits = generate_random_bits(64 * 2)
        sym = generate_ofdm_symbol(bits, 64, 16, "QPSK")
        assert sym.ndim == 1
        assert len(sym) == 64 + 16

    def test_16qam_symbol_shape(self):
        np.random.seed(0)
        bits = generate_random_bits(64 * 4)
        sym = generate_ofdm_symbol(bits, 64, 16, "16QAM")
        assert len(sym) == 64 + 16


class TestGenerateOFDMStream:
    def test_stream_shape(self):
        np.random.seed(0)
        bits_per_sym = 64 * 2
        bits = generate_random_bits(3 * bits_per_sym)
        stream = generate_ofdm_stream(bits, 64, 16, "QPSK")
        assert stream.shape[0] == 3
        assert stream.shape[1] == 64 + 16

    def test_wrong_bit_length_raises(self):
        bits = np.zeros(100)
        with pytest.raises(ValueError, match="multiple"):
            generate_ofdm_stream(bits, 64, 16, "QPSK")
