# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Summarise independent registry Monte Carlo blocks with Polars."""

lazy from pathlib import Path

import polars as pl

KEYS = ["cohort", "activity_id", "portfolio", "decision_set", "perspective", "endpoint", "design", "recruitment_years"]
METRICS = [
    "evsi_annual",
    "matched_evpi_annual",
    "gross_remaining_value",
    "delay_cost",
    "break_even_budget",
    "net_value",
    "probability_policy_change",
]


def registry_summaries(output: Path) -> None:
    """Write block means, Monte Carlo standard errors and doubled-draw diagnostics."""
    frames: list[pl.DataFrame] = []
    for filename, label in (("registry-joint.csv", "base"), ("registry-joint-double.csv", "double")):
        data = pl.read_csv(output / filename)
        summary = data.group_by(KEYS, maintain_order=True).agg([
            *[pl.col(name).mean().alias(name) for name in METRICS],
            *[(pl.col(name).std() / pl.len().cast(pl.Float64).sqrt()).alias(name + "_mcse") for name in METRICS],
            pl.col("study_cost").first(),
            pl.col("enrolled").first(),
            pl.col("completed").first(),
            pl.col("joint_states").first(),
            pl.len().alias("blocks"),
        ])
        summary.write_csv(output / ("registry-summary-" + label + ".csv"))
        frames.append(summary)
    comparison = (
        frames[0]
        .join(frames[1], on=KEYS, suffix="_double")
        .with_columns([
            (pl.col("net_value_double") - pl.col("net_value")).alias("net_value_precision_change"),
            (3.182446 * (pl.col("net_value_mcse") + pl.col("net_value_mcse_double"))).alias("conservative_mc_band"),
        ])
        .with_columns([
            (pl.col("net_value_precision_change").abs() <= pl.col("conservative_mc_band")).alias("within_mc_band"),
        ])
    )
    comparison.write_csv(output / "registry-precision.csv")
