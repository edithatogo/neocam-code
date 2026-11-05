# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Content identity and sealed output validation for the information analysis."""

import hashlib
import json
import platform
from importlib.metadata import version
from typing import cast
lazy from pathlib import Path


def digest(path: Path) -> str:
    """Return the SHA-256 digest of a source or generated artifact."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analysis_provenance(root: Path) -> dict[str, object]:
    """Bind the model, analysis, configuration, retained draws and software.

    Returns:
        Source digests and executed software versions.
    """
    paths = {
        p
        for directory in ("src", "scripts", "config", "data")
        for p in (root / directory).rglob("*")
        if p.is_file() and p.suffix in {".py", ".json", ".csv", ".geojson"}
    }
    for folder in ("v13-primary", "v13-refinements"):
        paths.update(p for p in (root / "outputs" / folder).glob("*") if p.suffix in {".csv", ".npz"})
    if (root / "uv.lock").exists():
        paths.add(root / "uv.lock")
    paths.update((root / "verification/mixed-policy-fiscal").glob("*.csv"))
    paths.update((root / "verification/mode-allocation").glob("*.csv"))
    cash = root / "verification/mixed-policy-fiscal/chhhs-cash.csv"
    if cash.exists():
        paths.add(cash)
    return {
        "versions": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            **{name: version(name) for name in ("voiage", "numpy", "polars", "scipy", "matplotlib")},
        },
        "inputs": {str(p.relative_to(root)): digest(p) for p in sorted(paths)},
    }


def seal_result(output: Path, provenance: dict[str, object]) -> None:
    """Write a manifest only after every artifact has been produced."""
    artifacts = {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
    _ = (output / "manifest.json").write_text(
        json.dumps({"provenance": provenance, "artifacts": artifacts}, sort_keys=True, indent=2) + "\n"
    )


def verify_result(output: Path, expected_provenance: dict[str, object] | None = None) -> None:
    """Reject incomplete, changed, missing or unsafe cached artifacts.

    Raises:
        ValueError: If the sealed artifact inventory does not match the files.
    """
    msg = "Incomplete or changed analysis artifact inventory"
    try:
        manifest = cast("dict[str, object]", json.loads((output / "manifest.json").read_text()))
        artifacts = manifest.get("artifacts")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        raise ValueError(msg) from error
    if expected_provenance is not None and manifest.get("provenance") != expected_provenance:
        msg = "Cached analysis provenance does not match current inputs"
        raise ValueError(msg)
    if not isinstance(artifacts, dict) or not artifacts:
        raise ValueError(msg)
    records = cast("dict[str, str]", artifacts)
    actual = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file() and p.name != "manifest.json"}
    if actual != set(records):
        raise ValueError(msg)
    for name, expected in records.items():
        path = (output / name).resolve()
        if not path.is_relative_to(output.resolve()) or digest(path) != expected:
            raise ValueError(msg)
