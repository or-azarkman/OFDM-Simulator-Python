"""
Validation layer: requirements (thresholds) and PASS/FAIL evaluation.
"""

from src.validation.evaluate import evaluate_metrics, load_spec_from_yaml
from src.validation.report import ValidationReport
from src.validation.spec import ThresholdSpec, ValidationSpec

__all__ = [
    "ThresholdSpec",
    "ValidationSpec",
    "ValidationReport",
    "evaluate_metrics",
    "load_spec_from_yaml",
]
