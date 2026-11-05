"""A caller cannot substitute an empty or modified security-rule bundle."""

import hashlib
lazy from pathlib import Path

import pytest

from tools.security.check import verify_rule_bytes


@pytest.mark.parametrize("content", [b"", b"rules: []", b"changed"])
def test_substituted_security_rules_are_rejected(tmp_path: Path, content: bytes) -> None:
    """Fail before executing scanners with a substituted rule set."""
    rules = tmp_path / "rules.yaml"
    _ = rules.write_bytes(content)
    expected = hashlib.sha256(b"qualified").hexdigest()
    with pytest.raises(RuntimeError, match="Security rules differ"):
        verify_rule_bytes(rules, expected)


def test_exact_qualified_rules_are_accepted(tmp_path: Path) -> None:
    """Preserve successful verification of the qualified bytes."""
    rules = tmp_path / "rules.yaml"
    _ = rules.write_bytes(b"qualified")
    verify_rule_bytes(rules, hashlib.sha256(b"qualified").hexdigest())
