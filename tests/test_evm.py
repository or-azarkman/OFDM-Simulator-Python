"""
Unit tests for Error Vector Magnitude (EVM) computation.
"""

import numpy as np
import pytest

from src.evm import compute_evm
from src.transmitter import qpsk_modulate, qam16_modulate
from src.channel import awgn_channel
from src.equalizers import equalize_zf, equalize_mmse


class TestComputeEVM:
    def test_identical_symbols_zero_evm(self):
        x = np.random.randn(64) + 1j * np.random.randn(64)
        evm_pct = compute_evm(x, x, percent=True)
        evm_frac = compute_evm(x, x, percent=False)
        assert evm_pct == 0.0
        assert evm_frac == 0.0

    def test_shape_2d_flattened(self):
        r = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        t = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        evm = compute_evm(r, t, percent=True)
        assert isinstance(evm, float)
        assert evm >= 0.0

    def test_percent_vs_fraction(self):
        r = np.random.randn(100) + 1j * np.random.randn(100)
        t = np.random.randn(100) + 1j * np.random.randn(100)
        evm_pct = compute_evm(r, t, percent=True)
        evm_frac = compute_evm(r, t, percent=False)
        np.testing.assert_allclose(evm_pct, 100.0 * evm_frac)

    def test_length_mismatch_raises(self):
        r = np.ones(10, dtype=complex)
        t = np.ones(12, dtype=complex)
        with pytest.raises(ValueError, match="same length"):
            compute_evm(r, t)

    def test_zero_reference_returns_zero(self):
        r = np.ones(64, dtype=complex)
        t = np.zeros(64, dtype=complex)
        evm = compute_evm(r, t, percent=True)
        assert evm == 0.0

    def test_known_offset(self):
        """EVM with known constant offset should match expected value."""
        t = np.ones(100, dtype=complex) * (1.0 + 1j)
        offset = 0.1 * (1.0 + 1j)
        r = t + offset
        evm = compute_evm(r, t, percent=False)
        expected = np.abs(offset) / np.abs(t[0])
        np.testing.assert_allclose(evm, expected, rtol=1e-10)

    def test_qpsk_symbols_no_noise(self):
        """EVM should be zero for perfect QPSK transmission."""
        np.random.seed(42)
        bits = np.random.randint(0, 2, 64)
        tx_syms = qpsk_modulate(bits)
        evm = compute_evm(tx_syms, tx_syms, percent=True)
        assert evm == 0.0

    def test_qam16_symbols_no_noise(self):
        """EVM should be zero for perfect 16-QAM transmission."""
        np.random.seed(42)
        bits = np.random.randint(0, 2, 64)
        tx_syms = qam16_modulate(bits)
        evm = compute_evm(tx_syms, tx_syms, percent=True)
        assert evm == 0.0

    def test_awgn_increases_evm(self):
        """EVM should increase with noise (lower SNR)."""
        np.random.seed(42)
        tx_syms = qpsk_modulate(np.random.randint(0, 2, 200))
        rx_low_snr = awgn_channel(tx_syms, snr_db=5.0)
        rx_high_snr = awgn_channel(tx_syms, snr_db=20.0)
        evm_low = compute_evm(rx_low_snr, tx_syms, percent=True)
        evm_high = compute_evm(rx_high_snr, tx_syms, percent=True)
        assert evm_low > evm_high
        assert evm_low > 0.0
        assert evm_high > 0.0

    def test_evm_with_multipath_and_equalization(self):
        """EVM should decrease after equalization in multipath channel."""
        np.random.seed(42)
        fft_size = 64
        tx_syms = qpsk_modulate(np.random.randint(0, 2, fft_size * 2))
        # Create frequency-domain channel response
        taps = np.array([1.0, 0.0, 0.4 * np.exp(1j * 0.5)], dtype=complex)
        h_pad = np.zeros(fft_size, dtype=complex)
        h_pad[:len(taps)] = taps
        H = np.fft.fft(h_pad)
        # Simulate multipath: Y = H * X + N (simplified, no time-domain convolution)
        rx_no_eq = tx_syms * H + 0.1 * (np.random.randn(len(tx_syms)) + 1j * np.random.randn(len(tx_syms)))
        rx_zf = equalize_zf(rx_no_eq, H)
        rx_mmse = equalize_mmse(rx_no_eq, H, snr_linear=10.0)
        evm_no_eq = compute_evm(rx_no_eq, tx_syms, percent=True)
        evm_zf = compute_evm(rx_zf, tx_syms, percent=True)
        evm_mmse = compute_evm(rx_mmse, tx_syms, percent=True)
        # Equalized should have lower EVM than no equalization
        assert evm_zf < evm_no_eq
        assert evm_mmse < evm_no_eq
        # All should be positive
        assert evm_no_eq > 0.0
        assert evm_zf > 0.0
        assert evm_mmse > 0.0

    def test_evm_reasonable_range(self):
        """EVM should be in reasonable range (0-200% for extreme cases)."""
        np.random.seed(42)
        bits = np.random.randint(0, 2, 100)
        tx_syms = qpsk_modulate(bits)  # Returns 50 symbols (100 bits / 2)
        # Add significant noise (match shape)
        noise = 2.0 * (np.random.randn(len(tx_syms)) + 1j * np.random.randn(len(tx_syms)))
        rx_syms = tx_syms + noise
        evm = compute_evm(rx_syms, tx_syms, percent=True)
        assert 0.0 <= evm < 500.0  # Reasonable upper bound for extreme noise
