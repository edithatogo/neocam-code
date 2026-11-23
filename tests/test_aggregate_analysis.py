"""Evidence distributions, current-kernel sensitivity and aggregate accounting."""

import csv
import json
import math
import shutil
from copy import deepcopy
from pathlib import Path
from typing import cast

import numpy as np
import pytest

from scripts import analyse_aggregate as aggregate
from scripts.information_provenance import verify_result
from src.configuration import load_configuration, strict_json

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def config() -> aggregate.AnalysisConfiguration:
    value = aggregate.load_analysis(ROOT / "config/aggregate-analysis.json")
    value["draws"] = 256
    return value


def base() -> aggregate.Sensitivity:
    return {
        "id": "base",
        "parameters": {},
        "parameter_factors": {},
        "pathways": {},
        "demand_multiplier": 1,
        "contacts_per_episode": None,
        "probabilistic": True,
    }


def test_reported_interval_and_shared_effect_latent_vector(config: aggregate.AnalysisConfiguration) -> None:
    evidence = config["effect"]
    z = np.array([-1.96, 0.0, 1.96])
    effects = {row["id"]: aggregate.effect_draws(evidence, row, z) for row in config["effect_scenarios"]}
    se = (math.log(0.9) - math.log(0.26)) / 3.92
    np.testing.assert_allclose(effects["reported"], np.exp(math.log(0.48) + se * z))
    assert effects["reported"][0] == pytest.approx(0.26, abs=0.01)
    assert effects["reported"][-1] == pytest.approx(0.90, abs=0.01)
    np.testing.assert_allclose(np.log(effects["transportability"] / 0.48) / math.hypot(se, 0.35), z)
    np.testing.assert_array_equal(effects["null"], np.ones(3))
    assert effects["skeptical"][-1] > 1  # Possible harm is retained, not truncated.


def test_all_effect_modes_reuse_identical_nuisance_draws(config: aggregate.AnalysisConfiguration) -> None:
    cfg = load_configuration(ROOT)
    draws = aggregate.paired_effects(cfg.parameters, cfg.pathways, config)
    reference, structural = draws["reported"]
    for effect, (x, e) in draws.items():
        for name in set(x) - {"odds_ratio"}:
            np.testing.assert_array_equal(x[name], reference[name], err_msg=f"{effect}/{name}")
        for name in e:
            np.testing.assert_array_equal(e[name], structural[name])
    first = draws["reported"][0]["odds_ratio"].copy()
    _ = aggregate.evaluate_setting(config["settings"][0], cfg, config, base(), draws["reported"])
    np.testing.assert_array_equal(draws["reported"][0]["odds_ratio"], first)


def test_effect_null_and_monotonic_transfer_direction(config: aggregate.AnalysisConfiguration) -> None:
    cfg = load_configuration(ROOT)
    setting = config["settings"][0]
    outputs: list[float] = []
    for odds_ratio in (0.26, 0.48, 1.0):
        scenario: aggregate.Sensitivity = {**base(), "parameters": {"odds_ratio": odds_ratio}}
        arms = aggregate.evaluate_setting(setting, cfg, config, scenario)
        video, phone = arms["retain_pilot_only"], arms["telephone"]
        outputs.append(float(cast("float", video["eventual_transfers"][0])))
        np.testing.assert_allclose(video["eventual_transfers"] + video["final_local"], video["episodes"])
        if odds_ratio == 1:
            np.testing.assert_allclose(video["eventual_transfers"], phone["eventual_transfers"])
            np.testing.assert_allclose(video["avoided_transfers"], 0, atol=1e-10)
            assert video["net_saving"][0] < 0  # Video programme costs persist without a transfer effect.
    assert outputs[0] < outputs[1] < outputs[2]


def test_demand_scales_once_and_contacts_are_not_episodes(config: aggregate.AnalysisConfiguration) -> None:
    cfg = load_configuration(ROOT)
    setting = config["settings"][1]  # Includes both pilot-rate and birth-exposure sites.
    reference = aggregate.evaluate_setting(setting, cfg, config, base())["telephone"]
    double = aggregate.evaluate_setting(setting, cfg, config, {**base(), "demand_multiplier": 2})["telephone"]
    repeated = aggregate.evaluate_setting(setting, cfg, config, {**base(), "contacts_per_episode": 2})["telephone"]
    np.testing.assert_allclose(double["contacts"], 2 * reference["contacts"])
    np.testing.assert_allclose(repeated["contacts"], reference["contacts"])
    np.testing.assert_allclose(repeated["episodes"], reference["episodes"] / 2)


def test_explicit_facility_count_prices_each_installation(config: aggregate.AnalysisConfiguration) -> None:
    cfg = load_configuration(ROOT)
    setting = deepcopy(config["settings"][-2])
    setting["annual_contacts_per_facility"] = 0
    setting["facility_count"] = 1
    one = aggregate.evaluate_setting(setting, cfg, config, base())["retain_pilot_expand_obsbot"]
    setting["facility_count"] = 2
    two = aggregate.evaluate_setting(setting, cfg, config, base())["retain_pilot_expand_obsbot"]
    np.testing.assert_allclose(two["incremental_purchase_capital"], 2 * one["incremental_purchase_capital"])
    assert two["incremental_purchase_capital"][0] == 9000
    np.testing.assert_array_equal(two["contacts"], [0])


