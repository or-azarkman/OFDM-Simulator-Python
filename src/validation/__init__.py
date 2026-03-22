"""
Validation layer: requirements (thresholds) and PASS/FAIL evaluation.
"""

from src.validation.evaluate import (
    evaluate_metrics,
    evaluate_metrics_with_margins,
    load_spec_from_yaml,
)
from src.validation.matrix_config import MatrixCase, load_matrix_cases
from src.validation.report import ValidationReport
from src.validation.spec import ThresholdSpec, ValidationSpec

__all__ = [
    "ThresholdSpec",
    "ValidationSpec",
    "ValidationReport",
    "MatrixCase",
    "evaluate_metrics",
    "evaluate_metrics_with_margins",
    "load_spec_from_yaml",
    "load_matrix_cases",
]
