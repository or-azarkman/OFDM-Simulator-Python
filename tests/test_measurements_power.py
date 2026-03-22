"""Power metrics (normalized average power)."""

import numpy as np
import pytest

from src.measurements.power import average_power_db, average_power_linear


def test_unit_constant_zero_db():
    x = np.ones(100, dtype=complex)
    assert average_power_linear(x) == pytest.approx(1.0)
    assert average_power_db(x) == pytest.approx(0.0, abs=1e-9)


def test_average_power_db_on_scaled_noise():
    rng = np.random.default_rng(0)
    x = (rng.standard_normal(500) + 1j * rng.standard_normal(500)) * 0.5
    p_lin = average_power_linear(x)
    assert p_lin > 0.2
    assert average_power_db(x) == pytest.approx(10.0 * np.log10(p_lin + 1e-30))
