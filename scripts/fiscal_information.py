# ruff: ignore[implicit-namespace-package] -- repository script
"""Paired information values for the existing assumed CHHHS fiscal ledger.

These annual resource/fiscal allocations reproduce chhhs-reproduction.md. They are
not cash settlement predictions. Financing shares are scenarios, not evidence.
"""

from typing import TypedDict, cast
lazy from collections.abc import Callable
lazy from pathlib import Path

import numpy as np

from scripts import group_information
from scripts.analyse_refinements import load_refinements, sample_v7
from scripts.group_information import GROUPS
from src.activity import ActivitySpec
from src.configuration import load_configuration
from src.deployment import eligibility_catalogue, evaluate_policies, policy_catalogue
from src.perspectives_v7 import cost_only_evpi, optimal_probabilities
from src.portfolios_v7 import portfolio
lazy from src.deployment import DeploymentPolicy


class FiscalRow(TypedDict):
    """One paired annual perspective decision result."""

    portfolio: str
    activity: str
    scenario: str
    decision_set: str
    perspective: str
    policy: str
    expected_saving: float
    probability_optimal: float
    expected_loss: float
    evpi: float
    mean_optimal: bool


conditional_inputs = cast(
    "Callable[..., tuple[dict[str, np.ndarray], dict[str, np.ndarray]]]", group_information.conditional_inputs
)

TOLERANCE = 1e-7


def fiscal_values(
    arms: dict[str, dict[str, np.ndarray]], names: list[str], hospital_fraction: np.ndarray
) -> dict[str, np.ndarray]:
    """Apply the retained reference financing shares to paired annual components.

    Returns:
        Seven paired policy payoff matrices under the stated financing shares.
    """
    by_policy: list[dict[str, np.ndarray]] = []
    phone = arms["telephone"]
    for name in names:
        delta = {key: phone[key] - value for key, value in arms[name].items()}
        origin = hospital_fraction * sum(
            delta[key] for key in ("origin_benchmark_cost", "local_benchmark_cost", "pre_rescue_benchmark_cost")
        )
        receiver = hospital_fraction * delta["receiving_benchmark_cost"] + delta["rescue_extra_resource_cost"]
        site = origin + delta["capital_annualised"] + delta["local_ready_cost"] + delta["local_workflow_cost"]
        district = site + delta["transport_resource_cost"] + 0.5 * receiver
        health = site + receiver + delta["transport_resource_cost"] + delta["hub_resource_cost"]
        family = -delta["family_cost_extension"]
        by_policy.append({
            "origin_sites": site,
            "district": district,
            "state": health + 0.2 * family,
            "health_system": health,
            "societal": health + family,
            "consumer": 0.8 * family,
            "commonwealth": np.zeros_like(health),
        })
    return {view: np.column_stack([values[view] for values in by_policy]) for view in by_policy[0]}


def _values(
    root: Path,
    effect: str,
    *,
    keys: str | None = None,
    inner_size: int = 128,
    block: int = 0,
) -> tuple[tuple[DeploymentPolicy, ...], dict[str, np.ndarray]]:
    cfg = load_configuration(root)
    sites = portfolio("chhhs")
    policies = policy_catalogue(sites)
    inputs, structural = (
        sample_v7(cfg.parameters, cfg.pathways, n=cfg.draws, seed=cfg.seed, effect_mode=effect)
        if keys is None
        else conditional_inputs(root, keys, inner_size, block, effect)
    )
    arms = evaluate_policies(
        sites,
        policies,
        eligibility_catalogue(sites, allow_hypothetical=True),
        cfg.parameters,
        cfg.pathways,
        cfg.owned_assets,
        inputs=inputs,
        structural_draws=structural,
        activity=ActivitySpec("contacts", 1),
    )
    return policies, fiscal_values(arms, [p.name for p in policies], structural["hospital_fraction"])


def fiscal_rows(root: Path) -> list[FiscalRow]:
    """Reproduce seven reference ledgers under each retained effect scenario.

    Returns:
        Paired decisions, expected loss and perfect-information values.
    """
    rows: list[FiscalRow] = []
    for effect in load_refinements(root / "config/refinements.json")["effect_modes"]:
        policies, values = _values(root, effect)
        for conditional in (False, True):
            indexes = [i for i, p in enumerate(policies) if conditional or not p.conditional]
            for view, full in values.items():
                matrix = full[:, indexes]
                means = matrix.mean(axis=0)
                best = float(cast("float", means.max()))
                probabilities = optimal_probabilities(matrix)
                evpi = cost_only_evpi(matrix)
                for index, mean, probability in zip(
                    indexes,
                    cast("list[float]", means.tolist()),
                    cast("list[float]", probabilities.tolist()),
                    strict=True,
                ):
                    rows.append({
                        "portfolio": "chhhs",
                        "activity": "contacts_1",
                        "scenario": effect,
                        "decision_set": "conditional_expansion" if conditional else "reported_operation",
                        "perspective": view,
                        "policy": policies[index].name,
                        "expected_saving": mean,
                        "probability_optimal": probability,
                        "expected_loss": evpi + best - mean,
                        "evpi": evpi,
                        "mean_optimal": abs(mean - best) < TOLERANCE,
                    })
    return rows


def fiscal_partial(root: Path) -> list[dict[str, object]]:
    """Report grouped values for the five additional reference fiscal views.

    Returns:
        Nested conditional values and independent-block Monte Carlo standard errors.

    """
    rows: list[dict[str, object]] = []
    for effect in load_refinements(root / "config/refinements.json")["effect_modes"]:
        for group, keys in GROUPS.items():
            for size in (128, 512):
                estimates = _partial_blocks(root, effect, keys, size)
                for (conditional, view), scores in estimates.items():
                    rows.append({
                        "portfolio": "chhhs",
                        "activity_id": "contacts_1",
                        "effect_mode": effect,
                        "financing": "reference_assumed",
                        "perspective": view,
                        "group": group,
                        "decision_set": "conditional" if conditional else "reported",
                        "conditional_evppi": np.mean(scores),
                        "block_mcse": np.std(scores, ddof=1) / 2,
                        "outer_per_block": 64,
                        "inner": size,
                        "blocks": 4,
                    })
    return rows


def _partial_blocks(root: Path, effect: str, keys: str, size: int) -> dict[tuple[bool, str], list[float]]:
    estimates: dict[tuple[bool, str], list[float]] = {}
    for block in range(4):
        policies, values = _values(root, effect, keys=keys, inner_size=size, block=block)
        for conditional in (False, True):
            indexes = [i for i, p in enumerate(policies) if conditional or not p.conditional]
            for view, full in values.items():
                if view in {"health_system", "societal"}:
                    continue
                matrix = full[:, indexes]
                score = cost_only_evpi(matrix.reshape(64, size, -1).mean(axis=1))
                if score > cost_only_evpi(matrix) + TOLERANCE:
                    msg = "Fiscal group value exceeds matched perfect-information bound"
                    raise ValueError(msg)
                estimates.setdefault((conditional, view), []).append(score)
    return estimates
