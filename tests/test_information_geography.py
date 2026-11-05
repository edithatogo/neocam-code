"""Assignment and eligibility reconciliation for all geographical policies."""

import csv
from pathlib import Path

from scripts.information_geography import map_records

ROOT = Path(__file__).resolve().parents[1]


def test_every_policy_site_has_a_point_or_explicit_locality() -> None:
    records = map_records(ROOT)
    with (ROOT / "outputs/v13-refinements/policy_assignments.csv").open() as stream:
        expected = list(csv.DictReader(stream))
    assert len(records) == len(expected)
    assert {(r["portfolio"], r["policy"], r["site"], r["strategy"]) for r in records} == {
        (r["portfolio"], r["policy"], r["site"], r["strategy"]) for r in expected
    }
    assert {r["site"] for r in records if r["coordinate_status"] == "unresolved_locality"} == {
        "Yarrabah Emergency Service"
    }
    assert {r["strategy"] for r in records} == {"telephone", "panda", "obsbot", "mobile", "fixed"}
    assert all(r["eligibility"] in {"reported_operation", "hypothetical"} for r in records)
