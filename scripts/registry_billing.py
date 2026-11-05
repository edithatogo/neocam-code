# ruff: ignore[implicit-namespace-package] -- analysis entrypoint
"""Five-year district cash scenario for sequential agreement and registry decisions."""

import csv
lazy from pathlib import Path

import numpy as np
from scipy.special import ndtr

from src.perspectives_v7 import cost_only_evpi

INFORMATION_TOLERANCE = 1e-7


def joint(root: Path, output: Path) -> None:
    """Integrate the future registry signal before and after contract clarification."""
    with (root / "verification/mixed-policy-fiscal/chhhs-cash.csv").open() as stream:
        cash = list(csv.DictReader(stream))
    with (root / "outputs/v13-refinements/policy_predictive.csv").open() as stream:
        counts = {
            (r["policy"], r["effect_mode"], r["metric"]): float(r["mean"])
            for r in csv.DictReader(stream)
            if r["portfolio"] == "chhhs" and r["activity_id"] == "contacts_1"
        }
    policies = list(dict.fromkeys(r["policy"] for r in cash))
    pilot = policies.index("retain_pilot_only")
    fixed, variable = np.array([
        [[float(r[k]) for r in cash if r["policy"] == p] for p in policies]
        for k in ("fixed_contract_no_care_cash", "variable_retrieval_no_care_cash")
    ])
    # Structural prior: reference retrieval offsets under attenuation, zero under null.
    flows = np.array([
        [fixed + share * response * effect * (variable - fixed) for effect in (1, 0)]
        for share in (0, 0.5, 1)
        for response in (0, 1)
    ])
    vol = counts["retain_pilot_expand_obsbot", "attenuated", "episodes"]
    rates = np.array([
        [
            counts[p, m, "eventual_transfers"] / counts[p, m, "episodes"]
            for p in ("telephone", "retain_pilot_expand_obsbot")
        ]
        for m in ("attenuated", "null")
    ])
    with output.open("w", encoding="utf-8", newline="") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow([
            "years",
            "billing_known",
            "gross_sample_value",
            "cost_of_waiting",
            "break_even_budget",
            "net_value_at_cost_5000",
            "illustrative_itemised_study_cost",
            "net_value_itemised",
            "perspective",
            "horizon_years",
        ])
        for years in (1, 2, 3):
            cost = 1500 + vol * years * 0.8 * (25 + 0.95 * 10)
            w.writerows([
                [*row, cost, row[4] - cost, "chhhs_cash", 5]
                for row in sequential_cash_rows(flows, years, pilot, signal_likelihood(rates, vol, years))
            ])


def signal_likelihood(rates: np.ndarray, volume: float, years: int) -> np.ndarray:
    """Return a normal-contrast likelihood for the retained illustrative two-state example.

    Returns:
        Signal-bin probabilities conditional on each effect state.
    """
    variance = (rates * (1 - rates)).sum(axis=1) / (0.5 * volume * years * 0.8 * 0.95) + 0.02**2
    edges = np.r_[-np.inf, np.linspace(-2, 2, 4001), np.inf]
    return np.diff(ndtr((edges[None, :] - (rates[:, 1] - rates[:, 0])[:, None]) / np.sqrt(variance[:, None])), axis=1)


def sequential_cash_rows(flows: np.ndarray, years: int, pilot: int, probs: np.ndarray) -> list[list[float]]:
    """Value a delayed research decision before and after billing clarification.

    Returns:
        Gross information, delay loss and net budget values on one cash horizon.

    Raises:
        ValueError: If sample information exceeds its matched future bound.
    """
    now = flows[:, :, :, :5].sum(axis=3)
    results = []
    # Continue incumbent pilot through recruitment. Expansion-only cash begins at purchase;
    # retained pilot replacements follow their original calendar. Telephone discontinues pilot.
    future = flows[:, :, :, : 5 - years].sum(axis=3)
    future[:, :, 1:] += (flows[:, :, pilot, years:5].sum(axis=2) - flows[:, :, pilot, : 5 - years].sum(axis=2))[
        :, :, None
    ]
    during = flows[:, :, pilot, :years].sum(axis=2)
    for known in (False, True):
        current = now if known else now.mean(axis=0, keepdims=True)
        payoff = future if known else future.mean(axis=0, keepdims=True)
        adopt = current.mean(axis=1).max(axis=1).mean()
        delayed = payoff.mean(axis=1).max(axis=1).mean() + during.mean()
        informed = np.mean([(probs.T @ state / 2).max(axis=1).sum() for state in payoff]) + during.mean()
        bound = np.mean([cost_only_evpi(state) for state in payoff])
        if not -INFORMATION_TOLERANCE <= informed - delayed <= bound + INFORMATION_TOLERANCE:
            msg = "Sequential registry information exceeds matched future perfect information"
            raise ValueError(msg)
        results.append([
            years,
            known,
            informed - delayed,
            adopt - delayed,
            informed - adopt,
            informed - adopt - 5000,
        ])
    return results
