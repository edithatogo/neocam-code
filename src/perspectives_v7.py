"""Small perspective ledger and Value-of-Perspective adapter.

Voiage provides the decision calculations. Neocam reports network-year units and tie bounds.
All costs supplied to the ledger are SIGNED incremental network-year amounts.
"""

from __future__ import annotations

from typing import cast

import numpy as np
lazy from voiage.methods.basic import evpi  # pyright: ignore[reportMissingTypeStubs] -- typed 3.1.0 wheel omits py.typed
lazy from voiage.methods.perspective_tensor import NetBenefitTensor  # pyright: ignore[reportMissingTypeStubs] -- typed 3.1.0 wheel omits py.typed

# The perspective ledger and Value-of-Perspective matrices are draw-by-strategy.
_MATRIX_NDIM = 2


def _matrix(value: np.ndarray) -> np.ndarray:
    a = np.asarray(value, dtype=float)
    if a.ndim != _MATRIX_NDIM or min(a.shape) == 0 or not np.isfinite(a).all():
        msg = "Require finite draw by strategy matrix"
        raise ValueError(msg)
    return a


def _labels(matrix: np.ndarray) -> tuple[str, ...]:
    return tuple(map(str, range(cast("int", matrix.shape[1]))))


def cost_only_evpi(matrix: np.ndarray) -> float:
    """Value perfect information for one network-year of paired net savings.

    Returns:
        Nonnegative expected value in AUD per network-year.
    """
    return max(0.0, evpi(matrix))


def policy_regrets(matrix: np.ndarray, information: float) -> np.ndarray:
    """Add each policy's expected shortfall to the value of perfect information.

    Returns:
        Expected opportunity loss in input strategy order.
    """
    means = matrix.mean(axis=0)
    return information + (means.max() - means)


def optimal_probabilities(values: np.ndarray, atol: float = 1e-9) -> np.ndarray:
    """Return each strategy's equal-lottery optimal-selection probability."""
    a = _matrix(values)
    tensor = NetBenefitTensor(a[:, :, None], _labels(a), ("net",))
    rows = tensor.perspective_acceptability_frontier(atol=atol)
    return np.array([row.probability_optimal for row in rows])


def perspective_regret(choose: np.ndarray, evaluate: np.ndarray, atol: float = 1e-9) -> dict[str, object]:
    """Fixed current-information choice, with an explicit equal-lottery tie policy.

    Per-draw loss may be negative. Only the EXPECTATION is a regret. This is
    not perfect information and the network-year value is not population-scaled.
    Tie bounds disclose the range among equally optimal source decisions.

    Returns:
        The expected regret, tie bounds and selection indices.

    Raises:
        ValueError: If the paired matrices are finite but not equally shaped.
    """
    a, b = _matrix(choose), _matrix(evaluate)
    if a.shape != b.shape:
        msg = "Paired perspectives must have equal shapes"
        raise ValueError(msg)
    tensor = NetBenefitTensor(np.stack((a, b), axis=2), _labels(a), ("choose", "evaluate"))
    regret = tensor.evop(choose_under="choose", evaluate_under="evaluate", selection_tie_policy="split", atol=atol)
    selected = [int(label) for label in regret.chosen_strategy.split("|")]
    target = [int(label) for label in regret.target_strategy.split("|")]
    mb = tensor.expected_net_benefit("evaluate")
    return {
        "value": regret.per_person,
        "choose_indices": selected,
        "target_indices": target,
        "source_tied": len(selected) > 1,
        "target_tied": len(target) > 1,
        "tie_policy": "equal lottery over expected-value optima",
        "minimum_tie_regret": max(0.0, float(mb.max() - mb[selected].max())),
        "maximum_tie_regret": max(0.0, float(mb.max() - mb[selected].min())),
        "unit": "AUD per network-year; no population rescaling",
    }


def reconcile_ledger(
    *,
    health_cost: np.ndarray,
    family_gross: np.ndarray,
    family_subsidy: np.ndarray,
    commonwealth: np.ndarray,
    provider_cost: np.ndarray,
) -> dict[str, np.ndarray]:
    """Reconcile fiscal allocations without counting internal transfers as resources.

    State includes the family subsidy; patient/family is net of it. Provider
    CHHHS is an attribution within the health system, not an additive perspective.
    The fiscal split is a scenario, not a statutory price/payment prediction.

    Returns:
        The reconciled perspective numeric arrays keyed by ledger name.

    Raises:
        ValueError: If the inputs are not paired finite arrays of equal shape.
    """
    arrays = [
        np.asarray(x, dtype=float) for x in (health_cost, family_gross, family_subsidy, commonwealth, provider_cost)
    ]
    if any(x.shape != arrays[0].shape or not np.isfinite(x).all() for x in arrays):
        msg = "Ledger inputs must be paired finite arrays of equal shape"
        raise ValueError(msg)
    h, f, s, c, p = arrays
    return {
        "health_system": h,
        "societal_bounded": h + f,
        "societal": h + f,
        "patient_family": f - s,
        "commonwealth": c,
        "state": h - c + s,
        "provider_chhhs": p,
        "family_gross": f,
        "family_subsidy": s,
    }
