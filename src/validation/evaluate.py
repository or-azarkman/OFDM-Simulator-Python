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


def requirement_table(report: ValidationReport) -> list[dict[str, Any]]:
    """
    Rows suitable for CSV / markdown: requirement vs limit vs measured vs margin vs PASS.
    """
    rows: list[dict[str, Any]] = []
    m = report.metrics
    for c in report.checks:
        if c.name == "evm_max":
            # limit embedded in detail string is fragile; store in extended API later
            evm = float(m.get("evm_percent", float("nan")))
            rows.append(
                {
                    "requirement": "EVM_RMS",
                    "unit": "%",
                    "measured": evm,
                    "passed": c.passed,
                    "detail": c.detail,
                }
            )
        elif c.name == "ber_max":
            ber = float(m.get("ber", float("nan")))
            rows.append(
                {
                    "requirement": "BER",
                    "unit": "linear",
                    "measured": ber,
                    "passed": c.passed,
                    "detail": c.detail,
                }
            )
    return rows


def evaluate_metrics_with_margins(
    metrics: Mapping[str, float],
    spec: ValidationSpec,
) -> tuple[ValidationReport, dict[str, float]]:
    """
    Same as evaluate_metrics, plus margin fields for CSV reporting.

    Returns:
        report, margins dict with keys like evm_margin_pct, ber_margin (if applicable).
    """
    report = evaluate_metrics(metrics, spec)
    margins: dict[str, float] = {}
    th = spec.thresholds

    if th.max_evm_percent is not None:
        evm = float(metrics.get("evm_percent", float("nan")))
        margins["evm_limit_pct"] = float(th.max_evm_percent)
        margins["evm_margin_pct"] = float(th.max_evm_percent) - evm

    if th.max_ber is not None:
        ber = float(metrics.get("ber", float("nan")))
        margins["ber_limit"] = float(th.max_ber)
        margins["ber_margin"] = float(th.max_ber) - ber

    return report, margins
