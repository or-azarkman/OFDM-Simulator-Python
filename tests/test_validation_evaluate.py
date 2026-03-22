"""Validation spec loading and PASS/FAIL evaluation."""

from pathlib import Path

import pytest

from src.validation.evaluate import evaluate_metrics, load_spec_from_yaml
from src.validation.spec import ThresholdSpec, ValidationSpec


def test_evaluate_pass_and_fail():
    spec = ValidationSpec(
        thresholds=ThresholdSpec(max_evm_percent=10.0, max_ber=0.01),
    )
    r_ok = evaluate_metrics({"evm_percent": 5.0, "ber": 1e-4}, spec)
    assert r_ok.passed
    r_fail = evaluate_metrics({"evm_percent": 50.0, "ber": 1e-4}, spec)
    assert not r_fail.passed


def test_load_default_smoke_yaml():
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "validation" / "default_smoke.yaml"
    if not p.is_file():
        pytest.skip("default_smoke.yaml not found")
    spec = load_spec_from_yaml(p)
    assert spec.thresholds.max_evm_percent is not None
