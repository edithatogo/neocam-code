# ruff: ignore[implicit-namespace-package] -- repository script
"""Independent blocks of nested conditional simulation for mixed policies."""

import csv
lazy from pathlib import Path

import numpy as np

from scripts.analyse_refinements import (
    ActivitySpec,
    eligibility_catalogue,
    evaluate_policies,
    load_configuration,
    policy_catalogue,
    portfolio,
    sample_v7,
)
from src.perspectives_v7 import cost_only_evpi

GROUPS = {
    "effect": "odds_ratio baseline_transfer case_mix reliability rescue_rate delay_share",
    "demand": "calls_per_pilot_site birth_growth state_uptake",
    "retrieval_hospital": (
        "air_anchor road_cost mode_air_shift marginal_fraction downstream_delta rescue_premium "
        "hospital_fraction hospital_multiplier local_multiplier pre_rescue"
    ),
    "programme": (
        "equipment_cost life_years check_minutes support training workflow_per_call loaded_hour "
        "hub_annual_cost capacity_threshold capacity_step_cost"
    ),
}


INFORMATION_TOLERANCE = 1e-7


def conditional_inputs(root: Path, keys: str, size: int, block: int, effect: str) -> tuple[dict, dict]:
    """Repeat joint learned inputs while resampling independent nuisance blocks.

    Returns:
        Population and structural input dictionaries with paired outer rows.
    """
    cfg = load_configuration(root)
    seed = cfg.seed + 100000 * (block + 1)
    outer = sample_v7(cfg.parameters, cfg.pathways, n=64, seed=seed, effect_mode=effect)
    inner = sample_v7(cfg.parameters, cfg.pathways, n=64 * size, seed=seed + 1, effect_mode=effect)
    for larger, smaller in zip(inner, outer, strict=True):
        for key in set(keys.split()) & smaller.keys():
            larger[key] = np.repeat(smaller[key], size, axis=0)
    return inner


def _conditional_block(root: Path, network: str, keys: str, options: tuple) -> dict:
    size, block, scenario = options
    cfg = load_configuration(root)
    sites = portfolio(network)
    policies = policy_catalogue(sites)
    inner = conditional_inputs(root, keys, size, block, scenario[0])
    arms = evaluate_policies(
        sites,
        policies,
        eligibility_catalogue(sites, allow_hypothetical=True),
        cfg.parameters,
        cfg.pathways,
        cfg.owned_assets,
        inputs=inner[0],
        structural_draws=inner[1],
        activity=ActivitySpec(scenario[1], scenario[2]),
    )
    values = {}
    for metric in ("net_saving", "net_with_family_extension"):
        for conditional in (False, True):
            matrix = np.column_stack([arms[p.name][metric] for p in policies if conditional or not p.conditional])
            estimate = cost_only_evpi(matrix.reshape(64, size, -1).mean(axis=1))
            bound = cost_only_evpi(matrix)
            if estimate > bound + INFORMATION_TOLERANCE:
                msg = "Conditional group information exceeds its matched full-information bound"
                raise ValueError(msg)
            values[metric, conditional] = estimate
    return values


def partial(
    root: Path,
    output: Path,
    inner_size: int = 64,
    networks: tuple[str, ...] = ("pilot", "chhhs", "chhhs_tchhs", "spokes"),
    *,
    scenario: tuple[str, str, float] = ("attenuated", "contacts", 1),
) -> None:
    """Hold a joint outer draw fixed and resample remaining independent input blocks."""
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow([
            "portfolio",
            "group",
            "perspective",
            "decision_set",
            "conditional_evppi",
            "block_mcse",
            "outer_per_block",
            "inner",
            "blocks",
        ])
        for network in networks:
            for group, keys in GROUPS.items():
                blocks = [_conditional_block(root, network, keys, (inner_size, block, scenario)) for block in range(4)]
                for metric, conditional in blocks[0]:
                    scores = [b[metric, conditional] for b in blocks]
                    writer.writerow([
                        network,
                        group,
                        metric,
                        "conditional" if conditional else "reported",
                        np.mean(scores),
                        np.std(scores, ddof=1) / 2,
                        64,
                        inner_size,
                        4,
                    ])
