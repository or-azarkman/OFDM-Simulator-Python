"""
RF impairment models for baseband OFDM validation (digital equivalent of RF effects).

This package applies effects in the **complex baseband** domain before or around
the existing AWGN/multipath channel. It is designed for a validation / test flow,
not for a full RF circuit simulator.
"""

from src.rf_impairments.chain import RFImpairmentChain
from src.rf_impairments.cfo import (
    apply_cfo_to_ofdm_stream,
    estimate_cfo_subcarrier_fraction_from_cp,
    remove_cfo_from_ofdm_stream,
)
from src.rf_impairments.phase_noise import (
    apply_independent_phase_noise_per_ofdm_symbol,
    apply_wiener_phase_noise_to_stream,
)

__all__ = [
    "RFImpairmentChain",
    "apply_cfo_to_ofdm_stream",
    "remove_cfo_from_ofdm_stream",
    "estimate_cfo_subcarrier_fraction_from_cp",
    "apply_wiener_phase_noise_to_stream",
    "apply_independent_phase_noise_per_ofdm_symbol",
]
