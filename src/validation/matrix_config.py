"""
Load multi-case validation matrices from YAML.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from src.validation.spec import ValidationSpec


@dataclass(frozen=True)
class MatrixCase:
    case_id: str
    spec: ValidationSpec


def load_matrix_cases(path: str | Path) -> tuple[dict[str, Any], list[MatrixCase]]:
    """
    YAML format::

        defaults:
          fft_size: 64
          cp_len: 16
          num_symbols: 300
          seed: 42
        defaults_thresholds:
          max_evm_percent: 40.0
          max_ber: 0.05
        cases:
          - id: my_case
            scenario:
              modulation: QPSK
              snr_db: 18
              cfo_subcarrier_fraction: 0.0
              # optional: cfo_correction_mode: none | genie | cp
              # Legacy: cfo_correction: true → genie
              # optional: phase_noise_mode: none | wiener | symbol
              #           phase_noise_std_rad: float (increment std for wiener; phi std per symbol for symbol)
            thresholds:
              max_evm_percent: 25.0

    Per case, ``scenario`` and ``thresholds`` override defaults.
    """
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")

    defaults = dict(data.get("defaults") or {})
    default_th = dict(data.get("defaults_thresholds") or {})
    raw_cases = data.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("'cases' must be a non-empty list")

    cases: list[MatrixCase] = []
    for i, item in enumerate(raw_cases):
        if not isinstance(item, dict):
            raise ValueError(f"cases[{i}] must be a mapping")
        cid = str(item.get("id") or f"case_{i}")
        scenario = {**defaults, **dict(item.get("scenario") or {})}
        th = {**default_th, **dict(item.get("thresholds") or {})}
        spec = ValidationSpec.from_dict({"thresholds": th, "scenario": scenario})
        cases.append(MatrixCase(case_id=cid, spec=spec))

    meta = {"source": str(path), "num_cases": len(cases)}
    return meta, cases
