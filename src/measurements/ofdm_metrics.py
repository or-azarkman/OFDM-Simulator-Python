"""
Single-shot OFDM measurements for validation (AWGN + optional CFO).

Reference TX symbols for EVM are taken from the **ideal** transmitted stream
(no CFO) so that EVM reflects residual rotation when CFO is not corrected.
"""

from __future__ import annotations

import numpy as np

from src.channel import awgn_channel
from src.evm import compute_evm
from src.receiver import (
    compute_ber,
    demodulate_ofdm_symbols,
    fft_ofdm,
    remove_cyclic_prefix,
)
from src.measurements.power import average_power_db, average_power_linear
from src.rf_impairments.cfo import apply_cfo_to_ofdm_stream
from src.transmitter import generate_ofdm_stream, generate_random_bits


def measure_awgn_cfo_once(
    *,
    fft_size: int,
    cp_len: int,
    num_symbols: int,
    modulation: str,
    snr_db: float,
    cfo_subcarrier_fraction: float,
    seed: int | None = 42,
) -> dict[str, float]:
    """
    One Monte Carlo draw: BER and EVM after AWGN, optional CFO (no CFO correction).

    Returns:
        dict with keys: evm_percent, ber, snr_db, cfo_subcarrier_fraction,
        tx_power_linear, tx_power_db, rx_power_linear, rx_power_db
        (TX power on the OFDM stream **before** CFO; RX power on **noisy** time signal)
    """
    if seed is not None:
        np.random.seed(seed)

    bits_per_sub = 2 if modulation.upper() == "QPSK" else 4
    total_bits = num_symbols * fft_size * bits_per_sub
    bits_tx = generate_random_bits(total_bits)
    ofdm_stream = generate_ofdm_stream(
        bits_tx, fft_size, cp_len, modulation, None, None
    )

    tx_power_linear = average_power_linear(ofdm_stream)
    tx_power_db = average_power_db(ofdm_stream)

    tx_no_cp = remove_cyclic_prefix(ofdm_stream, cp_len)
    freq_tx = fft_ofdm(tx_no_cp)

    if cfo_subcarrier_fraction != 0.0:
        ofdm_stream = apply_cfo_to_ofdm_stream(
            ofdm_stream, fft_size, cfo_subcarrier_fraction
        )

    noisy = awgn_channel(ofdm_stream, float(snr_db))
    rx_power_linear = average_power_linear(noisy)
    rx_power_db = average_power_db(noisy)

    ofdm_no_cp = remove_cyclic_prefix(noisy, cp_len)
    freq_rx = fft_ofdm(ofdm_no_cp)

    bits_rx = demodulate_ofdm_symbols(freq_rx, modulation)
    ber = float(compute_ber(bits_tx, bits_rx))
    evm = float(
        compute_evm(
            freq_rx.flatten(),
            freq_tx.flatten(),
            percent=True,
        )
    )

    return {
        "evm_percent": evm,
        "ber": ber,
        "snr_db": float(snr_db),
        "cfo_subcarrier_fraction": float(cfo_subcarrier_fraction),
        "tx_power_linear": tx_power_linear,
        "tx_power_db": tx_power_db,
        "rx_power_linear": rx_power_linear,
        "rx_power_db": rx_power_db,
    }
