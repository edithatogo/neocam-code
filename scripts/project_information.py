# ruff: ignore[implicit-namespace-package] -- repository scripts are a namespace package
"""Build a content-versioned decision ledger from the retained analyses."""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from scripts.analyse_refinements import load_refinements
from scripts.billing_information import billing_information
from scripts.fiscal_information import fiscal_partial, fiscal_rows
from scripts.information_cache import cached_partial
from scripts.information_figures import figures
from scripts.information_provenance import analysis_provenance, seal_result, verify_result
from scripts.information_summary import registry_summaries
from scripts.registry_billing import joint
from scripts.registry_cache import cached_joint
from scripts.registry_design import registry
from src.perspectives_v7 import cost_only_evpi

ROOT = Path(__file__).resolve().parents[1]


MEAN_TOLERANCE = 1e-8
PARTIAL_INNER_SIZES = (128, 512)


def _mixed_rows(records: list) -> object:
    groups = defaultdict(list)
    for row in records:
        groups[
            tuple(row[k] for k in ("portfolio", "activity_id", "effect_mode", "decision_set", "perspective"))
        ].append(row)
    for (portfolio, activity, effect, available, view), rows in groups.items():
        best = max(float(r["expected_net_value"]) for r in rows)
        for r in rows:
            mean = float(r["expected_net_value"])
            loss = float(r["expected_regret"])
            yield (
                portfolio,
                activity,
                effect,
                available,
                view,
                r["policy"],
                mean,
                r["probability_optimal"],
                loss,
                max(0, loss + mean - best),
                abs(mean - best) < MEAN_TOLERANCE,
            )


def _uniform_rows(records: list, inputs: list) -> list:
    decisions = []
    uniform = defaultdict(list)
    for row in records:
        uniform[row["portfolio"], row["scenario"], row["perspective"]].append(row)
    for (portfolio, scenario, view), rows in uniform.items():
        path = ROOT / f"outputs/v13-primary/{portfolio}_{scenario}_perspectives.npz"
        if not path.exists():
            best = max(float(r["mean"]) for r in rows)
            decisions.extend(
                (
                    portfolio,
                    "uniform",
                    scenario,
                    "five configurations",
                    view,
                    r["strategy"],
                    r["mean"],
                    r["probability_optimal"],
                    "unavailable: paired archive absent",
                    "unavailable: paired archive absent",
                    abs(float(r["mean"]) - best) < MEAN_TOLERANCE,
                )
                for r in rows
            )
            continue
        inputs.append(path)
        with np.load(path) as archive:
            matrix = archive[view]
        means = matrix.mean(axis=0)
        np.testing.assert_allclose(means, [float(r["mean"]) for r in rows], atol=1e-7)
        information = cost_only_evpi(matrix)
        for mean, r in zip(means, rows, strict=True):
            decisions.append((
                portfolio,
                "uniform",
                scenario,
                "five configurations",
                view,
                r["strategy"],
                mean,
                r["probability_optimal"],
                information + max(means) - mean,
                information,
                abs(max(means) - mean) < MEAN_TOLERANCE,
            ))
    return decisions


def _billing_rows(rows: list) -> list:
    policies = list(dict.fromkeys(r["policy"] for r in rows))
    billing = []
    for years in (3, 5):
        fixed, variable = np.array([
            [sum(float(r[k]) for r in rows if r["policy"] == p and int(r["year"]) <= years) for p in policies]
            for k in ("fixed_contract_no_care_cash", "variable_retrieval_no_care_cash")
        ])
        states = np.array([
            fixed + share * responsive * (variable - fixed) for share in (0, 0.5, 1) for responsive in (0, 1)
        ])
        before = policies[states.mean(axis=0).argmax()]
        for i, values in enumerate(states):
            billing.append((
                years,
                (0, 0.5, 1)[i // 2],
                bool(i % 2),
                1 / 6,
                before,
                policies[values.argmax()],
                values.max(),
                cost_only_evpi(states),
            ))
    return billing


def build() -> Path:
    """Return the sealed output directory for this input revision.

    Raises:
        ValueError: If cached artifacts are altered or inputs change during generation.
    """
    inputs = [Path(__file__)]

    def read(path: str) -> list[dict[str, str]]:
        source = ROOT / path
        inputs.append(source)
        with source.open() as stream:
            return list(csv.DictReader(stream))

    decisions = list(_mixed_rows(read("outputs/v13-refinements/policy_rankings.csv")))
    decisions.extend(_uniform_rows(read("outputs/v13-primary/psa_perspectives.csv"), inputs))
    billing = _billing_rows(read("verification/mixed-policy-fiscal/chhhs-cash.csv"))
    provenance = analysis_provenance(ROOT)
    payload = json.dumps(provenance, sort_keys=True, indent=2)
    base = ROOT / "verification/project-information"
    base.mkdir(parents=True, exist_ok=True)
    destination = base / hashlib.sha256(payload.encode()).hexdigest()[:12]
    if destination.exists():
        verify_result(destination, provenance)
        return destination
    with TemporaryDirectory(dir=base, prefix=".building-") as working:
        out = Path(working)
        for name, header, records in [
            (
                "decisions",
                "portfolio,activity,scenario,decision_set,perspective,policy,expected_saving,probability_optimal,expected_loss,evpi,mean_optimal",
                decisions,
            ),
            (
                "billing",
                "years,liability_share,variable_billing,prior,policy_before,policy_after,conditional_cash_saving,agreement_value",
                billing,
            ),
        ]:
            with (out / f"{name}.csv").open("w", newline="") as stream:
                writer = csv.writer(stream, lineterminator="\n")
                writer.writerow(header.split(","))
                writer.writerows(records)
        _partial_grid(out)
        fiscal_decisions = fiscal_rows(ROOT)
        with (out / "decisions-fiscal.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(fiscal_decisions[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(fiscal_decisions)
        fiscal = fiscal_partial(ROOT)
        with (out / "partial-fiscal.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(fiscal[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(fiscal)
        registry(ROOT, out / "registry.csv")
        joint(ROOT, out / "registry-billing.csv")
        billing_information(ROOT, out)
        cached_joint(ROOT, out / "registry-joint.csv")
        cached_joint(ROOT, out / "registry-joint-double.csv", draws=256, inner_size=128)
        registry_summaries(out)
        figures(ROOT, out)
        if analysis_provenance(ROOT) != provenance:
            msg = "Analysis inputs changed during generation"
            raise ValueError(msg)
        seal_result(out, provenance)
        verify_result(out, provenance)
        out.rename(destination)
    return destination


def _partial_grid(out: Path) -> None:
    config = load_refinements(ROOT / "config/refinements.json")
    records = []
    for effect in config["effect_modes"]:
        for activity in config["activity_scenarios"]:
            for size in PARTIAL_INNER_SIZES:
                default = effect == "attenuated" and activity["id"] == "contacts_1"
                name = (
                    ("partial" if size == max(PARTIAL_INNER_SIZES) else "partial-inner128")
                    if default
                    else f"partial-{effect}-{activity['id']}-{size}"
                )
                target = out / (name + ".csv")
                cached_partial(
                    ROOT,
                    target,
                    (effect, activity["activity_basis"], activity["contacts_per_episode"]),
                    size,
                )
                with target.open() as stream:
                    records.extend(
                        {"effect_mode": effect, "activity_id": activity["id"], **row} for row in csv.DictReader(stream)
                    )
    with (out / "partial-all-scenarios.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    build()
