"""Independent cash-flow examples for delayed information decisions."""

import numpy as np
import pytest

from scripts.registry_billing import sequential_cash_rows


def test_registry_pays_only_for_choices_after_results() -> None:
    flows = np.array([
        [
            [[0.0] * 7, [-3.0, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]],
            [[0.0] * 7, [-3.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0]],
        ]
    ])
    rows = sequential_cash_rows(flows, 1, 1, np.eye(2))
    for row in rows:
        assert row[2] == pytest.approx(4)
        assert row[3] == pytest.approx(3)
        assert row[4] == pytest.approx(1)
    uninformed = sequential_cash_rows(flows, 1, 1, np.full((2, 2), 0.5))
    assert all(row[2] == pytest.approx(0) for row in uninformed)
    too_late = sequential_cash_rows(flows, 5, 1, np.eye(2))
    assert all(row[2] == pytest.approx(0) for row in too_late)
