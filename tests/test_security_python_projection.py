"""Compatibility projection preserves security expressions in Python 3.15."""

import ast
lazy from pathlib import Path

import pytest

from tools.security.check import project_source


@pytest.mark.parametrize(
    "source",
    [
        "lazy import json\njson.loads(input())\n",
        "def f[T](value: T):\n return eval(value)\n",
        "type Alias = eval(input())\n",
        "try:\n pass\nexcept ValueError, TypeError:\n eval(input())\n",
    ],
)
def test_projection_retains_every_call_expression(tmp_path: Path, source: str) -> None:
    """Retain the complete call trees, including deferred alias expressions."""
    target = tmp_path / "source.py"
    _ = target.write_text(source)
    projected, edits = project_source(target)
    before = sorted(ast.dump(node) for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call))
    after = sorted(ast.dump(node) for node in ast.walk(ast.parse(projected)) if isinstance(node, ast.Call))
    assert before == after
    assert edits > 0
    assert projected.count("\n") == source.count("\n")


@pytest.mark.parametrize(
    "source",
    [
        "def f[T: eval(input())](value: T):\n return value\n",
        "def f[T = eval(input())](value: T):\n return value\n",
        "type Alias[T] = list[T]\n",
    ],
)
def test_unqualified_type_parameter_projection_is_rejected(tmp_path: Path, source: str) -> None:
    """Bounds, defaults and generic aliases cannot disappear from a scan."""
    target = tmp_path / "source.py"
    _ = target.write_text(source)
    with pytest.raises(RuntimeError, match="require explicit qualification"):
        _ = project_source(target)
