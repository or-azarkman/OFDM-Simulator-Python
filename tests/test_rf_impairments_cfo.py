"""Tests for CFO impairment (phase continuity, zero CFO identity)."""

import numpy as np
import pytest

from src.rf_impairments.cfo import (
    apply_cfo_to_ofdm_stream,
    estimate_cfo_subcarrier_fraction_from_cp,
    remove_cfo_from_ofdm_stream,
)


def test_cfo_zero_is_identity():
    rng = np.random.default_rng(0)
    x = (rng.standard_normal((5, 80)) + 1j * rng.standard_normal((5, 80))).astype(np.complex128)
    y = apply_cfo_to_ofdm_stream(x, fft_size=64, cfo_subcarrier_fraction=0.0)
    np.testing.assert_allclose(y, x)


def test_cfo_preserves_shape():
    x = np.ones((3, 16), dtype=complex)
    y = apply_cfo_to_ofdm_stream(x, fft_size=8, cfo_subcarrier_fraction=0.01)
    assert y.shape == x.shape


def test_cp_estimate_matches_applied_cfo():
    """CP must duplicate the last cp_len samples of the useful part (OFDM property)."""
    rng = np.random.default_rng(2)
    fft_size = 32
    cp_len = 8
    eps = 0.04
    rows = []
    for _ in range(12):
        body = (rng.standard_normal(fft_size) + 1j * rng.standard_normal(fft_size)).astype(
            np.complex128
        )
        cp = body[-cp_len:]
        rows.append(np.concatenate([cp, body]))
    x = np.stack(rows, axis=0)
    y = apply_cfo_to_ofdm_stream(x, fft_size=fft_size, cfo_subcarrier_fraction=eps)
    hat = estimate_cfo_subcarrier_fraction_from_cp(y, fft_size, cp_len)
    np.testing.assert_allclose(hat, eps, rtol=1e-9, atol=1e-10)


def test_remove_cfo_inverts_apply():
    rng = np.random.default_rng(1)
    x = (rng.standard_normal((4, 48)) + 1j * rng.standard_normal((4, 48))).astype(np.complex128)
    eps = 0.04
    fft_size = 32
    y = apply_cfo_to_ofdm_stream(x, fft_size=fft_size, cfo_subcarrier_fraction=eps)
    z = remove_cfo_from_ofdm_stream(y, fft_size=fft_size, cfo_subcarrier_fraction=eps)
    np.testing.assert_allclose(z, x, rtol=1e-10, atol=1e-12)


def test_cfo_phase_increases_monotonically_on_constant_input():
    n = 32
    x = np.ones((1, n), dtype=complex)
    y = apply_cfo_to_ofdm_stream(x, fft_size=16, cfo_subcarrier_fraction=0.05)
    phases = np.unwrap(np.angle(y.flatten()))
    assert np.all(np.diff(phases) > 0)
