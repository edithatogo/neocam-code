# ruff: ignore[implicit-namespace-package] -- repository script
"""Illustrative five-year resource decision with a comparative registry."""

import csv
lazy from pathlib import Path

import numpy as np
from scipy.special import ndtr

INFORMATION_TOLERANCE = 1e-7
MODES = ("attenuated", "null")


def _study_values(
    rates: np.ndarray, means: np.ndarray, pilot_index: int, design: tuple, scenario: tuple[int, float]
) -> tuple:
    years, volume = scenario
    _, enrol, follow, video_share, bias = design
    prior = means.mean(axis=0)
    n = volume * years * enrol
    variance = (rates * (1 - rates) / np.array([1 - video_share, video_share])).sum(axis=1) / (n * follow) + bias**2
    cuts = np.r_[-np.inf, np.linspace(-2, 2, 4001), np.inf]
    likelihood = np.diff(
        ndtr((cuts[None, :] - (rates[:, 1] - rates[:, 0])[:, None]) / np.sqrt(variance[:, None])), axis=1
    )
    info = float((likelihood.T @ means / 2).max(axis=1).sum() - prior.max())
    bound = means.max(axis=1).mean() - prior.max()
    if not -INFORMATION_TOLERANCE <= info <= bound + INFORMATION_TOLERANCE:
        msg = "Sample information exceeds the matched perfect-information bound"
        raise ValueError(msg)
    return n, info, max(0, info) * (5 - years), years * (prior.max() - prior[pilot_index])


def registry(root: Path, output: Path) -> None:
    """Integrate a two-state normal likelihood over future observed contrasts."""
    folder = root / "outputs/v13-refinements"
    with (folder / "policy_predictive.csv").open() as stream:
        counts = {
            (r["portfolio"], r["effect_mode"], r["policy"], r["metric"]): float(r["mean"])
            for r in csv.DictReader(stream)
            if r["activity_id"] == "contacts_1"
        }
    with (folder / "policy_rankings.csv").open() as stream:
        rankings = [
            r
            for r in csv.DictReader(stream)
            if r["activity_id"] == "contacts_1" and r["decision_set"] == "conditional_expansion"
        ]
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow([
            "portfolio",
            "perspective",
            "endpoint",
            "design",
            "recruitment_years",
            "enrolled_episodes",
            "per_year_evsi",
            "gross_remaining_value",
            "delay_cost",
            "break_even_budget",
        ])
        for network in sorted({r["portfolio"] for r in rankings}):
            writer.writerows(_network_rows(network, counts, rankings))


def _network_rows(network: str, counts: dict, rankings: list) -> object:
    pilot = "retain_pilot_only"
    video = "retain_pilot_expand_obsbot"
    if (network, "attenuated", video, "episodes") not in counts:
        video = pilot
    volume = counts[network, "attenuated", video, "episodes"]
    for view in ("health_system", "societal_bounded"):
        subset = [r for r in rankings if r["portfolio"] == network and r["perspective"] == view]
        policies = sorted({r["policy"] for r in subset})
        means = np.array([
            [
                next(float(r["expected_net_value"]) for r in subset if r["policy"] == p and r["effect_mode"] == m)
                for p in policies
            ]
            for m in MODES
        ])
        for endpoint in ("immediate_transfers", "delayed_rescues", "eventual_transfers"):
            rates = np.array([
                [counts[network, m, p, endpoint] / counts[network, m, p, "episodes"] for p in ("telephone", video)]
                for m in MODES
            ])
            for design, enrol, follow, video_share, bias in (
                ("balanced", 0.8, 0.95, 0.5, 0.02),
                ("selective", 0.5, 0.75, 0.7, 0.10),
            ):
                for years in (1, 2, 3):
                    n, info, gross, delay = _study_values(
                        rates, means, policies.index(pilot), (design, enrol, follow, video_share, bias), (years, volume)
                    )
                    yield [
                        network,
                        view,
                        endpoint,
                        design,
                        years,
                        n,
                        info,
                        gross,
                        delay,
                        gross - delay,
                    ]
