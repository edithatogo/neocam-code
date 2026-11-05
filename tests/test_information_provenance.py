"""Reproducibility boundaries of the information-analysis command."""

import hashlib
import json
lazy from pathlib import Path

import pytest

from scripts.information_provenance import analysis_provenance, verify_result


def test_version_changes_with_model_and_billing_source(tmp_path: Path) -> None:
    for name in ("src/pathways_v6.py", "scripts/registry_billing.py", "data/parameters.json"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text("original")
    original = analysis_provenance(tmp_path)
    _ = (tmp_path / "src/pathways_v6.py").write_text("changed")
    changed = analysis_provenance(tmp_path)
    assert original != changed
    _ = (tmp_path / "scripts/registry_billing.py").write_text("changed")
    assert changed != analysis_provenance(tmp_path)
    versions = original["versions"]
    assert isinstance(versions, dict)
    assert {"python", "voiage", "numpy", "polars", "scipy", "matplotlib"} <= versions.keys()


def test_incomplete_result_is_not_a_cached_success(tmp_path: Path) -> None:
    _ = (tmp_path / "manifest.json").write_text(json.dumps({"inputs": {}}))
    with pytest.raises(ValueError, match="artifact"):
        verify_result(tmp_path)


def test_modified_result_is_rejected(tmp_path: Path) -> None:
    _ = (tmp_path / "result.csv").write_text("changed")
    _ = (tmp_path / "manifest.json").write_text(json.dumps({"artifacts": {"result.csv": "0" * 64}}))
    with pytest.raises(ValueError, match="artifact"):
        verify_result(tmp_path)


def test_valid_artifacts_cannot_hide_wrong_input_provenance(tmp_path: Path) -> None:
    _ = (tmp_path / "result.csv").write_text("result")
    _ = (tmp_path / "manifest.json").write_text(
        json.dumps({
            "provenance": {"model": "wrong"},
            "artifacts": {"result.csv": hashlib.sha256(b"result").hexdigest()},
        })
    )
    with pytest.raises(ValueError, match="provenance"):
        verify_result(tmp_path, {"model": "current"})
