"""
Unit tests for Error Vector Magnitude (EVM) computation.
"""

import numpy as np
import pytest

from src.evm import compute_evm


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
