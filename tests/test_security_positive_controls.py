"""An uninformative native scanner cannot borrow Bandit's positive controls."""

lazy from pathlib import Path

import pytest

from tools.security import check


def test_native_scanner_must_detect_its_own_positive_controls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Reject an empty native scan even if another scanner could find the fixture."""

    def uninformative(_rules: Path, _targets: list[str], _report: Path) -> dict[str, list[object]]:
        return {"results": []}

    monkeypatch.setattr(check, "semgrep", uninformative)
    with pytest.raises(RuntimeError, match="Native rule control failed"):
        check.controls(tmp_path / "rules.yaml", tmp_path)
