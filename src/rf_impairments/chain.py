"""
Composable impairment chain: apply a sequence of transformations to a signal.

Each callable must accept ``(signal: np.ndarray) -> np.ndarray`` and preserve shape.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeAlias

import numpy as np

ImpairmentFn: TypeAlias = Callable[[np.ndarray], np.ndarray]


class RFImpairmentChain:
    """Ordered list of impairments applied in sequence."""

    def __init__(self, steps: Sequence[ImpairmentFn] | None = None) -> None:
        self._steps: list[ImpairmentFn] = list(steps) if steps else []

    def add(self, fn: ImpairmentFn) -> RFImpairmentChain:
        self._steps.append(fn)
        return self

    def apply(self, signal: np.ndarray) -> np.ndarray:
        out = np.asarray(signal, dtype=complex)
        for fn in self._steps:
            out = fn(out)
        return out

    def __len__(self) -> int:
        return len(self._steps)
