"""
Evaluate measured metrics against a ValidationSpec.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from src.validation.report import CheckResult, ValidationReport
from src.validation.spec import ValidationSpec


def load_spec_from_yaml(path: str | Path) -> ValidationSpec:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return ValidationSpec.from_dict(data)


def evaluate_metrics(
    metrics: Mapping[str, float],
    spec: ValidationSpec,
) -> ValidationReport:
    """
    Compare metrics to thresholds. Unknown keys in metrics are ignored.

    Supported checks:
      - max_evm_percent  vs  metrics["evm_percent"]
      - max_ber          vs  metrics["ber"]
    """
    checks: list[CheckResult] = []
    th = spec.thresholds

    if th.max_evm_percent is not None:
        evm = float(metrics.get("evm_percent", float("nan")))
        ok = evm <= th.max_evm_percent
        checks.append(
            CheckResult(
                name="evm_max",
                passed=ok,
                detail=f"EVM={evm:.3f}% (limit {th.max_evm_percent}%)",
            )
        )

    if th.max_ber is not None:
        ber = float(metrics.get("ber", float("nan")))
        ok = ber <= th.max_ber
        checks.append(
            CheckResult(
                name="ber_max",
                passed=ok,
                detail=f"BER={ber:.6e} (limit {th.max_ber})",
            )
        )

    overall = all(c.passed for c in checks) if checks else True
    return ValidationReport(
        passed=overall,
        checks=checks,
        metrics=dict(metrics),
    )


def report_to_dict(report: ValidationReport) -> dict[str, Any]:
    return {
        "passed": report.passed,
        "metrics": report.metrics,
        "checks": [
            {"name": c.name, "passed": c.passed, "detail": c.detail}
            for c in report.checks
        ],
    }
