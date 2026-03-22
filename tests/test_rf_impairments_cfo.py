"""Tests for CFO impairment (phase continuity, zero CFO identity)."""

import numpy as np
import pytest

from src.rf_impairments.cfo import apply_cfo_to_ofdm_stream


def test_cfo_zero_is_identity():
    rng = np.random.default_rng(0)
    x = (rng.standard_normal((5, 80)) + 1j * rng.standard_normal((5, 80))).astype(np.complex128)
    y = apply_cfo_to_ofdm_stream(x, fft_size=64, cfo_subcarrier_fraction=0.0)
    np.testing.assert_allclose(y, x)


def test_cfo_preserves_shape():
    x = np.ones((3, 16), dtype=complex)
    y = apply_cfo_to_ofdm_stream(x, fft_size=8, cfo_subcarrier_fraction=0.01)
    assert y.shape == x.shape


def test_cfo_phase_increases_monotonically_on_constant_input():
    n = 32
    x = np.ones((1, n), dtype=complex)
    y = apply_cfo_to_ofdm_stream(x, fft_size=16, cfo_subcarrier_fraction=0.05)
    phases = np.unwrap(np.angle(y.flatten()))
    assert np.all(np.diff(phases) > 0)
