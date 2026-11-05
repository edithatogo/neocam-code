# ruff: ignore[implicit-namespace-package] -- repository script
"""Reuse sealed joint-registry calculations when their numerical inputs match."""

import csv
import hashlib
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from scripts.information_provenance import analysis_provenance, digest, seal_result, verify_result
from scripts.registry_joint import joint_registry


def numerical_provenance(provenance: dict[str, object]) -> dict[str, object]:
    """Select the complete registry dependency closure from a global manifest.

    Returns:
        Every model/configuration/data/environment input and both script dependencies.
    """
    return {
        "versions": provenance["versions"],
        "inputs": {
            name: value
            for name, value in cast("dict[str, str]", provenance["inputs"]).items()
            if not name.startswith("scripts/")
            or name in {"scripts/registry_joint.py", "scripts/analyse_refinements.py"}
        },
    }


def cached_joint(root: Path, target: Path, *, draws: int = 128, inner_size: int = 64) -> None:
    """Reuse only a sealed unchanged calculation with the exact simulation sizes."""
    expected = numerical_provenance(analysis_provenance(root))
    provenance = {
        **expected,
        "draws": draws,
        "inner_size": inner_size,
        "cache_code": digest(Path(__file__)),
    }
    key = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()[:16]
    base = root / "verification/project-information-registry-cache"
    base.mkdir(parents=True, exist_ok=True)
    cached = base / key
    if cached.exists():
        verify_result(cached, provenance)
        _ = shutil.copyfile(cached / "registry.csv", target)
        return
    reused = False
    for candidate in sorted((root / "verification/project-information").glob("*/manifest.json")):
        if candidate.parent.name.startswith("."):
            continue
        verify_result(candidate.parent)
        manifest = cast("dict[str, object]", json.loads(candidate.read_text()))
        source = candidate.parent / target.name
        if numerical_provenance(cast("dict[str, object]", manifest["provenance"])) != expected or not source.exists():
            continue
        with source.open() as stream:
            sizes = {(int(r["joint_states"]), int(r["inner_nuisance_draws"])) for r in csv.DictReader(stream)}
        if sizes != {(2 * draws, inner_size)}:
            continue
        _ = shutil.copyfile(source, target)
        reused = True
        break
    if not reused:
        joint_registry(root, target, draws=draws, inner_size=inner_size)
    with TemporaryDirectory(dir=base, prefix=".building-") as working:
        folder = Path(working)
        _ = shutil.copyfile(target, folder / "registry.csv")
        seal_result(folder, provenance)
        verify_result(folder, provenance)
        _ = folder.rename(cached)
