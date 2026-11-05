"""Synthetic registry likelihood and contract-decision regression checks."""

import csv
lazy from pathlib import Path

import pytest

from scripts.registry_design import registry


def _registry_inputs(root: Path, *, informative: bool) -> None:
    folder = root / "outputs/v13-refinements"
    folder.mkdir(parents=True)
    counts: list[dict[str, str | float]] = []
    ranks: list[dict[str, str | float]] = []
    for mode in ("attenuated", "null"):
        for policy in ("telephone", "retain_pilot_only"):
            rate = 0.5
            if informative and policy == "retain_pilot_only":
                rate = 0.01 if mode == "attenuated" else 0.99
            counts.extend(
                {
                    "portfolio": "pilot",
                    "activity_id": "contacts_1",
                    "effect_mode": mode,
                    "policy": policy,
                    "metric": metric,
                    "mean": 100000 * (1 if metric == "episodes" else rate),
                }
                for metric in ("episodes", "immediate_transfers", "delayed_rescues", "eventual_transfers")
            )
            ranks.extend(
                {
                    "portfolio": "pilot",
                    "activity_id": "contacts_1",
                    "effect_mode": mode,
                    "decision_set": "conditional_expansion",
                    "perspective": view,
                    "policy": policy,
                    "expected_net_value": 0 if policy == "telephone" else 10 if mode == "attenuated" else -10,
                }
                for view in ("health_system", "societal_bounded")
            )
    for name, records in (("policy_predictive.csv", counts), ("policy_rankings.csv", ranks)):
        with (folder / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(records[0]))
            writer.writeheader()
            writer.writerows(records)


@pytest.mark.parametrize("informative", [False, True])
def test_registry_information_bounds(tmp_path: Path, *, informative: bool) -> None:
    _registry_inputs(tmp_path, informative=informative)
    output = tmp_path / "registry.csv"
    registry(tmp_path, output)
    with output.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 36
    for row in rows:
        information = float(row["per_year_evsi"])
        assert -1e-7 <= information <= 5 + 1e-7
        if informative:
            assert information == pytest.approx(5, abs=1e-5)
        else:
            assert information == pytest.approx(0, abs=1e-7)
