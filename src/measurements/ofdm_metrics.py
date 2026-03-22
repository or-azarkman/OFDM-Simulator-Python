"""
Single-shot OFDM measurements for validation (AWGN + optional CFO).

Reference TX symbols for EVM are taken from the **ideal** transmitted stream
(no CFO). With ``cfo_correction_mode="genie"``, the RX applies a **known-CFO**
inverse ramp. With ``"cp"``, CFO is **estimated** from CP correlation (Moose-style)
then removed. Otherwise no CFO correction.
"""

from __future__ import annotations

from typing import Any, Mapping

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
from src.rf_impairments.cfo import (
    apply_cfo_to_ofdm_stream,
    estimate_cfo_subcarrier_fraction_from_cp,
    remove_cfo_from_ofdm_stream,
)
from src.transmitter import generate_ofdm_stream, generate_random_bits


def parse_cfo_correction_mode(scenario: Mapping[str, Any]) -> str:
    """
    YAML scenario keys:

    - ``cfo_correction_mode``: ``none`` | ``genie`` | ``cp`` (preferred)
    - Legacy: ``cfo_correction: true`` → ``genie``
    """
    raw = scenario.get("cfo_correction_mode")
    if isinstance(raw, str):
        m = raw.strip().lower()
        if m in ("none", "genie", "cp"):
            return m
    if scenario.get("cfo_correction") is True:
        return "genie"
    return "none"


def measure_awgn_cfo_once(
    *,
    fft_size: int,
    cp_len: int,
    num_symbols: int,
    modulation: str,
    snr_db: float,
    cfo_subcarrier_fraction: float,
    seed: int | None = 42,
    cfo_correction_mode: str = "none",
) -> dict[str, float]:
    """
    One Monte Carlo draw: BER and EVM after AWGN, optional CFO.

    ``cfo_correction_mode``:
      - ``none`` — no CFO removal (default).
      - ``genie`` — use true ``cfo_subcarrier_fraction`` (oracle bound).
      - ``cp`` — estimate CFO from CP self-correlation, then remove.

    Returns:
        dict with keys: evm_percent, ber, snr_db, cfo_subcarrier_fraction,
        cfo_correction (0.0 or 1.0 if any correction applied),
        cfo_correction_mode (0=none, 1=genie, 2=cp),
        cfo_estimated_subcarrier_fraction (NaN or estimate when mode is cp),
        tx_power_linear, tx_power_db, rx_power_linear, rx_power_db
        (TX power on the OFDM stream **before** CFO; RX power on **noisy** time signal
        **before** CFO removal — i.e. at the channel output)
    """
    mode = (cfo_correction_mode or "none").strip().lower()
    if mode not in ("none", "genie", "cp"):
        raise ValueError(f"Invalid cfo_correction_mode: {cfo_correction_mode!r}")
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

    eps_hat: float | None = None
    if cfo_subcarrier_fraction != 0.0:
        if mode == "genie":
            noisy = remove_cfo_from_ofdm_stream(
                noisy, fft_size, cfo_subcarrier_fraction
            )
        elif mode == "cp":
            eps_est = estimate_cfo_subcarrier_fraction_from_cp(
                noisy, fft_size, cp_len
            )
            eps_hat = float(eps_est)
            noisy = remove_cfo_from_ofdm_stream(noisy, fft_size, eps_hat)

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

    corrected = (
        cfo_subcarrier_fraction != 0.0 and mode in ("genie", "cp")
    )
    mode_code = {"none": 0.0, "genie": 1.0, "cp": 2.0}[mode]

    return {
        "evm_percent": evm,
        "ber": ber,
        "snr_db": float(snr_db),
        "cfo_subcarrier_fraction": float(cfo_subcarrier_fraction),
        "cfo_correction": 1.0 if corrected else 0.0,
        "cfo_correction_mode": mode_code,
        "cfo_estimated_subcarrier_fraction": eps_hat,
        "tx_power_linear": tx_power_linear,
        "tx_power_db": tx_power_db,
        "rx_power_linear": rx_power_linear,
        "rx_power_db": rx_power_db,
    }
