"""An unchanged sealed registry stage may survive a purely fiscal/reporting edit."""

lazy from pathlib import Path

lazy import pytest

from scripts import registry_cache
from scripts.information_provenance import analysis_provenance, seal_result


def test_registry_reuse_binds_model_source_and_sizes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def source(name: str) -> Path:
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        _ = p.write_text("original")
        return p

    model = source("src/pathways_v6.py")
    report = source("scripts/fiscal_information.py")
    _ = source("scripts/registry_joint.py")
    previous = tmp_path / "verification/project-information/previous"
    previous.mkdir(parents=True)
    _ = (previous / "registry-joint.csv").write_text("joint_states,inner_nuisance_draws\n256,64\n")
    seal_result(previous, analysis_provenance(tmp_path))
    calls: list[tuple[int, int]] = []

    def calculate(root: Path, target: Path, *, draws: int, inner_size: int) -> None:
        assert root == tmp_path
        calls.append((draws, inner_size))
        _ = target.write_text("joint_states,inner_nuisance_draws\n512,128\n", encoding="utf-8")

    monkeypatch.setattr(registry_cache, "joint_registry", calculate)
    target = tmp_path / "registry-joint.csv"
    _ = report.write_text("changed fiscal report")
    registry_cache.cached_joint(tmp_path, target)
    assert calls == []
    registry_cache.cached_joint(tmp_path, target, draws=256, inner_size=128)
    assert calls == [(256, 128)]
    _ = model.write_text("changed model")
    registry_cache.cached_joint(tmp_path, target)
    assert calls == [(256, 128), (128, 64)]
