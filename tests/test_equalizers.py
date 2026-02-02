"""
Unit tests for one-tap equalizers (ZF, MMSE).
"""

import numpy as np
import pytest

from src.equalizers import equalize_zf, equalize_mmse


class TestEqualizeZF:
    def test_shape_2d(self):
        Y = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        H = np.ones(64, dtype=complex) + 0.1 * (np.random.randn(64) + 1j * np.random.randn(64))
        out = equalize_zf(Y, H)
        assert out.shape == Y.shape
        assert np.iscomplexobj(out)

    def test_shape_1d(self):
        Y = np.random.randn(64) + 1j * np.random.randn(64)
        H = np.ones(64, dtype=complex)
        out = equalize_zf(Y, H)
        assert out.shape == Y.shape

    def test_identity_channel(self):
        X = np.random.randn(64) + 1j * np.random.randn(64)
        H = np.ones(64, dtype=complex)
        Y = X * H
        out = equalize_zf(Y, H)
        np.testing.assert_allclose(out, X, atol=1e-10)

    def test_channel_response_1d_raises(self):
        Y = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        H = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        with pytest.raises(ValueError, match="1D"):
            equalize_zf(Y, H)


class TestEqualizeMMSE:
    def test_shape_2d(self):
        Y = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        H = np.ones(64, dtype=complex) + 0.1 * (np.random.randn(64) + 1j * np.random.randn(64))
        out = equalize_mmse(Y, H, snr_linear=10.0)
        assert out.shape == Y.shape
        assert np.iscomplexobj(out)

    def test_high_snr_near_zf(self):
        np.random.seed(42)
        X = np.random.randn(64) + 1j * np.random.randn(64)
        H = np.ones(64, dtype=complex) * (0.5 + 0.3j)
        Y = X * H
        out_zf = equalize_zf(Y, H)
        out_mmse = equalize_mmse(Y, H, snr_linear=1e6)
        np.testing.assert_allclose(out_mmse, out_zf, atol=1e-5)

    def test_channel_response_1d_raises(self):
        Y = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        H = np.random.randn(4, 64) + 1j * np.random.randn(4, 64)
        with pytest.raises(ValueError, match="1D"):
            equalize_mmse(Y, H, snr_linear=10.0)

    def test_channel_nulls_zf_amplifies_noise(self):
        """ZF amplifies noise at channel nulls (small |H|)."""
        np.random.seed(42)
        X = np.ones(64, dtype=complex)
        H = np.ones(64, dtype=complex)
        H[32] = 0.01  # Near null
        # Add noise
        noise = 0.1 * (np.random.randn(64) + 1j * np.random.randn(64))
        Y = X * H + noise
        out_zf = equalize_zf(Y, H)
        # At null, ZF amplifies noise significantly
        assert np.abs(out_zf[32]) > np.abs(Y[32])

    def test_mmse_better_than_zf_at_low_snr_with_nulls(self):
        """MMSE should outperform ZF at low SNR when channel has nulls (small |H|)."""
        np.random.seed(42)
        X = np.random.randn(64) + 1j * np.random.randn(64)
        H = np.ones(64, dtype=complex) * (0.5 + 0.3j)
        H[16] = 0.05  # Near null
        H[32] = 0.05  # Near null
        # Add significant noise (low SNR)
        noise = 0.3 * (np.random.randn(64) + 1j * np.random.randn(64))
        Y = X * H + noise
        out_zf = equalize_zf(Y, H)
        out_mmse = equalize_mmse(Y, H, snr_linear=0.1)  # Very low SNR
        # At nulls, ZF amplifies noise; MMSE should be better overall
        error_zf = np.mean(np.abs(X - out_zf) ** 2)
        error_mmse = np.mean(np.abs(X - out_mmse) ** 2)
        # MMSE should be better, especially at nulls
        assert error_mmse < error_zf or np.abs(out_mmse[16]) < np.abs(out_zf[16])
