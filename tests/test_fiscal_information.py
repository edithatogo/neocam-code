"""The explicit fiscal perspectives retain their frozen paired means and probabilities."""

import csv
from pathlib import Path

import numpy as np
import pytest

from scripts.fiscal_information import fiscal_rows


def test_fiscal_information_reproduces_retained_ledgers() -> None:
    root = Path(__file__).resolve().parents[1]
    with (root / "verification/mixed-policy-fiscal/chhhs-estimate-sensitivity.csv").open() as stream:
        retained = {(r["effect_mode"], r["perspective"], r["policy"]): r for r in csv.DictReader(stream)}
    rows = fiscal_rows(root)
    assert len(rows) == 4 * 7 * (2 + 6)
    for row in rows:
        if row["decision_set"] != "conditional_expansion":
            continue
        target = retained[row["scenario"], row["perspective"], row["policy"]]
        assert row["expected_saving"] == pytest.approx(float(target["mean"]), abs=1e-7)
        assert row["probability_optimal"] == pytest.approx(float(target["probability_optimal"]), abs=1e-9)
        assert float(row["expected_loss"]) + 1e-7 >= float(row["evpi"])
    assert np.isfinite([float(row["evpi"]) for row in rows]).all()
