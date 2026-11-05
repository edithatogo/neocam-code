"""Security policy and tool dependencies must invalidate an assurance receipt."""

lazy from pathlib import Path

import pytest

from quality.assurance import input_fingerprint


@pytest.mark.parametrize(
    "name",
    ["check.py", "uv.lock", "rules-lock.json", "reviewed-findings.json", "install_engine.py", "engine-lock.json"],
)
def test_security_tool_inputs_change_the_assurance_fingerprint(tmp_path: Path, name: str) -> None:
    """Reject reuse when the isolated scanner, lock or adjudication policy changes."""
    folder = tmp_path / "tools/security"
    folder.mkdir(parents=True)
    source = folder / name
    _ = source.write_text("original\n", encoding="utf-8")
    before = input_fingerprint(tmp_path)
    _ = source.write_text("changed\n", encoding="utf-8")
    assert input_fingerprint(tmp_path) != before
