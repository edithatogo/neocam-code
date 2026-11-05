# Copyright (c) 2026 Panda Vision contributors
"""Convert uv's universal CycloneDX export to a GitHub dependency snapshot."""

from __future__ import annotations

import argparse
import json
import os
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- read the exact committed lock using a fixed Git command
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol, cast

type Json = bool | int | float | str | list[Json] | dict[str, Json] | None


class _Args(Protocol):
    """Typed command-line paths."""

    export: Path
    output: Path


def _object(value: Json) -> dict[str, Json]:
    if not isinstance(value, dict):
        msg = "Expected a dependency object"
        raise TypeError(msg)
    return value


def _array(value: Json) -> list[Json]:
    if not isinstance(value, list):
        msg = "Expected a dependency list"
        raise TypeError(msg)
    return value


def _text(value: Json) -> str:
    if not isinstance(value, str):
        msg = "Expected a dependency identifier"
        raise TypeError(msg)
    return value


def build_snapshot(lock: bytes, export: bytes, *, sha: str, ref: str, job: str) -> dict[str, Json]:
    """Include every locked package, rejecting partial or inconsistent exports.

    Returns:
        A commit-bound GitHub dependency snapshot.

    Raises:
        ValueError: The export omits a locked package or references missing dependencies.
    """
    document = _object(cast("Json", json.loads(export)))
    packages = [_object(item) for item in _array(_object(cast("Json", tomllib.loads(lock.decode())))["package"])]
    project = next(item for item in packages if "virtual" in _object(item["source"]))
    expected = {
        (_text(item["name"]), _text(item["version"])) for item in packages if "virtual" not in _object(item["source"])
    }
    components = {_text(item["bom-ref"]): item for item in map(_object, _array(document["components"]))}
    actual = {(_text(item["name"]), _text(item["version"])) for item in components.values()}
    if actual != expected or len(components) != len(expected):
        msg = "CycloneDX export does not cover the complete lock"
        raise ValueError(msg)
    edges = {
        _text(item["ref"]): [_text(child) for child in _array(item.get("dependsOn", []))]
        for item in map(_object, _array(document["dependencies"]))
    }
    project_id = _text(_object(_object(document["metadata"])["component"])["bom-ref"])
    direct = set(edges[project_id])
    all_children = {child for children in edges.values() for child in children}
    if not all_children <= components.keys():
        msg = "CycloneDX export contains unresolved dependency edges"
        raise ValueError(msg)
    runtime_names = {_text(_object(item)["name"]) for item in _array(project.get("dependencies", []))}
    for group in _object(project.get("optional-dependencies", {})).values():
        runtime_names.update(_text(_object(item)["name"]) for item in _array(group))
    runtime = {key for key, item in components.items() if item["name"] in runtime_names}
    pending = list(runtime)
    while pending:
        for child in edges.get(pending.pop(), []):
            if child not in runtime:
                runtime.add(child)
                pending.append(child)
    resolved: dict[str, Json] = {
        key: {
            "package_url": item["purl"],
            "relationship": "direct" if key in direct else "indirect",
            "scope": "runtime" if key in runtime else "development",
            "dependencies": [components[child]["purl"] for child in edges.get(key, [])],
        }
        for key, item in components.items()
    }
    return {
        "version": 0,
        "sha": sha,
        "ref": ref,
        # Reuse the initial local submission identity so new snapshots replace it.
        "job": {"id": job, "correlator": "neocam-local-uv-lock-all-groups-extras"},
        "detector": {
            "name": "uv-lock-local",
            "version": "0.13.6",
            "url": "https://github.com/astral-sh/uv",
        },
        "scanned": datetime.now(UTC).isoformat(),
        "metadata": {"selection": "universal lock, all groups and extras", "python": "3.15"},
        "manifests": {
            "uv.lock": {"name": "uv.lock", "file": {"source_location": "uv.lock"}, "resolved": resolved},
        },
    }


def main() -> None:
    """Write a temporary snapshot bound to the checked-out commit and lock.

    Raises:
        RuntimeError: The interpreter is not Python 3.15.
        ValueError: The working lock differs from the submitted commit.
    """
    if sys.version_info[:2] != (3, 15):
        msg = "Dependency snapshots require Python 3.15"
        raise RuntimeError(msg)
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("export", type=Path)
    _ = parser.add_argument("output", type=Path)
    args = cast("_Args", cast("object", parser.parse_args()))
    sha = os.environ["GITHUB_SHA"]
    lock = Path("uv.lock").read_bytes()
    committed = subprocess.check_output(["git", "show", f"{sha}:uv.lock"])  # ruff: ignore[subprocess-without-shell-equals-true, start-process-with-partial-path] -- fixed read-only Git command; SHA comes from trusted Actions metadata
    if lock != committed:
        msg = "Working lock does not match the submitted commit"
        raise ValueError(msg)
    snapshot = build_snapshot(
        lock,
        args.export.read_bytes(),
        sha=sha,
        ref=os.environ["GITHUB_REF"],
        job=f"{os.environ['GITHUB_RUN_ID']}:{os.environ['GITHUB_RUN_ATTEMPT']}",
    )
    _ = args.output.write_text(json.dumps(snapshot) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
