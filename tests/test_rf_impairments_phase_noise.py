"""Phase noise impairments: identity, shape, EVM degradation."""

import numpy as np
import pytest

from src.measurements.ofdm_metrics import measure_awgn_cfo_once
from src.rf_impairments.phase_noise import (
    apply_independent_phase_noise_per_ofdm_symbol,
    apply_wiener_phase_noise_to_stream,
)


def test_wiener_zero_is_identity():
    rng = np.random.default_rng(0)
    x = (rng.standard_normal((3, 40)) + 1j * rng.standard_normal((3, 40))).astype(np.complex128)
    y = apply_wiener_phase_noise_to_stream(x, 0.0)
    np.testing.assert_allclose(y, x, rtol=0, atol=0)


def test_symbol_phase_zero_is_identity():
    x = np.ones((4, 24), dtype=np.complex128)
    y = apply_independent_phase_noise_per_ofdm_symbol(x, fft_size=16, cp_len=8, sigma_phi_rad=0.0)
    np.testing.assert_allclose(y, x)


def test_symbol_phase_preserves_shape():
    rng = np.random.default_rng(1)
    x = rng.standard_normal((5, 80)) + 1j * rng.standard_normal((5, 80))
    y = apply_independent_phase_noise_per_ofdm_symbol(
        x.astype(np.complex128), fft_size=64, cp_len=16, sigma_phi_rad=0.1, rng=rng
    )
    assert y.shape == x.shape


def test_symbol_phase_noise_raises_evm():
    """Strong per-symbol phase noise must dominate EVM vs AWGN at moderate SNR."""
    m = measure_awgn_cfo_once(
        fft_size=32,
        cp_len=8,
        num_symbols=120,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.0,
        seed=42,
        phase_noise_mode="symbol",
        phase_noise_std_rad=0.18,
    )
    assert m["evm_percent"] > 12.0


def test_parse_phase_noise_invalid_mode_raises():
    from src.measurements.ofdm_metrics import parse_phase_noise

    with pytest.raises(ValueError):
        parse_phase_noise({"phase_noise_mode": "invalid", "phase_noise_std_rad": 0.1})
