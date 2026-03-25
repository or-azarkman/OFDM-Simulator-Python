"""
Single-shot OFDM measurements for validation (AWGN + optional CFO + optional phase noise).

Reference TX symbols for EVM are taken from the **ideal** transmitted stream
(no CFO). With ``cfo_correction_mode="genie"``, the RX applies a **known-CFO**
inverse ramp. With ``"cp"``, CFO is **estimated** from CP correlation (Moose-style)
then removed. Otherwise no CFO correction.

**Phase noise** (optional) is applied **after** CFO and **before** AWGN: multiplicative
``exp(j φ)`` on time-domain samples (Wiener or per-OFDM-symbol — see
``parse_phase_noise``).
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
from src.rf_impairments.phase_noise import (
    apply_independent_phase_noise_per_ofdm_symbol,
    apply_wiener_phase_noise_to_stream,
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


def parse_phase_noise(scenario: Mapping[str, Any]) -> tuple[str, float]:
    """
    YAML scenario keys:

    - ``phase_noise_mode``: ``none`` | ``wiener`` | ``symbol``
    - ``phase_noise_std_rad``: strength (meaning depends on mode):

      - ``wiener`` — standard deviation of the **phase increment** per sample (rad).
      - ``symbol`` — standard deviation of a **single random phase** per OFDM symbol (rad).

    If mode is ``none`` or ``phase_noise_std_rad`` is 0, phase noise is disabled.
    """
    mode = str(scenario.get("phase_noise_mode", "none")).strip().lower()
    if mode not in ("none", "wiener", "symbol"):
        raise ValueError(f"Invalid phase_noise_mode: {scenario.get('phase_noise_mode')!r}")
    std = float(scenario.get("phase_noise_std_rad", 0.0))
    if mode == "none" or std == 0.0:
        return ("none", 0.0)
    return (mode, std)


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
    phase_noise_mode: str = "none",
    phase_noise_std_rad: float = 0.0,
) -> dict[str, float]:
    """
    One Monte Carlo draw: BER and EVM after AWGN, optional CFO, optional phase noise.

    ``cfo_correction_mode``:
      - ``none`` — no CFO removal (default).
      - ``genie`` — use true ``cfo_subcarrier_fraction`` (oracle bound).
      - ``cp`` — estimate CFO from CP self-correlation, then remove.

    ``phase_noise_mode`` / ``phase_noise_std_rad``: see :func:`parse_phase_noise`.
    Phase noise is applied after CFO, before AWGN.

    Returns:
        dict with keys: evm_percent, ber, snr_db, cfo_subcarrier_fraction,
        cfo_correction (0.0 or 1.0 if any correction applied),
        cfo_correction_mode (0=none, 1=genie, 2=cp),
        cfo_estimated_subcarrier_fraction (NaN or estimate when mode is cp),
        phase_noise_mode (0=none, 1=wiener, 2=symbol),
        phase_noise_std_rad,
        tx_power_linear, tx_power_db, rx_power_linear, rx_power_db
        (TX power on the OFDM stream **before** CFO; RX power on **noisy** time signal
        **before** CFO removal — i.e. at the channel output)
    """
    mode = (cfo_correction_mode or "none").strip().lower()
    if mode not in ("none", "genie", "cp"):
        raise ValueError(f"Invalid cfo_correction_mode: {cfo_correction_mode!r}")
    pn_mode = (phase_noise_mode or "none").strip().lower()
    if pn_mode not in ("none", "wiener", "symbol"):
        raise ValueError(f"Invalid phase_noise_mode: {phase_noise_mode!r}")
    if pn_mode == "none" or phase_noise_std_rad == 0.0:
        pn_mode = "none"
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

    if pn_mode == "wiener":
        ofdm_stream = apply_wiener_phase_noise_to_stream(
            ofdm_stream, float(phase_noise_std_rad)
        )
    elif pn_mode == "symbol":
        ofdm_stream = apply_independent_phase_noise_per_ofdm_symbol(
            ofdm_stream, fft_size, cp_len, float(phase_noise_std_rad)
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
    pn_code = {"none": 0.0, "wiener": 1.0, "symbol": 2.0}[pn_mode]
    pn_std_out = float(phase_noise_std_rad) if pn_mode != "none" else 0.0

    return {
        "evm_percent": evm,
        "ber": ber,
        "snr_db": float(snr_db),
        "cfo_subcarrier_fraction": float(cfo_subcarrier_fraction),
        "cfo_correction": 1.0 if corrected else 0.0,
        "cfo_correction_mode": mode_code,
        "cfo_estimated_subcarrier_fraction": eps_hat,
        "phase_noise_mode": pn_code,
        "phase_noise_std_rad": pn_std_out,
        "tx_power_linear": tx_power_linear,
        "tx_power_db": tx_power_db,
        "rx_power_linear": rx_power_linear,
        "rx_power_db": rx_power_db,
    }
