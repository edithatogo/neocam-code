# Copyright (c) 2026 Panda Vision contributors
"""Dependency coverage and graph fidelity for trusted lock submissions."""

import json

import pytest

from quality.dependency_snapshot import Json, build_snapshot

LOCK = b"""[[package]]
name = "project"
version = "1"
source = {virtual = "."}
dependencies = [{name = "runtime"}]
[[package]]
name = "runtime"
version = "1"
source = {registry = "https://pypi.org/simple"}
[[package]]
name = "shared"
version = "2"
source = {registry = "https://pypi.org/simple"}
[[package]]
name = "dev"
version = "3"
source = {registry = "https://pypi.org/simple"}
"""


def _export() -> dict[str, Json]:
    return {
        "metadata": {"component": {"bom-ref": "project"}},
        "components": [
            {"bom-ref": name, "name": name, "version": version, "purl": f"pkg:pypi/{name}@{version}"}
            for name, version in (("runtime", "1"), ("shared", "2"), ("dev", "3"))
        ],
        "dependencies": [
            {"ref": "project", "dependsOn": ["runtime", "dev"]},
            {"ref": "runtime", "dependsOn": ["shared"]},
            {"ref": "dev", "dependsOn": ["shared"]},
        ],
    }


def test_preserves_shared_runtime_dependency_and_development_scope() -> None:
    """A package shared with development retains runtime scope and exact edges."""
    snapshot = build_snapshot(LOCK, json.dumps(_export()).encode(), sha="abc", ref="refs/heads/main", job="1")
    # Preserve the bootstrap submission identity: another detector may shadow it.
    assert snapshot["job"] == {"id": "1", "correlator": "neocam-local-uv-lock-all-groups-extras"}
    assert snapshot["detector"] == {
        "name": "uv-lock-local",
        "version": "0.13.6",
        "url": "https://github.com/astral-sh/uv",
    }
    assert snapshot["manifests"] == {
        "uv.lock": {
            "name": "uv.lock",
            "file": {"source_location": "uv.lock"},
            "resolved": {
                "runtime": {
                    "package_url": "pkg:pypi/runtime@1",
                    "relationship": "direct",
                    "scope": "runtime",
                    "dependencies": ["pkg:pypi/shared@2"],
                },
                "shared": {
                    "package_url": "pkg:pypi/shared@2",
                    "relationship": "indirect",
                    "scope": "runtime",
                    "dependencies": [],
                },
                "dev": {
                    "package_url": "pkg:pypi/dev@3",
                    "relationship": "direct",
                    "scope": "development",
                    "dependencies": ["pkg:pypi/shared@2"],
                },
            },
        },
    }


def test_rejects_partial_export() -> None:
    """A plausible but incomplete export cannot hide locked dependencies."""
    export = _export()
    export["components"] = []
    with pytest.raises(ValueError, match="complete lock"):
        _ = build_snapshot(LOCK, json.dumps(export).encode(), sha="abc", ref="refs/heads/main", job="1")


def test_rejects_unresolved_edge() -> None:
    """Unknown edges cannot silently disappear from dependency review."""
    export = _export()
    export["dependencies"] = [{"ref": "project", "dependsOn": ["missing"]}]
    with pytest.raises(ValueError, match="unresolved dependency edges"):
        _ = build_snapshot(LOCK, json.dumps(export).encode(), sha="abc", ref="refs/heads/main", job="1")
