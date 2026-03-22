"""CFO correction path in measure_awgn_cfo_once (known CFO / genie)."""

from src.measurements.ofdm_metrics import measure_awgn_cfo_once


def test_measure_without_correction_high_ber_with_cfo():
    m = measure_awgn_cfo_once(
        fft_size=64,
        cp_len=16,
        num_symbols=200,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.04,
        seed=42,
        cfo_correction=False,
    )
    assert m["ber"] > 0.1  # uncorrected CFO destroys link


def test_measure_with_correction_restores_link():
    m = measure_awgn_cfo_once(
        fft_size=64,
        cp_len=16,
        num_symbols=200,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.04,
        seed=42,
        cfo_correction=True,
    )
    assert m["cfo_correction"] == 1.0
    assert m["ber"] < 0.02
    assert m["evm_percent"] < 25.0


def test_cfo_correction_flag_zero_when_disabled():
    m = measure_awgn_cfo_once(
        fft_size=32,
        cp_len=8,
        num_symbols=50,
        modulation="QPSK",
        snr_db=18.0,
        cfo_subcarrier_fraction=0.0,
        seed=0,
        cfo_correction=True,
    )
    assert m["cfo_correction"] == 0.0
