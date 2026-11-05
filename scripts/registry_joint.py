# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Joint model-draw registry scenarios; observable endpoints, not causal identification."""

import csv
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import TypedDict, cast
lazy from pathlib import Path

import numpy as np

from scripts.analyse_refinements import load_refinements, sample_v7
from src.activity import ActivitySpec
from src.configuration import load_configuration
from src.deployment import DeploymentPolicy, eligibility_catalogue, evaluate_policies, policy_catalogue
from src.perspectives_v7 import cost_only_evpi
from src.portfolios_v7 import portfolio
lazy from src.statewide import Site

TOLERANCE = 1e-7
MATRIX_DIMENSIONS = 2
SIGNAL_PROBABILITY_FLOOR = 1e-12


def finite_information(payoffs: np.ndarray, likelihood: np.ndarray) -> float:
    """Integrate the posterior maximum over a matched equally weighted state prior.

    Returns:
        Expected sample value for the same states, decision set and annual ledger.

    Raises:
        ValueError: If the signal is invalid or its value exceeds perfect information.
    """
    if likelihood.ndim != MATRIX_DIMENSIONS or payoffs.ndim != MATRIX_DIMENSIONS or len(likelihood) != len(payoffs):
        msg = "Matched state likelihood and payoff matrices required"
        raise ValueError(msg)
    if np.any(likelihood < 0) or not np.isfinite(likelihood).all() or not np.isfinite(payoffs).all():
        msg = "Finite nonnegative likelihood and finite payoffs required"
        raise ValueError(msg)
    np.testing.assert_allclose(likelihood.sum(axis=1), 1, atol=1e-10)
    value = float((likelihood.T @ payoffs / len(payoffs)).max(axis=1).sum() - payoffs.mean(axis=0).max())
    if not -TOLERANCE <= value <= cost_only_evpi(payoffs) + TOLERANCE:
        msg = "Registry information violates its matched perfect-information bound"
        raise ValueError(msg)
    return max(0.0, value)


def contrast_likelihood(rates: np.ndarray, control_n: int, video_n: int, bias: float) -> np.ndarray:
    """Marginalise a symmetric residual risk shift and observe the count contrast.

    Returns:
        One probability distribution per joint model state. Contrast-only observation
        deliberately discards baseline-count information and does not identify causality.
    """
    rows: list[np.ndarray] = []
    length = control_n + video_n + 1
    fft_size = 1 << (length - 1).bit_length()
    for index in range(len(rates)):
        control = float(cast("float", rates[index, 0]))
        video = float(cast("float", rates[index, 1]))
        a = binomial_mass(control_n, control)
        contrasts = [
            np.fft.irfft(
                np.fft.rfft(binomial_mass(video_n, min(1.0, max(0.0, video + shift))), fft_size)
                * np.fft.rfft(a[::-1], fft_size),
                fft_size,
            )[:length]
            for shift in (-bias, bias)
        ]
        row = np.maximum(np.mean(contrasts, axis=0), 0)
        rows.append(cast("np.ndarray", row / row.sum()))
    return np.array(rows)


@lru_cache(maxsize=128)
def _log_combinations(n: int) -> np.ndarray:
    return np.array([math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) for k in range(n + 1)])


def binomial_mass(n: int, probability: float) -> np.ndarray:
    """Compute a count likelihood in log space including degenerate endpoints.

    Returns:
        The probabilities for counts zero through n inclusive.
    """
    if probability in {0.0, 1.0}:
        mass = np.zeros(n + 1)
        mass[0 if probability == 0 else n] = 1
        return mass
    k = np.arange(n + 1)
    mass = np.exp(_log_combinations(n) + k * math.log(probability) + (n - k) * math.log1p(-probability))
    np.testing.assert_allclose(float(cast("float", mass.sum())), 1, atol=1e-9)
    return cast("np.ndarray", mass / mass.sum())


