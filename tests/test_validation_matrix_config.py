"""Validation matrix YAML loading and loose end-to-end case."""

from pathlib import Path

import numpy as np
import pytest

from src.measurements.ofdm_metrics import measure_awgn_cfo_once
from src.validation.evaluate import evaluate_metrics_with_margins
from src.validation.matrix_config import load_matrix_cases


def test_load_default_matrix_file():
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "validation" / "test_matrix_default.yaml"
    if not p.is_file():
        pytest.skip("test_matrix_default.yaml missing")
    meta, cases = load_matrix_cases(p)
    assert meta["num_cases"] >= 1
    assert len(cases) >= 1
    assert cases[0].case_id


def test_measure_includes_power_fields():
    m = measure_awgn_cfo_once(
        fft_size=32,
        cp_len=8,
        num_symbols=20,
        modulation="QPSK",
        snr_db=20.0,
        cfo_subcarrier_fraction=0.0,
        seed=0,
    )
    assert "tx_power_db" in m and "rx_power_db" in m
    assert np.isfinite(m["tx_power_db"]) and np.isfinite(m["rx_power_db"])


def test_loose_matrix_case_passes(tmp_path):
    """Regression: single very loose case must PASS (deterministic)."""
    p = tmp_path / "matrix.yaml"
    p.write_text(
        """
defaults:
  fft_size: 32
  cp_len: 8
  num_symbols: 64
  seed: 0
defaults_thresholds:
  max_evm_percent: 99.0
  max_ber: 1.0
cases:
  - id: loose_smoke
    scenario:
      modulation: QPSK
      snr_db: 18.0
      cfo_subcarrier_fraction: 0.0
    thresholds:
      max_evm_percent: 99.0
      max_ber: 1.0
""",
        encoding="utf-8",
    )
    _, cases = load_matrix_cases(p)
    spec = cases[0].spec
    sc = spec.scenario
    metrics = measure_awgn_cfo_once(
        fft_size=int(sc["fft_size"]),
        cp_len=int(sc["cp_len"]),
        num_symbols=int(sc["num_symbols"]),
        modulation=str(sc["modulation"]),
        snr_db=float(sc["snr_db"]),
        cfo_subcarrier_fraction=float(sc["cfo_subcarrier_fraction"]),
        seed=int(sc["seed"]),
    )
    report, margins = evaluate_metrics_with_margins(metrics, spec)
    assert report.passed
    assert "evm_margin_pct" in margins