def test_relative_capital_scenario_scales_each_setting(config: aggregate.AnalysisConfiguration) -> None:
    cfg = load_configuration(ROOT)
    scenario = next(row for row in config["sensitivity"] if row["id"] == "capital_double")
    for setting in config["settings"][-2:]:
        reference = aggregate.evaluate_setting(setting, cfg, config, base())
        changed = aggregate.evaluate_setting(setting, cfg, config, scenario)
        for policy in changed:
            np.testing.assert_allclose(
                changed[policy]["incremental_purchase_capital"], 2 * reference[policy]["incremental_purchase_capital"]
            )


@pytest.fixture
def small_repository(tmp_path: Path, config: aggregate.AnalysisConfiguration) -> Path:
    for name in (
        "config/reference.json",
        "config/pathways.json",
        "config/equipment_estate.json",
        "data/parameters.json",
        "data/births_queensland_2022.csv",
        "data/aggregate/public-inputs.json",
        "scripts/analyse_aggregate.py",
        "scripts/analyse_refinements.py",
        "scripts/information_provenance.py",
        "quality/artifacts.py",
        "uv.lock",
    ):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        _ = shutil.copyfile(ROOT / name, target)
    config["settings"] = [config["settings"][0], config["settings"][-2]]
    config["sensitivity"] = [row for row in config["sensitivity"] if row["id"] in {"repeat_2", "initial_endpoint"}]
    _ = (tmp_path / "config/aggregate-analysis.json").write_text(json.dumps(config), encoding="utf-8")
    return tmp_path


def test_complete_refresh_normalisation_manifest_and_no_overwrite(small_repository: Path) -> None:
    path = small_repository / "config/aggregate-analysis.json"
    output = small_repository / "outputs/new"
    result = aggregate.run(path, output, small_repository)
    assert result["primary_effect"] == "reported"
    verify_result(output)
    manifest = strict_json(output / "manifest.json")
    provenance = cast("dict[str, object]", manifest["provenance"])
    inputs = cast("dict[str, str]", provenance["inputs"])
    assert "scripts/analyse_aggregate.py" in inputs
    assert "uv.lock" in inputs
    with (output / "budgets.csv").open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            cash, saving = float(row["cash_expenditure"]), float(row["transport_resource_saving"])
            capture = float(row["transport_cash_capture_fraction"])
            assert float(row["net_cash_expenditure"]) == pytest.approx(cash - capture * saving)
            if saving > 0:
                assert float(row["break_even_capture_fraction"]) == pytest.approx(cash / saving)
    with (output / "decisions.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    groups: dict[tuple[str, ...], list[dict[str, str]]] = {}
    for row in rows:
        key = tuple(row[name] for name in ("setting", "scenario", "effect", "analysis", "decision_set", "perspective"))
        groups.setdefault(key, []).append(row)
    for group in groups.values():
        assert sum(float(row["probability_optimal"]) for row in group) == pytest.approx(1)
        assert any(row["mean_optimal"] == "True" for row in group)
        evpi = float(group[0]["annual_cost_only_evpi"])
        assert evpi >= 0
        best = max(float(row["expected_net_saving"]) for row in group)
        for row in group:
            assert float(row["expected_loss"]) == pytest.approx(evpi + best - float(row["expected_net_saving"]))
    with pytest.raises(ValueError, match="new output"):
        _ = aggregate.run(path, output, small_repository)
    with pytest.raises(ValueError, match="new output"):
        _ = aggregate.run(path, small_repository.parent / "outside", small_repository)


@pytest.mark.parametrize("error", ["effect", "portfolio", "unknown_contact", "boolean", "primary", "path"])
def test_reject_invalid_scope_and_distributions(small_repository: Path, error: str) -> None:
    path = small_repository / "config/aggregate-analysis.json"
    config = aggregate.load_analysis(path, small_repository)
    if error == "effect":
        config["effect"]["lower"] = 0.7
    elif error == "portfolio":
        config["settings"][0]["facility_count"] = 99
    elif error == "unknown_contact":
        config["settings"][0]["contacts_by_site"] = {"unknown": 20}
    elif error == "boolean":
        config["settings"][0]["contacts_by_site"] = {"Atherton": True}
    elif error == "primary":
        config["effect_scenarios"][0]["transport_sd"] = 0.35
    else:
        config["source_ledger"] = "../outside.json"
    _ = path.write_text(json.dumps(config), encoding="utf-8")
    with pytest.raises(ValueError, match=r"effect|count|site|numeric|Primary|Source"):
        _ = aggregate.load_analysis(path, small_repository)
