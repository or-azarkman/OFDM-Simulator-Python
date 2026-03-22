"""
Measurement utilities for validation runs (EVM, BER, etc.).

Wraps existing PHY metrics with a small, stable API for automation and reporting.
"""

from src.measurements.ofdm_metrics import measure_awgn_cfo_once
from src.measurements.power import average_power_db, average_power_linear

__all__ = [
    "measure_awgn_cfo_once",
    "average_power_db",
    "average_power_linear",
]
