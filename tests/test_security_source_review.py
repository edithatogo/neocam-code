"""A scanner result cannot silently accept new or changed source code."""

import pytest

from tools.security.check import verify_source_review


@pytest.mark.parametrize("observed", [{"new.py": "new"}, {"one.py": "changed"}, {}])
def test_source_review_rejects_a_different_snapshot(observed: dict[str, str]) -> None:
    """Require renewed review after addition, modification or deletion."""
    with pytest.raises(RuntimeError, match="Source differs"):
        verify_source_review({"one.py": "reviewed"}, observed)


def test_source_review_accepts_exact_reviewed_bytes() -> None:
    """Preserve the successful case for the exact reviewed source set."""
    verify_source_review({"one.py": "reviewed"}, {"one.py": "reviewed"})
