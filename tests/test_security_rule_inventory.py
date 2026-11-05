"""A scanner cannot silently omit or replace a required rule."""

import hashlib

import pytest

from tools.security.check import verify_rule_inventory


@pytest.mark.parametrize("rules", [["one"], ["one", "one"], ["one", "unexpected"]])
def test_incomplete_native_rule_inventory_is_rejected(rules: list[str]) -> None:
    """Reject missing, duplicate and substituted rules even with no findings."""
    expected = hashlib.sha256(b"one\ntwo").hexdigest()
    with pytest.raises(RuntimeError, match="rule inventory differs"):
        verify_rule_inventory(rules, skipped=False, expected_count=2, expected_digest=expected)


def test_skipped_native_rule_is_rejected() -> None:
    """A reported rule inventory does not excuse a rule skipped by the engine."""
    with pytest.raises(RuntimeError, match="rule inventory differs"):
        verify_rule_inventory(
            ["one"], skipped=True, expected_count=1, expected_digest=hashlib.sha256(b"one").hexdigest()
        )


def test_complete_native_rule_inventory_is_accepted() -> None:
    """Require exact rule identity while allowing engine scheduling order."""
    verify_rule_inventory(
        ["two", "one"], skipped=False, expected_count=2, expected_digest=hashlib.sha256(b"one\ntwo").hexdigest()
    )
