"""
Unit tests for AWGN channel model.
"""

import numpy as np
import pytest

from src.channel import awgn_channel


class TestAWGNChannel:
    def test_output_shape(self):
        x = np.random.randn(100) + 1j * np.random.randn(100)
        y = awgn_channel(x, 10.0)
        assert y.shape == x.shape
        assert np.iscomplexobj(y)

    def test_high_snr_near_original(self):
        np.random.seed(123)
        x = np.random.randn(500) + 1j * np.random.randn(500)
        y = awgn_channel(x, 40.0)
        np.testing.assert_allclose(y, x, atol=0.1)

    def test_low_snr_noisy(self):
        np.random.seed(123)
        x = np.ones(100, dtype=complex)
        y = awgn_channel(x, 0.0)
        # At 0 dB, noise power = signal power; correlation should be < 1
        corr = np.abs(np.mean(np.conj(x) * y)) / (np.sqrt(np.mean(np.abs(x) ** 2)) * np.sqrt(np.mean(np.abs(y) ** 2)))
        assert corr < 1.0

    def test_snr_effect(self):
        np.random.seed(42)
        x = np.random.randn(2000) + 1j * np.random.randn(2000)
        y10 = awgn_channel(x, 10.0)
        y20 = awgn_channel(x, 20.0)
        err10 = np.mean(np.abs(x - y10) ** 2)
        err20 = np.mean(np.abs(x - y20) ** 2)
        assert err20 < err10
