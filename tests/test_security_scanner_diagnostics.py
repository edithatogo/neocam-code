"""Machine-readable success cannot conceal incomplete native analysis."""

import pytest

from tools.security.check import verify_scanner_diagnostics


@pytest.mark.parametrize(
    "message",
    [
        "[0.2][WARNING]: partial analysis",
        "[ERROR]: failed",
        "Fixpoint timeout",
        "[\x1b[33mWARNING\x1b[0m]: partial analysis",
    ],
)
def test_incomplete_scanner_diagnostics_are_rejected(message: str) -> None:
    """Reject native warnings that are absent from the JSON error inventory."""
    with pytest.raises(RuntimeError, match="incomplete analysis"):
        verify_scanner_diagnostics(message)


def test_clean_scanner_diagnostics_are_accepted() -> None:
    """Retain successful silent execution."""
    verify_scanner_diagnostics("")
