# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Reconcile every displayed policy assignment before geographical rendering."""

import csv
lazy from pathlib import Path


def map_records(root: Path) -> list[dict[str, str]]:
    """Attach eligibility and explicit coordinate availability to every assignment.

    Returns:
        A complete policy/site inventory; unresolved locations retain a locality entry.

    Raises:
        ValueError: If a site assignment is duplicated or has no eligibility evidence.
    """

    def read(name: str) -> list[dict[str, str]]:
        with (root / name).open() as stream:
            return list(csv.DictReader(stream))

    points = {r["site"]: r for r in read("config/voi-facilities.csv")}
    eligibility = {
        (r["portfolio"], r["site"], r["strategy"]): r["status"] for r in read("outputs/v13-refinements/eligibility.csv")
    }
    assignments = read("outputs/v13-refinements/policy_assignments.csv")
    ids = {site: str(i + 1) for i, site in enumerate(sorted({r["site"] for r in assignments}))}
    seen: set[tuple[str, str, str]] = set()
    records: list[dict[str, str]] = []
    for row in assignments:
        key = row["portfolio"], row["policy"], row["site"]
        status = eligibility.get((row["portfolio"], row["site"], row["strategy"]))
        if key in seen or status is None:
            msg = "Duplicate assignment or missing eligibility evidence"
            raise ValueError(msg)
        seen.add(key)
        point = points.get(row["site"], {})
        records.append({
            **row,
            "site_id": ids[row["site"]],
            "eligibility": status,
            "longitude": point.get("longitude", ""),
            "latitude": point.get("latitude", ""),
            "coordinate_status": "verified_facility" if point else "unresolved_locality",
        })
    return records
