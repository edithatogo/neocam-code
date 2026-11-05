"""Fiscal evidence boundaries and conservation of retained resource offsets."""

import csv
import json
from math import isclose
from typing import cast

from scripts.analyse_refinements import ROOT, load_refinements
from src.activity import ActivitySpec
from src.configuration import load_configuration
from src.deployment import eligibility_catalogue, evaluate_policies, policy_catalogue
from src.portfolios_v7 import portfolio

FISCAL = ROOT / "verification/mixed-policy-fiscal"


def test_evidence_does_not_turn_asset_liability_into_cash_savings() -> None:
    evidence = cast("dict[str, object]", json.loads((ROOT / "config/fiscal-evidence.json").read_text()))
    rule = cast("dict[str, object]", evidence["fixed_wing_rule"])
    assert rule["payer"] == "referring_hhs"
    assert rule["requires"] == ["referral_accepted", "asset_tasked"]
    assert rule["effective_from"] == "2026-06-19"
    assert rule["marginal_cash_capture"] is None
    assert rule["historical_application_verified"] is False
    assert set(cast("list[str]", rule["excluded_rsq_costs"])) == {"clinical_coordination", "rsq_medical_staff"}
    assert evidence["unconditional_fiscal_reporting"] is False
    assert evidence["external_acceptance"] is False
    assert len(cast("list[str]", evidence["independent_reviews_pending"])) == 4
    assert {r["id"] for r in cast("list[dict[str, str]]", evidence["unresolved"])} == {
        "capital",
        "local_programme",
        "hub",
        "origin_care",
        "receiving_care",
        "road_rotary",
        "cash_capture",
        "family",
        "government",
        "historical_terms",
    }


def test_retained_payer_partitions_reproduce_model_and_leave_system_unchanged() -> None:
    cfg = load_configuration(ROOT)
    activities = load_refinements(ROOT / "config/refinements.json")["activity_scenarios"]
    expected: dict[tuple[str, str, str], float] = {}
    for network in cfg.portfolios:
        sites = portfolio(network)
        for activity in activities:
            arms = evaluate_policies(
                sites,
                policy_catalogue(sites),
                eligibility_catalogue(sites, allow_hypothetical=True),
                cfg.parameters,
                cfg.pathways,
                cfg.owned_assets,
                activity=ActivitySpec(activity["activity_basis"], activity["contacts_per_episode"]),
            )
            for policy, arm in arms.items():
                expected[network, activity["id"], policy] = float(cast("float", arm["transport_resource_benefit"][0]))
    weights = {
        "chhhs_default": (1, 0, 0),
        "retrieval_funder": (0, 1, 0),
        "destination": (0, 0, 1),
        "shared": (0.5, 0.5, 0),
    }
    seen: set[tuple[str, str, str, str]] = set()
    with (FISCAL / "retrieval-payers.csv").open() as stream:
        for row in csv.DictReader(stream):
            key = row["portfolio"], row["activity_id"], row["policy"]
            scenario = row["payer_scenario"]
            assert (*key, scenario) not in seen
            seen.add((*key, scenario))
            offset = expected[key]
            amounts = [float(row[name]) for name in ("chhhs", "retrieval_funder", "destination")]
            assert isclose(float(row["system_retrieval_offset"]), offset, abs_tol=1e-7)
            assert isclose(sum(amounts), offset, abs_tol=1e-7)
            for amount, weight in zip(amounts, weights[scenario], strict=True):
                assert isclose(amount, weight * offset, abs_tol=1e-7)
    assert seen == {(*key, scenario) for key in expected for scenario in weights}


def test_fixed_and_variable_cash_differ_only_by_annual_retrieval_offset() -> None:
    with (FISCAL / "retrieval-payers.csv").open() as stream:
        offsets = {
            row["policy"]: float(row["system_retrieval_offset"])
            for row in csv.DictReader(stream)
            if row["portfolio"] == "chhhs"
            and row["activity_id"] == "contacts_1"
            and row["payer_scenario"] == "chhhs_default"
        }
    seen: set[tuple[str, int]] = set()
    with (FISCAL / "chhhs-cash.csv").open() as stream:
        for row in csv.DictReader(stream):
            key = row["policy"], int(row["year"])
            assert key not in seen
            seen.add(key)
            difference = float(row["variable_retrieval_no_care_cash"]) - float(row["fixed_contract_no_care_cash"])
            assert isclose(difference, offsets[row["policy"]], abs_tol=1e-7)
    assert seen == {(policy, year) for policy in offsets for year in range(1, 8)}
