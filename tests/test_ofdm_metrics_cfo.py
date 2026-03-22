"""CFO correction path in measure_awgn_cfo_once (genie / CP estimate)."""

import numpy as np

from src.measurements.ofdm_metrics import measure_awgn_cfo_once, parse_cfo_correction_mode


def test_parse_cfo_correction_mode_helpers():
    assert parse_cfo_correction_mode({}) == "none"
    assert parse_cfo_correction_mode({"cfo_correction": True}) == "genie"
    assert parse_cfo_correction_mode({"cfo_correction_mode": "cp"}) == "cp"
    assert parse_cfo_correction_mode({"cfo_correction_mode": "GENIE"}) == "genie"


def test_measure_without_correction_high_ber_with_cfo():
    m = measure_awgn_cfo_once(
        fft_size=64,
        cp_len=16,
        num_symbols=200,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.04,
        seed=42,
        cfo_correction_mode="none",
    )
    assert m["ber"] > 0.1  # uncorrected CFO destroys link


def test_measure_with_genie_restores_link():
    m = measure_awgn_cfo_once(
        fft_size=64,
        cp_len=16,
        num_symbols=200,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.04,
        seed=42,
        cfo_correction_mode="genie",
    )
    assert m["cfo_correction"] == 1.0
    assert m["cfo_correction_mode"] == 1.0
    assert m["cfo_estimated_subcarrier_fraction"] is None
    assert m["ber"] < 0.02
    assert m["evm_percent"] < 25.0


def test_measure_with_cp_estimate_restores_link():
    m = measure_awgn_cfo_once(
        fft_size=64,
        cp_len=16,
        num_symbols=200,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.04,
        seed=42,
        cfo_correction_mode="cp",
    )
    assert m["cfo_correction"] == 1.0
    assert m["cfo_correction_mode"] == 2.0
    assert m["cfo_estimated_subcarrier_fraction"] is not None
    assert np.isclose(
        m["cfo_estimated_subcarrier_fraction"], 0.04, rtol=0.05, atol=0.002
    )
    assert m["ber"] < 0.02
    assert m["evm_percent"] < 25.0


def test_cfo_correction_flag_zero_when_no_cfo():
    m = measure_awgn_cfo_once(
        fft_size=32,
        cp_len=8,
        num_symbols=50,
        modulation="QPSK",
        snr_db=18.0,
        cfo_subcarrier_fraction=0.0,
        seed=0,
        cfo_correction_mode="genie",
    )
    assert m["cfo_correction"] == 0.0