def _clinical_inputs(
    root: Path, sizes: tuple[int, int], block: int, mode: str
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    cfg = load_configuration(root)
    draws, inner_size = sizes
    seed = cfg.seed + 900000 + block + 1000 * draws
    outer = sample_v7(cfg.parameters, cfg.pathways, n=draws, seed=seed, effect_mode=mode)
    inputs, structural = sample_v7(cfg.parameters, cfg.pathways, n=draws * inner_size, seed=seed + 1, effect_mode=mode)
    for inner, small in zip((inputs, structural), outer, strict=True):
        for key in {
            "odds_ratio",
            "baseline_transfer",
            "case_mix",
            "reliability",
            "rescue_rate",
            "delay_share",
        } & small.keys():
            inner[key] = np.repeat(small[key], inner_size, axis=0)
    return inputs, structural


@dataclass(frozen=True)
class RegistryRun:
    """Finite conditional simulation sizes and the retained activity interpretation."""

    outer_draws: int
    inner_size: int
    activity: ActivitySpec
    activity_id: str


@dataclass(frozen=True)
class RegistryStates:
    """Clinical states with nuisance inputs integrated out conditionally."""

    policies: list[str]
    values: dict[str, np.ndarray]
    risks: dict[tuple[str, str], np.ndarray]
    bounds: dict[str, float]
    inner_size: int


def conditional_states(root: Path, network: str, block: int, run: RegistryRun, *, conditional: bool) -> RegistryStates:
    """Average nuisance uncertainty within each clinical outer state.

    Returns:
        Paired conditional means, endpoint risks and matched full-information bounds.
    """
    cfg = load_configuration(root)
    sites = portfolio(network)
    policies = tuple(p for p in policy_catalogue(sites) if conditional or not p.conditional)
    video = next((p for p in policies if p.name == "retain_pilot_expand_obsbot"), policies[-1])
    payoffs: dict[str, list[np.ndarray]] = {"health_system": [], "societal_bounded": []}
    rates: dict[tuple[str, str], list[np.ndarray]] = {}
    for mode in ("attenuated", "null"):
        inputs, structural = _clinical_inputs(root, (run.outer_draws, run.inner_size), block, mode)
        arms = evaluate_policies(
            sites,
            policies,
            eligibility_catalogue(sites, allow_hypothetical=True),
            cfg.parameters,
            cfg.pathways,
            cfg.owned_assets,
            inputs=inputs,
            structural_draws=structural,
            activity=run.activity,
        )
        for view, metric in (("health_system", "net_saving"), ("societal_bounded", "net_with_family_extension")):
            payoffs[view].append(np.column_stack([arms[p.name][metric] for p in policies]))
        observed = _cohort_rates(root, sites, video, (inputs, structural), run.activity)
        for key, array in observed.items():
            rates.setdefault(key, []).append(array)
    full = {k: np.concatenate(v) for k, v in payoffs.items()}
    return RegistryStates(
        [p.name for p in policies],
        {k: v.reshape(2 * run.outer_draws, run.inner_size, -1).mean(axis=1) for k, v in full.items()},
        {k: np.concatenate(v).reshape(2 * run.outer_draws, run.inner_size, -1).mean(axis=1) for k, v in rates.items()},
        {k: cost_only_evpi(v) for k, v in full.items()},
        run.inner_size,
    )


def _cohort_rates(
    root: Path,
    sites: list[Site],
    video: DeploymentPolicy,
    inputs: tuple[dict[str, np.ndarray], dict[str, np.ndarray]],
    activity: ActivitySpec,
) -> dict[tuple[str, str], np.ndarray]:
    cfg = load_configuration(root)
    equipped = [site for site in sites if dict(video.assignments)[site.name] != "telephone"]
    pilot = [site for site in equipped if site.name in {"Atherton", "Mareeba", "Innisfail"}]
    groups = {"pilot_existing": pilot}
    if len(equipped) > len(pilot):
        groups["network_assumed_access"] = equipped
    result: dict[tuple[str, str], np.ndarray] = {}
    for name, group in groups.items():
        comparison = (
            DeploymentPolicy("telephone", tuple((site.name, "telephone") for site in group)),
            DeploymentPolicy(
                video.name, tuple((site.name, dict(video.assignments)[site.name]) for site in group), video.conditional
            ),
        )
        observed = evaluate_policies(
            group,
            comparison,
            eligibility_catalogue(group, allow_hypothetical=True),
            cfg.parameters,
            cfg.pathways,
            cfg.owned_assets,
            inputs=inputs[0],
            structural_draws=inputs[1],
            activity=activity,
        )
        for metric in ("immediate_transfers", "delayed_rescues", "eventual_transfers"):
            result[name, metric] = np.column_stack([
                observed[p.name][metric] / observed[p.name]["episodes"] for p in comparison
            ])
    return result


@dataclass(frozen=True)
class StudyDesign:
    """Explicit recruitment and residual-confounding scenarios, not observations."""

    name: str
    enrol: float
    follow: float
    video_share: float
    bias: float
    design_effect: float


def research_budget(info: float, means: np.ndarray, pilot: int, years: int, horizon: int) -> tuple[float, float, float]:
    """Value research only after its findings can change a decision.

    Returns:
        Gross future information, incumbent delay loss and break-even study budget.
    """
    gross = max(0, horizon - years) * info
    delay = min(years, horizon) * float(cast("float", means.max() - means[pilot]))
    return gross, delay, gross - delay


class DesignCounts(TypedDict):
    """Recruitment and collection-cost inputs for one explicit study scenario."""

    enrolled: int
    completed: int
    effective_control_n: int
    effective_video_n: int
    design_effect: float
    residual_risk_shift: float
    setup_cost: float
    per_enrolled_cost: float
    per_complete_cost: float
    study_cost: float
    forecast_eligible_episodes_per_year: float


def study_counts(volume: float, years: int, design: StudyDesign) -> DesignCounts:
    """Plan distinct episodes and itemised illustrative collection costs.

    Returns:
        Recruited/completed episodes and arm counts summing to the effective total.
    """
    enrolled = round(volume * years * design.enrol)
    completed = round(enrolled * design.follow)
    return {
        "enrolled": enrolled,
        "completed": completed,
        "effective_control_n": round(completed / design.design_effect)
        - round(completed * design.video_share / design.design_effect),
        "effective_video_n": round(completed * design.video_share / design.design_effect),
        "design_effect": design.design_effect,
        "residual_risk_shift": design.bias,
        "setup_cost": 1500,
        "per_enrolled_cost": 25,
        "per_complete_cost": 10,
        "study_cost": 1500 + 25 * enrolled + 10 * completed,
        "forecast_eligible_episodes_per_year": volume,
    }


def _information_row(
    payoffs: np.ndarray, signal: np.ndarray, policies: list[str], years: int, cost: float
) -> dict[str, str | int | float]:
    means = cast("np.ndarray", payoffs.mean(axis=0))
    info = finite_information(payoffs, signal)
    gross, delay, budget = research_budget(info, means, policies.index("retain_pilot_only"), years, 5)
    posterior = signal.T @ payoffs
    actions = posterior.argmax(axis=1)
    probability = signal.mean(axis=0)
    active_indices = cast("list[int]", np.unique(actions[probability > SIGNAL_PROBABILITY_FLOOR]).tolist())
    return {
        "possible_policy_after_signal": "|".join(policies[i] for i in active_indices),
        "probability_policy_change": float(cast("float", probability[actions != means.argmax()].sum())),
        "preferred_action": "collect_evidence"
        if budget > cost
        else "retain_pilot"
        if policies[int(means.argmax())] == "retain_pilot_only"
        else "adopt_now",
        "joint_states": len(payoffs),
        "attenuated_prior": 0.5,
        "null_prior": 0.5,
        "policy_before": policies[int(means.argmax())],
        "evsi_annual": info,
        "matched_evpi_annual": cost_only_evpi(payoffs),
        "gross_remaining_value": gross,
        "delay_cost": delay,
        "break_even_budget": budget,
        "net_value": budget - cost,
    }


def _block_rows(state: RegistryStates, volumes: tuple[float, float], block: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for design in (
        StudyDesign("balanced", 0.8, 0.95, 0.5, 0.02, 1),
        StudyDesign("selective_clustered", 0.5, 0.75, 0.7, 0.10, 2),
    ):
        for years in (1, 2, 3):
            for (cohort, endpoint), rates in state.risks.items():
                counts = study_counts(volumes[1] if cohort == "pilot_existing" else volumes[0], years, design)
                signal = contrast_likelihood(
                    rates, counts["effective_control_n"], counts["effective_video_n"], design.bias
                )
                for view, payoffs in state.values.items():
                    information = _information_row(payoffs, signal, state.policies, years, counts["study_cost"])
                    rows.append({
                        "cohort": cohort,
                        "study_access": "existing pilot equipment"
                        if cohort == "pilot_existing"
                        else "additional access/devices assumed; enabling cost unpriced",
                        "perspective": view,
                        "endpoint": endpoint,
                        "design": design.name,
                        "recruitment_years": years,
                        "horizon_years": 5,
                        "block": block,
                        **counts,
                        **information,
                        "matched_evpi_annual": state.bounds[view],
                        "clinical_group_bound_annual": cost_only_evpi(payoffs),
                        "inner_nuisance_draws": state.inner_size,
                        "remaining_budget_for_unpriced_enabling": (
                            "not applicable" if cohort == "pilot_existing" else information["net_value"]
                        ),
                        "causal_identification": "unavailable; conditional observable-endpoint learning",
                    })
    return rows


def joint_registry(root: Path, output: Path, draws: int = 128, inner_size: int = 64) -> None:
    """Evaluate finite joint-PSA projections in four independent Monte Carlo blocks."""
    with (root / "outputs/v13-refinements/policy_predictive.csv").open(encoding="utf-8") as stream:
        volumes = {
            (r["portfolio"], r["activity_id"]): float(r["mean"])
            for r in csv.DictReader(stream)
            if r["effect_mode"] == "attenuated" and r["policy"] == "retain_pilot_only" and r["metric"] == "episodes"
        }
    rows: list[dict[str, object]] = []
    activities = load_refinements(root / "config/refinements.json")["activity_scenarios"]
    for (network, activity_id), forecast in volumes.items():
        activity = next(a for a in activities if a["id"] == activity_id)
        run = RegistryRun(
            draws, inner_size, ActivitySpec(activity["activity_basis"], activity["contacts_per_episode"]), activity_id
        )
        rows.extend(_network_registry_rows(root, network, forecast, volumes["pilot", activity_id], run))
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _network_registry_rows(
    root: Path, network: str, forecast: float, pilot_volume: float, run: RegistryRun
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for conditional in (False, True):
        volume = forecast if conditional else pilot_volume
        for block in range(4):
            state = conditional_states(root, network, block, run, conditional=conditional)
            rows.extend(
                {
                    "portfolio": network,
                    "activity_id": run.activity_id,
                    "decision_set": "conditional_expansion" if conditional else "reported_operation",
                    **row,
                }
                for row in _block_rows(state, (volume, pilot_volume), block)
            )
    return rows
