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

__all__ = [
    "RFImpairmentChain",
    "apply_cfo_to_ofdm_stream",
    "remove_cfo_from_ofdm_stream",
    "estimate_cfo_subcarrier_fraction_from_cp",
]
