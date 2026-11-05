"""A report edit cannot invalidate an unchanged sealed numerical stage."""

lazy from pathlib import Path

lazy import pytest

from scripts import information_cache


def test_stage_reuses_only_unchanged_calculation_inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def calculate(root: Path, target: Path, *, inner_size: int, scenario: tuple[str, str, float]) -> None:
        assert root == tmp_path
        assert inner_size == 64
        assert scenario == ("attenuated", "contacts", 1)
        calls.append(1)
        _ = target.write_text("value\n3\n", encoding="utf-8")

    monkeypatch.setattr(information_cache, "partial", calculate)
    for name in ("scripts/group_information.py", "scripts/registry_joint.py", "src/pathways_v6.py"):
        source = tmp_path / name
        source.parent.mkdir(parents=True, exist_ok=True)
        _ = source.write_text("original")
    target = tmp_path / "result.csv"
    information_cache.cached_partial(tmp_path, target, ("attenuated", "contacts", 1), 64)
    information_cache.cached_partial(tmp_path, target, ("attenuated", "contacts", 1), 64)
    assert len(calls) == 1
    _ = (tmp_path / "scripts/registry_joint.py").write_text("changed report-independent registry")
    information_cache.cached_partial(tmp_path, target, ("attenuated", "contacts", 1), 64)
    assert len(calls) == 1
    _ = (tmp_path / "src/pathways_v6.py").write_text("changed model")
    information_cache.cached_partial(tmp_path, target, ("attenuated", "contacts", 1), 64)
    assert len(calls) == 2
