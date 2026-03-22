"""
Structured validation specification (thresholds + scenario metadata).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ThresholdSpec:
    """Pass/fail gates (None = skip check)."""

    max_evm_percent: float | None = None
    max_ber: float | None = None


@dataclass(frozen=True)
class ValidationSpec:
    """Full validation spec: thresholds + optional scenario knobs."""

    thresholds: ThresholdSpec
    scenario: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "ValidationSpec":
        th = data.get("thresholds") or {}
        thresholds = ThresholdSpec(
            max_evm_percent=th.get("max_evm_percent"),
            max_ber=th.get("max_ber"),
        )
        scenario = dict(data.get("scenario") or {})
        return ValidationSpec(thresholds=thresholds, scenario=scenario)
