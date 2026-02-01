"""
Unit tests for theoretical BER (QPSK, 16-QAM in AWGN).
"""

import numpy as np
import pytest

from src.theory import ber_qpsk_awgn, ber_16qam_awgn, theoretical_ber


class TestTheoryQPSK:
    def test_high_snr_low_ber(self):
        ber = ber_qpsk_awgn(np.array([20.0]))
        assert ber[0] < 1e-6

    def test_low_snr_high_ber(self):
        ber = ber_qpsk_awgn(np.array([0.0]))
        assert 0.01 < ber[0] < 0.5

    def test_vector_input(self):
        snr = np.array([0, 5, 10, 15, 20])
        out = ber_qpsk_awgn(snr)
        assert out.shape == (5,)
        assert np.all(np.diff(out) <= 0)


class TestTheory16QAM:
    def test_high_snr_low_ber(self):
        ber = ber_16qam_awgn(np.array([25.0]))
        assert ber[0] < 1e-4

    def test_monotonic(self):
        snr = np.linspace(0, 20, 10)
        out = ber_16qam_awgn(snr)
        assert np.all(np.diff(out) <= 0)


class TestTheoreticalBER:
    def test_qpsk(self):
        snr = np.array([10.0])
        np.testing.assert_array_almost_equal(
            theoretical_ber(snr, "QPSK"), ber_qpsk_awgn(snr)
        )

    def test_16qam(self):
        snr = np.array([10.0])
        np.testing.assert_array_almost_equal(
            theoretical_ber(snr, "16QAM"), ber_16qam_awgn(snr)
        )

    def test_unsupported_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            theoretical_ber(np.array([10.0]), "64QAM")
