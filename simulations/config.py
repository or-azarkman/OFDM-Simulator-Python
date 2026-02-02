"""
config.py

Simulation configuration and reproducibility.

Centralizes parameters for BER, EVM, and constellation runs so that
experiments are reproducible and easy to vary for different scenarios.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_multipath_taps() -> np.ndarray:
    """Default 3-tap channel: direct path + two delayed paths."""
    return np.array([1.0, 0.0, 0.4 * np.exp(1j * 0.5)], dtype=complex)


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
    channel_type: str = "awgn"
    equalize: str = "zf"
    multipath_taps: Union[Sequence[complex], np.ndarray, None] = field(
        default_factory=_default_multipath_taps
    )
    use_pilots: bool = False
    pilot_spacing: int = 8
    num_pilots: Optional[int] = None

    def __post_init__(self) -> None:
        if isinstance(self.results_dir, str):
            self.results_dir = Path(self.results_dir)
        if self.multipath_taps is not None:
            self.multipath_taps = np.asarray(self.multipath_taps, dtype=complex)
        if self.random_seed is not None:
            np.random.seed(self.random_seed)

    @property
    def run_dir(self) -> Path:
        base = f"{self.num_symbols}_symbols"
        if self.channel_type.lower() == "multipath":
            base = f"{base}_multipath"
            eq = (self.equalize or "zf").lower()
            if eq == "mmse":
                base = f"{base}_mmse"
            elif eq == "zf":
                base = f"{base}_zf"
            if getattr(self, "use_pilots", False):
                base = f"{base}_pilots"
        return self.results_dir / base

    @property
    def images_dir(self) -> Path:
        """Subdirectory for plots."""
        return self.run_dir / "images"

    def ensure_dirs(self) -> None:
        """Create results and images directories if needed."""
        self.images_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def summary_dir() -> Path:
        """Get the summary directory path."""
        return _project_root() / "results" / "summary"

    @staticmethod
    def summary_ber_dir() -> Path:
        """Get the BER summary subdirectory."""
        d = SimulationConfig.summary_dir() / "ber"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @staticmethod
    def summary_evm_dir() -> Path:
        """Get the EVM summary subdirectory."""
        d = SimulationConfig.summary_dir() / "evm"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @staticmethod
    def summary_constellation_dir() -> Path:
        """Get the constellation summary subdirectory."""
        d = SimulationConfig.summary_dir() / "constellation"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @staticmethod
    def summary_pilots_dir() -> Path:
        """Get the pilots summary subdirectory."""
        d = SimulationConfig.summary_dir() / "pilots"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @staticmethod
    def summary_docs_dir() -> Path:
        """Get the docs summary subdirectory."""
        d = SimulationConfig.summary_dir() / "docs"
        d.mkdir(parents=True, exist_ok=True)
        return d
