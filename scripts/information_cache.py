# ruff: ignore[implicit-namespace-package] -- repository scripts use a namespace package
"""Reuse sealed conditional-simulation stages after a reporting interruption."""

import hashlib
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from scripts.group_information import partial
from scripts.information_provenance import analysis_provenance, seal_result, verify_result


def cached_partial(root: Path, target: Path, scenario: tuple[str, str, float], inner_size: int) -> None:
    """Execute a conditional calculation or copy its unchanged verified result."""
    provenance = analysis_provenance(root)
    inputs = cast("dict[str, str]", provenance["inputs"])
    provenance["inputs"] = {
        name: digest
        for name, digest in inputs.items()
        if not name.startswith("scripts/")
        or name
        in {
            "scripts/group_information.py",
            "scripts/analyse_refinements.py",
            "scripts/information_cache.py",
        }
    }
    provenance["scenario"] = list(scenario)
    provenance["inner_size"] = inner_size
    key = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()[:16]
    base = root / "verification/project-information-cache"
    base.mkdir(parents=True, exist_ok=True)
    cached = base / key
    if cached.exists():
        verify_result(cached, provenance)
        shutil.copyfile(cached / "partial.csv", target)
        return
    partial(root, target, inner_size=inner_size, scenario=scenario)
    with TemporaryDirectory(dir=base, prefix=".building-") as work:
        folder = Path(work)
        shutil.copyfile(target, folder / "partial.csv")
        seal_result(folder, provenance)
        verify_result(folder, provenance)
        folder.rename(cached)
