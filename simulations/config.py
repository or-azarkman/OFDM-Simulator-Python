"""
config.py

Simulation configuration and reproducibility.

Centralizes parameters for BER and constellation runs so that
experiments are reproducible and easy to vary for different scenarios.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np


def _project_root() -> Path:
    """Project root = parent of simulations/."""
    return Path(__file__).resolve().parent.parent


@dataclass
class SimulationConfig:
    """OFDM simulation parameters."""

    fft_size: int = 64
    cp_len: int = 16
    num_symbols: int = 5000
    monte_carlo_trials: int = 50
    snr_range_db: np.ndarray = field(default_factory=lambda: np.arange(0, 21, 2))
    random_seed: Optional[int] = 42
    results_dir: Path = field(default_factory=lambda: _project_root() / "results")

    def __post_init__(self) -> None:
        if isinstance(self.results_dir, str):
            self.results_dir = Path(self.results_dir)
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

    @property
    def run_dir(self) -> Path:
        """Directory for this run: results/{num_symbols}_symbols/."""
        return self.results_dir / f"{self.num_symbols}_symbols"

    @property
    def images_dir(self) -> Path:
        """Subdirectory for plots."""
        return self.run_dir / "images"

    def ensure_dirs(self) -> None:
        """Create results and images directories if needed."""
        self.images_dir.mkdir(parents=True, exist_ok=True)
