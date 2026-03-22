"""
Validation report (PASS/FAIL + reasons).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


@dataclass
class ValidationReport:
    """Outcome of comparing measured metrics to thresholds."""

    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)

    def summary_lines(self) -> list[str]:
        lines = [f"OVERALL: {'PASS' if self.passed else 'FAIL'}"]
        for c in self.checks:
            lines.append(f"  [{c.name}] {'PASS' if c.passed else 'FAIL'} — {c.detail}")
        return lines
