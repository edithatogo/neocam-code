# ruff: ignore[implicit-namespace-package] -- repository script executed with python -m
"""Refresh aggregate scenarios through the existing mixed-policy numerical kernel.

Published association uncertainty and transportability assumptions are separate.
Effect scenarios share nuisance draws; outputs are conditional network-year estimates.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import re
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict, cast

import numpy as np

from quality.artifacts import calculation_inputs
from scripts.analyse_refinements import summary, write_csv
from scripts.information_provenance import digest, seal_result
from src.activity import ActivitySpec
from src.audit_v7 import sample_v7
from src.configuration import ResolvedConfiguration, exact_keys, load_configuration, strict_json
from src.deployment import eligibility_catalogue, evaluate_policies, policy_cash_budget, policy_catalogue
from src.perspectives_v7 import cost_only_evpi, optimal_probabilities, policy_regrets
from src.portfolios_v7 import portfolio
from src.statewide import Parameters, Site
lazy from src.pathways_v6 import PathwaySpec

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parents[1]
NORMAL_975 = 1.96
MAX_DRAWS = 1_000_000
MAX_FACILITIES = 1000
MAX_BUDGET_YEARS = 100
TOLERANCE = 1e-7
METRICS = (
    "net_saving",
    "net_with_family_extension",
    "programme_cost",
    "cash_running_cost",
    "incremental_purchase_capital",
    "hub_cash_cost",
    "episodes",
    "contacts",
    "immediate_transfers",
    "delayed_rescues",
    "eventual_transfers",
    "avoided_transfers",
    "final_local",
)
Draws = tuple[dict[str, np.ndarray], dict[str, np.ndarray]]
Arms = dict[str, dict[str, np.ndarray]]
Rows = list[dict[str, object]]
_replace_parameters = cast("Callable[..., Parameters]", replace)
_replace_pathways = cast("Callable[..., PathwaySpec]", replace)


class EffectEvidence(TypedDict):
    """Reported association and its source outcome, before model extrapolation."""

    odds_ratio: float
    lower: float
    upper: float
    source: str
    outcome: str


class EffectScenario(TypedDict):
    """Multiplier of reported log effect plus separately declared uncertainty."""

    id: str
    log_effect_fraction: float
    transport_sd: float


class Setting(TypedDict):
    """A named network or an explicitly illustrative aggregate network."""

    id: str
    level: str
    portfolio: str | None
    facility_count: int
    geography: str
    annual_contacts_per_facility: float | None
    contacts_by_site: dict[str, float]
    contacts_per_episode: float
    parameters: dict[str, object]
    pathways: dict[str, object]
    interpretation: str


class Sensitivity(TypedDict):
    """A declared one-way or joint scenario; no hidden Cartesian expansion."""

    id: str
    parameters: dict[str, object]
    parameter_factors: dict[str, float]
    pathways: dict[str, object]
    demand_multiplier: float
    contacts_per_episode: float | None
    probabilistic: bool


class AnalysisConfiguration(TypedDict):
    """Small JSON contract for rapid aggregate model refreshes."""

    schema_version: int
    reference_config: str
    source_ledger: str
    draws: int
    seed: int
    budget_years: int
    transport_cash_capture_fractions: list[float]
    effect: EffectEvidence
    effect_scenarios: list[EffectScenario]
    settings: list[Setting]
    sensitivity: list[Sensitivity]
    interpretation: str


def _number(value: object, label: str, lower: float = 0, upper: float = math.inf) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        msg = f"{label} must be finite numeric"
        raise ValueError(msg)
    if not lower <= value <= upper:
        msg = f"{label} outside allowed bounds"
        raise ValueError(msg)
    return float(value)


def _source(root: Path, value: object) -> Path:
    if not isinstance(value, str) or Path(value).is_absolute():
        msg = "Source must be a repository-relative path"
        raise ValueError(msg)
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        msg = "Source must be an existing repository file"
        raise ValueError(msg)
    return path


def _scale_parameters(p: Parameters, factors: dict[str, float]) -> Parameters:
    changes: dict[str, float] = {}
    for name, factor in factors.items():
        value = cast("object", getattr(p, name, None))
        changes[name] = _number(value, name, -math.inf) * _number(factor, name + " factor")
    return _replace_parameters(p, **changes)


def _records(value: object, keys: set[str], label: str) -> list[dict[str, object]]:
    if not isinstance(value, list) or not value:
        msg = f"Nonempty {label} list required"
        raise ValueError(msg)
    rows = cast("list[dict[str, object]]", value)
    seen: set[str] = set()
    for row in rows:
        exact_keys(row, keys, label)
        identity = row["id"]
        if not isinstance(identity, str) or not re.fullmatch(r"[a-z0-9_]+", identity) or identity in seen:
            msg = f"Unique safe identifiers required for {label}"
            raise ValueError(msg)
        seen.add(identity)
    return rows


def setting_sites(setting: Setting) -> list[Site]:
    """Resolve individual facilities so fixed costs respect the declared count.

    Returns:
        Existing facilities or a labelled hypothetical network.

    Raises:
        ValueError: If the named portfolio and facility count disagree.
    """
    sites = (
        portfolio(setting["portfolio"])
        if setting["portfolio"] is not None
        else [
            Site(f"{setting['id']}_{i + 1}", 0, 2026, "rural_proxy", setting["geography"])
            for i in range(setting["facility_count"])
        ]
    )
    if len(sites) != setting["facility_count"]:
        msg = "Declared facility count differs from portfolio"
        raise ValueError(msg)
    return sites


def load_analysis(path: Path, root: Path = ROOT) -> AnalysisConfiguration:  # ruff: ignore[too-many-statements, too-many-branches, too-many-locals, complex-structure] -- single strict input-contract pass
    """Validate all settings before creating any analysis artifacts.

    Returns:
        The validated aggregate analysis configuration.

    Raises:
        ValueError: If any scope, probability, override or path is invalid.
        TypeError: If an input collection has the wrong type.
    """
    if not path.resolve().is_relative_to(root.resolve()):
        msg = "Analysis configuration must remain inside repository"
        raise ValueError(msg)
    data = strict_json(path)
    exact_keys(data, set(AnalysisConfiguration.__annotations__), "Aggregate analysis")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        msg = "Unsupported aggregate schema"
        raise ValueError(msg)
    cfg = load_configuration(root, _source(root, data["reference_config"]))
    _ = _source(root, data["source_ledger"])
    for key, low, high in (("draws", 2, MAX_DRAWS), ("seed", 0, MAX_DRAWS), ("budget_years", 1, MAX_BUDGET_YEARS)):
        if type(data[key]) is not int or not low <= cast("int", data[key]) <= high:
            msg = f"Invalid {key}"
            raise ValueError(msg)
    capture = data["transport_cash_capture_fractions"]
    if not isinstance(capture, list) or not capture:
        msg = "Nonempty transport cash capture scenarios required"
        raise ValueError(msg)
    fractions = [_number(value, "transport cash capture fraction", 0, 1) for value in cast("list[object]", capture)]
    if len(fractions) != len(set(fractions)):
        msg = "Duplicate transport cash capture fractions"
        raise ValueError(msg)
    exact_keys(data["effect"], set(EffectEvidence.__annotations__), "Effect evidence")
    evidence = cast("EffectEvidence", data["effect"])
    lower = _number(evidence["lower"], "lower")
    point = _number(evidence["odds_ratio"], "odds_ratio")
    upper = _number(evidence["upper"], "upper")
    if not 0 < lower < point < upper or not evidence["source"] or not evidence["outcome"]:
        msg = "Positive ordered effect estimate, interval and source required"
        raise ValueError(msg)
    effects = _records(data["effect_scenarios"], set(EffectScenario.__annotations__), "effects")
    for effect in effects:
        _ = _number(effect["log_effect_fraction"], "log effect fraction", 0, 1)
        _ = _number(effect["transport_sd"], "transportability SD")
    if effects[0] != {"id": "reported", "log_effect_fraction": 1, "transport_sd": 0}:
        msg = "Primary effect must use the reported estimate without added transportability SD"
        raise ValueError(msg)
    settings = _records(data["settings"], set(Setting.__annotations__), "settings")
    for record in settings:
        setting = cast("Setting", cast("object", record))
        count = setting["facility_count"]
        if type(count) is not int or not 1 <= count <= MAX_FACILITIES:
            msg = "Invalid facility count"
            raise ValueError(msg)
        if setting["portfolio"] not in {None, "pilot", "chhhs", "chhhs_tchhs", "spokes"}:
            msg = "Unknown portfolio"
            raise ValueError(msg)
        if setting["level"] not in {"district", "regional", "state", "national", "international"}:
            msg = "Unknown decision level"
            raise ValueError(msg)
        sites = setting_sites(setting)
        if not isinstance(record["contacts_by_site"], dict):
            msg = "Site contacts must be a mapping"
            raise TypeError(msg)
        if set(setting["contacts_by_site"]) - {s.name for s in sites}:
            msg = "Unknown site in aggregate contact override"
            raise ValueError(msg)
        for value in setting["contacts_by_site"].values():
            _ = _number(value, "annual site contacts")
        contacts = setting["annual_contacts_per_facility"]
        if contacts is not None:
            _ = _number(contacts, "annual contacts per facility")
        if setting["portfolio"] is None and contacts is None:
            msg = "Illustrative networks require explicit annual activity per facility"
            raise ValueError(msg)
        if not setting["interpretation"]:
            msg = "Setting interpretation required"
            raise ValueError(msg)
        _ = ActivitySpec("contacts", setting["contacts_per_episode"])
        if "odds_ratio" in setting["parameters"]:
            msg = "Set the reported odds ratio in effect evidence, not setting overrides"
            raise ValueError(msg)
        _ = _replace_parameters(cfg.parameters, **setting["parameters"])
        _ = _replace_pathways(cfg.pathways, **setting["pathways"])
    scenarios = _records(data["sensitivity"], set(Sensitivity.__annotations__), "sensitivity")
    for scenario in scenarios:
        if scenario["id"] == "base" or type(scenario["probabilistic"]) is not bool:
            msg = "Sensitivity identifier/PSA flag invalid"
            raise ValueError(msg)
        _ = _number(scenario["demand_multiplier"], "demand multiplier")
        if scenario["contacts_per_episode"] is not None:
            _ = ActivitySpec("contacts", cast("float", scenario["contacts_per_episode"]))
        _ = _replace_parameters(cfg.parameters, **cast("dict[str, object]", scenario["parameters"]))
        _ = _scale_parameters(cfg.parameters, cast("dict[str, float]", scenario["parameter_factors"]))
        _ = _replace_pathways(cfg.pathways, **cast("dict[str, object]", scenario["pathways"]))
        if scenario["probabilistic"] and "odds_ratio" in (
            set(cast("dict[str, object]", scenario["parameters"]))
            | set(cast("dict[str, float]", scenario["parameter_factors"]))
        ):
            msg = "OR overrides are deterministic; use effect scenarios for probabilistic changes"
            raise ValueError(msg)
    return cast("AnalysisConfiguration", cast("object", data))


def effect_draws(evidence: EffectEvidence, scenario: EffectScenario, z: np.ndarray) -> np.ndarray:
    """Reconstruct a log-normal association from its rounded reported interval.

    Returns:
        Paired OR draws; null is exactly one, without clipping possible harm.
    """
    fraction = scenario["log_effect_fraction"]
    se = (math.log(evidence["upper"]) - math.log(evidence["lower"])) / (2 * NORMAL_975)
    return np.exp(fraction * math.log(evidence["odds_ratio"]) + math.hypot(fraction * se, scenario["transport_sd"]) * z)


def paired_effects(p: Parameters, s: PathwaySpec, config: AnalysisConfiguration) -> dict[str, Draws]:
    """Sample nuisance arrays once and replace only the shared effect draw vector.

    Returns:
        Effect scenarios with identical nuisance arrays and structural draws.
    """
    x, e = sample_v7(p, s, n=config["draws"], seed=config["seed"], effect_mode="published")
    z = np.random.default_rng(config["seed"] + 81000).standard_normal(config["draws"])
    return {
        row["id"]: ({**x, "odds_ratio": effect_draws(config["effect"], row, z)}, e)
        for row in config["effect_scenarios"]
    }


def _inputs(
    setting: Setting, cfg: ResolvedConfiguration, config: AnalysisConfiguration, scenario: Sensitivity
) -> tuple[Parameters, PathwaySpec, ActivitySpec]:
    p = _replace_parameters(cfg.parameters, **setting["parameters"])
    p = _replace_parameters(p, odds_ratio=config["effect"]["odds_ratio"])
    p = _replace_parameters(p, **scenario["parameters"])
    p = _scale_parameters(p, scenario["parameter_factors"])
    # This rate already scales pilot activity and the non-pilot birth-exposure formula.
    p = replace(p, calls_per_pilot_site=p.calls_per_pilot_site * scenario["demand_multiplier"])
    s = _replace_pathways(cfg.pathways, **setting["pathways"])
    s = _replace_pathways(s, **scenario["pathways"])
    contacts = scenario["contacts_per_episode"]
    return p, s, ActivitySpec("contacts", setting["contacts_per_episode"] if contacts is None else contacts)


def _calls(setting: Setting, sites: list[Site], n: int, multiplier: float) -> dict[str, np.ndarray]:
    per_facility = setting["annual_contacts_per_facility"]
    values = {} if per_facility is None else {site.name: per_facility for site in sites}
    values.update(setting["contacts_by_site"])
    return {name: np.full(n, value * multiplier) for name, value in values.items()}


def evaluate_setting(
    setting: Setting,
    cfg: ResolvedConfiguration,
    config: AnalysisConfiguration,
    scenario: Sensitivity,
    draws: Draws | None = None,
) -> Arms:
    """Evaluate declared aggregate inputs with current policy and pathway accounting.

    Returns:
        Unmodified current-kernel policy arrays, checked for cohort conservation.

    Raises:
        ValueError: If any result is nonfinite or the episode partition fails.
    """
    sites = setting_sites(setting)
    p, s, activity = _inputs(setting, cfg, config, scenario)
    n = 1 if draws is None else len(draws[0]["odds_ratio"])
    arms = evaluate_policies(
        sites,
        policy_catalogue(sites),
        eligibility_catalogue(sites, allow_hypothetical=True),
        p,
        s,
        cfg.owned_assets if setting["portfolio"] is not None else (),
        inputs=None if draws is None else draws[0],
        structural_draws=None if draws is None else draws[1],
        activity=activity,
        site_calls=_calls(setting, sites, n, scenario["demand_multiplier"]),
    )
    for arm in arms.values():
        residual = arm["eventual_transfers"] + arm["final_local"] - arm["episodes"]
        if not all(np.isfinite(values).all() for values in arm.values()) or np.max(np.abs(residual)) > TOLERANCE:
            msg = "Nonfinite result or failed cohort conservation"
            raise ValueError(msg)
    return arms


def _decisions(arms: Arms, setting: Setting, context: dict[str, object]) -> Rows:
    rows: Rows = []
    policies = policy_catalogue(setting_sites(setting))
    for decision_set in ("reported_operation", "conditional_expansion"):
        names = [p.name for p in policies if not p.conditional or decision_set == "conditional_expansion"]
        for metric, perspective in (("net_saving", "health_system"), ("net_with_family_extension", "societal_bounded")):
            matrix = np.column_stack([arms[name][metric] for name in names])
            means = matrix.mean(axis=0)
            evpi = cost_only_evpi(matrix)
            probabilities, losses = optimal_probabilities(matrix), policy_regrets(matrix, evpi)
            best = float(cast("float", means.max()))
            for i, name in enumerate(names):
                rows.append({
                    **context,
                    "decision_set": decision_set,
                    "perspective": perspective,
                    "policy": name,
                    "expected_net_saving": float(cast("float", means[i])),
                    "mean_optimal": abs(float(cast("float", means[i])) - best) < TOLERANCE,
                    "probability_optimal": float(cast("float", probabilities[i])),
                    "expected_loss": float(cast("float", losses[i])),
                    "annual_cost_only_evpi": evpi,
                })
    return rows


def _context(
    setting: Setting, scenario: Sensitivity, effect: str, s: PathwaySpec, activity: ActivitySpec
) -> dict[str, object]:
    return {
        "setting": setting["id"],
        "level": setting["level"],
        "facility_count": setting["facility_count"],
        "scope": "illustrative_transferability" if setting["portfolio"] is None else "existing_portfolio",
        "scenario": scenario["id"],
        "effect": effect,
        "endpoint": s.endpoint,
        "contacts_per_episode": activity.contacts_per_episode,
        "currency": "reference_AUD",
        "interpretation": setting["interpretation"],
    }


def _cash_rows(
    budget: list[dict[str, float]],
    transport_saving: float,
    config: AnalysisConfiguration,
    context: dict[str, object],
) -> Rows:
    return [
        {
            **context,
            **row,
            "cash_perspective": "CHHHS scenario"
            if context["setting"] == "chhhs"
            else "illustrative network cash scenario",
            "transport_resource_saving": transport_saving,
            "transport_cash_capture_fraction": fraction,
            "transport_cash_offset": fraction * transport_saving,
            "net_cash_expenditure": row["cash_expenditure"] - fraction * transport_saving,
            "break_even_capture_fraction": row["cash_expenditure"] / transport_saving if transport_saving > 0 else None,
            "capture_basis": "Assumed all-mode resource-offset capture; not invoice or settlement evidence",
        }
        for row in budget
        for fraction in config["transport_cash_capture_fractions"]
    ]


def run(config_path: Path, output: Path, root: Path = ROOT) -> dict[str, object]:  # ruff: ignore[too-many-locals, complex-structure] -- one linear analysis/output pass
    """Write a new, source-bound aggregate analysis without replacing retained runs.

    Returns:
        Resolved input and output metadata, with no release or validation claim.

    Raises:
        ValueError: If the output exists or is outside repository outputs.
    """
    root, output = root.resolve(), output.resolve()
    if not output.is_relative_to(root / "outputs") or output == root / "outputs" or output.exists():
        msg = "Use a new output directory below repository outputs"
        raise ValueError(msg)
    config = load_analysis(config_path, root)
    cfg = load_configuration(root, _source(root, config["reference_config"]))
    base: Sensitivity = {
        "id": "base",
        "parameters": {},
        "parameter_factors": {},
        "pathways": {},
        "demand_multiplier": 1,
        "contacts_per_episode": None,
        "probabilistic": True,
    }
    tables: dict[str, Rows] = {
        name: [] for name in ("deterministic", "scenarios", "decisions", "sensitivity", "budgets")
    }
    for setting in config["settings"]:
        sites = setting_sites(setting)
        for scenario in [base, *config["sensitivity"]]:
            p, s, activity = _inputs(setting, cfg, config, scenario)
            context = _context(setting, scenario, "reported", s, activity)
            arms = evaluate_setting(setting, cfg, config, scenario)
            target = "deterministic" if scenario["id"] == "base" else "sensitivity"
            for policy, arm in arms.items():
                tables[target].append({
                    **context,
                    "policy": policy,
                    **{key: float(cast("float", arm[key][0])) for key in METRICS},
                    "first_year_cash": float(
                        cast("float", arm["incremental_purchase_capital"][0] + arm["cash_running_cost"][0])
                    ),
                })
            tables["decisions"].extend(_decisions(arms, setting, {**context, "analysis": "deterministic"}))
            if scenario["id"] == "base":
                for policy in policy_catalogue(sites):
                    budget = policy_cash_budget(
                        sites,
                        policy,
                        eligibility_catalogue(sites, allow_hypothetical=True),
                        p,
                        s,
                        cfg.owned_assets if setting["portfolio"] is not None else (),
                        activity=activity,
                        years=config["budget_years"],
                        site_calls=_calls(setting, sites, 1, scenario["demand_multiplier"]),
                    )
                    transport_saving = float(
                        cast(
                            "float",
                            arms["telephone"]["transport_resource_cost"][0]
                            - arms[policy.name]["transport_resource_cost"][0],
                        )
                    )
                    tables["budgets"].extend(
                        _cash_rows(budget, transport_saving, config, {**context, "policy": policy.name})
                    )
            if not scenario["probabilistic"]:
                continue
            paired = paired_effects(p, s, config)
            for effect, draws in paired.items():
                if scenario["id"] != "base" and effect != "reported":
                    continue
                # An explicit OR sensitivity is deterministic; PSA always uses the declared evidence distribution.
                context = _context(setting, scenario, effect, s, activity)
                sampled = evaluate_setting(setting, cfg, config, scenario, draws)
                tables["decisions"].extend(_decisions(sampled, setting, {**context, "analysis": "probabilistic"}))
                for policy, arm in sampled.items():
                    for metric in METRICS:
                        values = arm[metric]
                        probability = float(np.mean(values > 0)) if metric.startswith("net_") else None
                        tables["scenarios"].append({
                            **context,
                            "policy": policy,
                            "metric": metric,
                            **summary(values),
                            "mcse_mean": float(values.std(ddof=1) / math.sqrt(len(values))),
                            "probability_resource_saving": probability,
                            "mcse_probability": None
                            if probability is None
                            else math.sqrt(probability * (1 - probability) / len(values)),
                        })
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in tables.items():
        write_csv(output, name + ".csv", rows)
    resolved: dict[str, object] = {
        "analysis": config,
        "reference": cfg.snapshot(),
        "primary_effect": "reported",
        "reported_log_or_se": (math.log(config["effect"]["upper"]) - math.log(config["effect"]["lower"]))
        / (2 * NORMAL_975),
        "units": "annual network; money in reference AUD; overlapping networks are not additive",
        "uncertainty": "Reported association CI plus labelled researcher priors; not a fitted local posterior",
        "endpoint": (
            "Published transfer within 24 hours; eventual mapping is extrapolation; initial is a structural scenario"
        ),
        "clinical_validation": False,
        "row_counts": {name: len(rows) for name, rows in tables.items()},
    }
    _ = (output / "resolved_inputs.json").write_text(
        json.dumps(resolved, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    provenance: dict[str, object] = {
        "inputs": {
            **calculation_inputs(root),
            **cfg.source_hashes,
            **{
                name: digest(root / name)
                for name in (
                    "scripts/analyse_aggregate.py",
                    "scripts/analyse_refinements.py",
                    "scripts/information_provenance.py",
                    "quality/artifacts.py",
                    "uv.lock",
                )
            },
            config_path.resolve().relative_to(root).as_posix(): digest(config_path),
            config["source_ledger"]: digest(_source(root, config["source_ledger"])),
        },
        "versions": {"python": platform.python_version(), **{name: version(name) for name in ("numpy", "voiage")}},
        "interpretation": "Current source bytes; no Git ancestry, release acceptance or clinical validation claimed",
    }
    seal_result(output, provenance)
    return resolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("--config", type=Path, default=ROOT / "config/aggregate-analysis.json")
    _ = parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _ = run(cast("Path", args.config), cast("Path", args.output))
