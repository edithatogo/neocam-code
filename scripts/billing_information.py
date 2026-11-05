# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Information about avoidable cash with referring-HHS fixed-wing liability known."""

import csv
import math
lazy from pathlib import Path

import numpy as np

from scripts.registry_billing import sequential_cash_rows, signal_likelihood
from src.perspectives_v7 import cost_only_evpi

CASH_HORIZON = 5


def billing_information(root: Path, output: Path) -> None:
    """Integrate independent illustrative cash-capture shares, not legal uncertainty."""
    with (root / "verification/mode-allocation/b287f1135fdf.csv").open(encoding="utf-8") as stream:
        rows = [
            r
            for r in csv.DictReader(stream)
            if r["network"] == "chhhs" and math.isclose(float(r["volume_multiplier"]), 1)
        ]
    records = []
    for steps in (101, 201, 401, 801):
        grid = (np.arange(steps) + 0.5) / steps
        for horizon in (3, 5):
            selected = [r for r in rows if int(r["years"]) == horizon]
            policies = [r["policy"] for r in selected]
            fixed = np.array([float(r["annual_fixed_wing_offset"]) for r in selected])
            other = np.array([float(r["annual_road_offset"]) + float(r["annual_rotary_offset"]) for r in selected])
            spend = np.array([float(r["local_spend"]) for r in selected])
            matrix = horizon * (grid[:, None, None] * fixed + grid[None, :, None] * other) - spend
            mean = matrix.mean(axis=(0, 1))
            information = cost_only_evpi(matrix.reshape(-1, len(policies)))
            records.append({
                "years": horizon,
                "grid_points_per_dimension": steps,
                "policy_before": policies[int(mean.argmax())],
                "perfect_cash_information": information,
                "fixed_wing_capture_information": cost_only_evpi(matrix.mean(axis=1)),
                "road_rotary_capture_information": cost_only_evpi(matrix.mean(axis=0)),
                "possible_policy_after": "|".join(policies[i] for i in np.unique(matrix.argmax(axis=2))),
                "liability_rule": "fixed-wing referring HHS known; cash capture independent uniform scenarios",
            })
    _write(output / "billing-policy-consistent.csv", records)
    _registry_cash(root, output, rows)


def _write(path: Path, rows: list) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _registry_cash(root: Path, output: Path, mode_rows: list) -> None:
    with (root / "verification/mixed-policy-fiscal/chhhs-cash.csv").open(encoding="utf-8") as stream:
        cash = list(csv.DictReader(stream))
    policies = list(dict.fromkeys(r["policy"] for r in cash))
    fixed = np.array([[float(r["fixed_contract_no_care_cash"]) for r in cash if r["policy"] == p] for p in policies])
    offsets = [next(r for r in mode_rows if r["policy"] == p and int(r["years"]) == CASH_HORIZON) for p in policies]
    wing = np.array([float(r["annual_fixed_wing_offset"]) for r in offsets])
    other = np.array([float(r["annual_road_offset"]) + float(r["annual_rotary_offset"]) for r in offsets])
    np.testing.assert_allclose(fixed[:, :5].sum(axis=1), [-float(r["local_spend"]) for r in offsets], atol=1e-7)
    with (root / "outputs/v13-refinements/policy_predictive.csv").open(encoding="utf-8") as stream:
        counts = {
            (r["policy"], r["effect_mode"], r["metric"]): float(r["mean"])
            for r in csv.DictReader(stream)
            if r["portfolio"] == "chhhs" and r["activity_id"] == "contacts_1"
        }
    volume = counts["retain_pilot_expand_obsbot", "attenuated", "episodes"]
    rates = np.array([
        [
            counts[p, m, "eventual_transfers"] / counts[p, m, "episodes"]
            for p in ("telephone", "retain_pilot_expand_obsbot")
        ]
        for m in ("attenuated", "null")
    ])
    records = []
    for steps in (9, 17, 33):
        grid = (np.arange(steps) + 0.5) / steps
        flows = np.array([
            [fixed + effect * (a * wing + b * other)[:, None] for effect in (1, 0)] for a in grid for b in grid
        ])
        for years in (1, 2, 3):
            cost = 1500 + volume * years * 0.8 * (25 + 0.95 * 10)
            records.extend([
                {
                    "grid_points_per_dimension": steps,
                    "years": row[0],
                    "billing_known": row[1],
                    "gross_sample_value": row[2],
                    "cost_of_waiting": row[3],
                    "break_even_budget": row[4],
                    "study_cost": cost,
                    "net_value": row[4] - cost,
                    "perspective": "chhhs_cash",
                    "horizon_years": CASH_HORIZON,
                    "basis": (
                        "fixed-wing liability known; independent uniform capture; equal effect prior; "
                        "point programme costs; legacy known-baseline signal"
                    ),
                }
                for row in sequential_cash_rows(
                    flows, years, policies.index("retain_pilot_only"), signal_likelihood(rates, volume, years)
                )
            ])
    _write(output / "registry-cash-policy-consistent.csv", records)
