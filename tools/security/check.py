# ruff: ignore[implicit-namespace-package] -- standalone security-tool entrypoint
"""Run private, fail-closed Python security analysis and synthetic controls."""

import argparse
import ast
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import re
import shutil
import subprocess  # ruff: ignore[suspicious-subprocess-import] -- fixed scanner modules and resolved Git executable, without a shell
import sys
import tempfile
import tomllib
from pathlib import Path

from tools.security.install_engine import engine_path


def verify_rule_bytes(rules: Path, expected: str) -> None:
    """Reject empty, substituted or altered security rules before scanning.

    Raises:
        RuntimeError: Rule bytes differ from the qualified bundle.
    """
    if hashlib.sha256(rules.read_bytes()).hexdigest() != expected:
        message = "Security rules differ from the qualified bundle"
        raise RuntimeError(message)


def verify_toolchain(rules: Path) -> dict[str, str]:
    """Check installed tool versions and the immutable internal-use rule set.

    Returns:
        dict[str, str]: Actual qualified package versions.

    Raises:
        RuntimeError: Installed packages or prohibited imports violate policy.
    """
    project = tomllib.loads(Path(__file__).with_name("pyproject.toml").read_text())
    versions = {}
    for specification in project["project"]["dependencies"]:
        name, expected = specification.split("==")
        versions[name] = importlib.metadata.version(name)
        if versions[name] != expected:
            message = "Security tooling differs from the pinned versions"
            raise RuntimeError(message)
    if any(
        importlib.util.find_spec(name) is not None for name in ("pandas", "xarray", "semgrep", "mcp", "opentelemetry")
    ):
        message = "Prohibited dataframe or Python CLI dependencies are present in the security environment"
        raise RuntimeError(message)
    lock = json.loads(Path(__file__).with_name("rules-lock.json").read_text())
    verify_rule_bytes(rules, lock["compiled_rules_sha256"])
    versions["opengrep-core"] = json.loads(Path(__file__).with_name("engine-lock.json").read_text())["version"]
    _ = engine_path()
    return versions


def verify_scanner_diagnostics(diagnostics: str) -> None:
    """Reject incomplete-analysis warnings even when JSON omits them.

    Raises:
        RuntimeError: The scanner reports a warning, error or fixpoint timeout.
    """
    cleaned = re.sub(r"\x1b\[[0-9;]*m", "", diagnostics).casefold()
    if any(marker in cleaned for marker in ("[warning]", "[error]", "fixpoint timeout")):
        message = "Scanner diagnostics report incomplete analysis"
        raise RuntimeError(message)


def execute(command: list[str], report: Path) -> dict:
    """Execute a scanner and retain its complete machine-readable response.

    Returns:
        dict: The scanner's JSON response.

    Raises:
        RuntimeError: The selected command or scanner result is invalid.
    """
    if command[:3] != [sys.executable, "-m", "bandit"] and command[0] != str(engine_path()):
        message = "Only the qualified native engine and Bandit module may execute"
        raise RuntimeError(message)
    result = subprocess.run(command, capture_output=True, text=True, check=False)  # ruff: ignore[subprocess-without-shell-equals-true] -- validated interpreter and scanner module; no shell
    report.with_suffix(".log").write_text(result.stderr, encoding="utf-8")
    report.write_text(result.stdout, encoding="utf-8")
    if result.returncode not in {0, 1}:
        message = f"Security scanner failed with exit {result.returncode}"
        raise RuntimeError(message)
    verify_scanner_diagnostics(result.stderr)
    data = json.loads(result.stdout)
    if data.get("errors"):
        message = "Security scanner reported analysis errors"
        raise RuntimeError(message)
    return data


class AliasProjection(ast.NodeTransformer):
    """Represent a type-alias expression without removing its value AST."""

    @staticmethod
    def visit_TypeAlias(node: ast.TypeAlias) -> ast.Assign:
        """Keep the complete alias value as a conservatively evaluated assignment.

        Returns:
            ast.Assign: The same target and expression.
        """
        return ast.Assign(targets=[node.name], value=node.value, type_comment=None)


def generic_projection(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    lines: list[str],
    offsets: list[int],
    source: str,
) -> tuple[int, int, str]:
    """Expose a generic declaration without discarding bounds or defaults.

    Returns:
        tuple[int, int, str]: A line-preserving declaration edit.

    Raises:
        RuntimeError: A type parameter contains an expression or unsupported syntax.
    """
    if any(
        not isinstance(param, ast.TypeVar) or param.bound is not None or param.default_value is not None
        for param in node.type_params
    ):
        message = "Bounded or defaulted type parameters require explicit qualification"
        raise RuntimeError(message)
    line = lines[node.lineno - 1]
    keyword = (
        "class "
        if isinstance(node, ast.ClassDef)
        else "async def "
        if isinstance(node, ast.AsyncFunctionDef)
        else "def "
    )
    prefix = keyword + node.name
    if not line[node.col_offset :].startswith(prefix):
        message = "Unsupported generic declaration spelling"
        raise RuntimeError(message)
    start = offsets[node.lineno - 1] + node.col_offset + len(prefix)
    end = source.index("]", start) + 1
    if not source[start:end].startswith("[") or "\n" in source[start:end]:
        message = "Unsupported generic declaration spelling"
        raise RuntimeError(message)
    node.type_params = []
    return start, end, " " * (end - start)


def alias_projection(node: ast.TypeAlias, offsets: list[int], source: str) -> tuple[int, int, str]:
    """Retain the complete alias expression under an assignment spelling.

    Returns:
        tuple[int, int, str]: The declaration-keyword edit.

    Raises:
        RuntimeError: A declaration has unqualified generic parameters or spelling.
    """
    start = offsets[node.lineno - 1] + node.col_offset
    if node.type_params or source[start : start + 5] != "type ":
        message = "Generic type aliases require explicit qualification"
        raise RuntimeError(message)
    return start, start + 5, ""


def exception_projection(item: ast.Tuple, offsets: list[int], source: str) -> list[tuple[int, int, str]]:
    """Restore optional exception-tuple parentheses without changing the AST.

    Returns:
        list[tuple[int, int, str]]: Zero or two delimiter edits.
    """
    start = offsets[item.lineno - 1] + item.col_offset
    end = offsets[item.end_lineno - 1] + item.end_col_offset
    return [] if source[start] == "(" else [(start, start, "("), (end, end, ")")]


def project_source(source_path: Path) -> tuple[str, int]:
    """Expose supported syntax while retaining every executable expression.

    Returns:
        tuple[str, int]: The projected source and number of syntax edits.

    Raises:
        RuntimeError: A declaration, source spelling or AST change is unsupported.
    """
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    edits = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and node.is_lazy:
            start = offsets[node.lineno - 1] + node.col_offset
            if source[start : start + 5] != "lazy ":
                message = "Unsupported lazy-import spelling requires explicit qualification"
                raise RuntimeError(message)
            edits.append((start, start + 5, ""))
            node.is_lazy = 0
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.type_params:
            edits.append(generic_projection(node, lines, offsets, source))
        if isinstance(node, ast.TypeAlias):
            edits.append(alias_projection(node, offsets, source))
        if isinstance(node, ast.ExceptHandler) and isinstance(node.type, ast.Tuple):
            edits.extend(exception_projection(node.type, offsets, source))
    rendered = source
    for start, end, replacement in sorted(edits, reverse=True):
        rendered = rendered[:start] + replacement + rendered[end:]
    expected_tree = AliasProjection().visit(tree)
    if ast.dump(ast.parse(rendered)) != ast.dump(expected_tree):
        message = "Security projection changed Python statements or expressions"
        raise RuntimeError(message)
    return rendered, len(edits)


def verify_rule_inventory(rules: list[str], *, skipped: bool, expected_count: int, expected_digest: str) -> None:
    """Reject skipped, duplicated, missing or substituted native rules.

    Raises:
        RuntimeError: The native engine did not execute every qualified rule.
    """
    digest = hashlib.sha256("\n".join(sorted(rules)).encode()).hexdigest()
    if skipped or len(rules) != expected_count or digest != expected_digest:
        message = "Native security rule inventory differs"
        raise RuntimeError(message)


def semgrep(rules: Path, targets: list[str], report: Path) -> dict:
    """Run all pinned rules, with telemetry and suppression comments disabled.

    Returns:
        dict: The complete scanner report.

    Raises:
        RuntimeError: Projection parity or complete scanning cannot be established.
    """
    with tempfile.TemporaryDirectory(prefix="neocam-sast-source-") as folder:
        translated = {}
        projection = []
        absolute = [Path(name).resolve() for name in targets]
        base = Path(os.path.commonpath(absolute)) if Path(targets[0]).is_absolute() else Path.cwd()
        if base.is_file():
            base = base.parent
        for name in targets:
            rendered, import_count = project_source(Path(name))
            target = Path(folder) / Path(name).resolve().relative_to(base)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(rendered, encoding="utf-8")
            translated[str(target)] = name
            projection.append({
                "path": name,
                "syntax_edits": import_count,
                "scan_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
            })
        target_spec = Path(folder) / "targets.json"
        target_spec.write_text(
            json.dumps([
                ["CodeTarget", {"path": path, "analyzer": analyzer, "products": ["sast"]}]
                for path in translated
                for analyzer in ("python", "generic", "regex")
            ])
        )
        data = execute(
            [
                str(engine_path()),
                "-rules",
                str(rules),
                "-targets",
                str(target_spec),
                "-json_nodots",
                "-strict",
                "-fast",
                "-j",
                "1",
            ],
            report,
        )
        lock = json.loads(Path(__file__).with_name("rules-lock.json").read_text())
        verify_rule_inventory(
            [item[0] for item in data["rules_by_engine"]],
            skipped=bool(data["skipped_rules"]) or any(item[1] != "OSS" for item in data["rules_by_engine"]),
            expected_count=lock["python_rule_count"],
            expected_digest=lock["rule_ids_sha256"],
        )
        scanned = set(data["paths"]["scanned"])
        if scanned != set(translated):
            message = "Semgrep did not scan every source projection"
            raise RuntimeError(message)
        data["paths"]["scanned"] = [translated[name] for name in data["paths"]["scanned"]]
        for finding in data["results"]:
            finding["path"] = translated[finding["path"]]
        data["source_projection"] = projection
        report.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return data


def bandit(targets: list[str], report: Path) -> dict:
    """Retain every severity and confidence level from native Python AST checks.

    Returns:
        dict: The complete scanner report.
    """
    return execute(
        [sys.executable, "-m", "bandit", "--ignore-nosec", "-q", "-f", "json", *targets],
        report,
    )


def controls(rules: Path, output: Path) -> None:
    """Require detection of seeded vulnerabilities and acceptance of safe variants.

    Raises:
        RuntimeError: A vulnerability or safe-variant control behaves incorrectly.
    """
    cases = {
        "generic_code_execution": (
            "def run[T](value: T):\n return eval(value)",
            "def run[T](value: T):\n return str(value)",
        ),
        "alias_code_execution": ("type Alias = eval(input())", "type Alias = str"),
        "exception_code_execution": (
            "try:\n pass\nexcept ValueError, TypeError:\n eval(input())",
            "try:\n pass\nexcept ValueError, TypeError:\n pass",
        ),
        "suppression_rejection": ("eval(input())  # nosemgrep # nosec B307", "import json\njson.loads(input())"),
        "code_execution": ("eval(input())", "import json\njson.loads(input())"),
        "shell_injection": (
            "import subprocess\nsubprocess.run(input(), shell=True)",
            "import subprocess\nsubprocess.run(['/usr/bin/true'], check=True)",
        ),
        "deserialization": (
            "import pickle\npickle.loads(input().encode())",
            "import json\njson.loads(input())",
        ),
        "tls_verification": (
            "import requests\nrequests.get('https://example.org', verify=False, timeout=5)",
            (
                "import requests\n"
                "response = requests.get('https://example.org', verify=True, timeout=5)\n"
                "response.raise_for_status()"
            ),
        ),
        "weak_hash": (
            "import hashlib\nhashlib.md5(input().encode())",
            "import hashlib\nhashlib.sha256(input().encode())",
        ),
        "unsafe_yaml": (
            "import yaml\nyaml.load(input(), Loader=yaml.Loader)",
            "import yaml\nyaml.safe_load(input())",
        ),
        "lazy_deserialization": (
            "lazy import pickle\npickle.loads(input().encode())",
            "lazy import json\njson.loads(input())",
        ),
    }
    required_bandit = {
        "generic_code_execution": "B307",
        "alias_code_execution": "B307",
        "exception_code_execution": "B307",
        "suppression_rejection": "B307",
        "code_execution": "B307",
        "shell_injection": "B602",
        "deserialization": "B301",
        "tls_verification": "B501",
        "weak_hash": "B324",
        "unsafe_yaml": "B506",
        "lazy_deserialization": "B301",
    }
    with tempfile.TemporaryDirectory(prefix="neocam-security-controls-") as folder:
        directory = Path(folder)
        fixtures = []
        for name, (bad, safe) in cases.items():
            for label, source in (("bad", bad), ("safe", safe)):
                target = directory / f"{name}_{label}.py"
                target.write_text(source + "\n")
                fixtures.append((name, label, str(target)))
        targets = [target for _, _, target in fixtures]
        sg = semgrep(rules, targets, output / "control-semgrep.json")
        for name, label, target in fixtures:
            if any(item["path"] == target for item in sg["results"]) != (label == "bad"):
                message = f"Native rule control failed: {name} {label}"
                raise RuntimeError(message)
        bd = bandit(targets, output / "control-bandit.json")
        for name, label, target in fixtures:
            sg_findings = [item for item in sg["results"] if item["path"] == target]
            bd_findings = [item for item in bd["results"] if item["filename"] == target]
            findings = sg_findings + [item for item in bd_findings if item["issue_severity"] != "LOW"]
            if bool(findings) != (label == "bad"):
                message = f"Security control failed: {name} {label}"
                raise RuntimeError(message)
            if label == "bad" and required_bandit[name] not in {item["test_id"] for item in bd_findings}:
                message = f"The expected vulnerability rule did not trigger: {name}"
                raise RuntimeError(message)


def verify_source_review(expected: dict[str, str], observed: dict[str, str]) -> None:
    """Require a fresh review for every added, changed or removed Python file.

    Raises:
        RuntimeError: The complete source snapshot differs from its review.
    """
    if expected != observed:
        message = "Source differs from the completed security review"
        raise RuntimeError(message)


def review_findings(findings: list, digests: dict[str, str]) -> None:
    """Bind adjudicated audit/style findings to exact reviewed source bytes.

    Raises:
        RuntimeError: A security finding or unreviewed source change is present.
    """
    reviewed = json.loads(Path(__file__).with_name("reviewed-findings.json").read_text())
    verify_source_review(reviewed["source_sha256"], digests)
    expected = {
        tuple(item[key] for key in ("rule", "path", "start", "end", "source_sha256")) for item in reviewed["findings"]
    }
    observed = set()
    for item in findings:
        metadata = item["extra"].get("metadata", {})
        if metadata.get("category") == "security" and metadata.get("confidence") != "LOW":
            message = "A medium/high-confidence security finding must be corrected"
            raise RuntimeError(message)
        rule = item["check_id"][item["check_id"].index("python.") :]
        observed.add((rule, item["path"], item["start"]["line"], item["end"]["line"], digests[item["path"]]))
    if observed != expected:
        message = "Audit/style findings differ from the exact reviewed source inventory"
        raise RuntimeError(message)


def main() -> None:
    """Scan tracked Python files and emit an exact-source acceptance receipt.

    Raises:
        RuntimeError: Runtime, inventory, findings or source-integrity checks fail.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if sys.version_info[:3] != (3, 15, 1):
        message = "Security qualification requires Python 3.15.1"
        raise RuntimeError(message)
    os.environ["SEMGREP_ENABLE_VERSION_CHECK"] = "0"
    os.environ["SEMGREP_SEND_METRICS"] = "off"
    if os.environ.get("SEMGREP_APP_TOKEN"):
        message = "Private scanning must run without a Semgrep cloud token"
        raise RuntimeError(message)
    args.output.mkdir(parents=True, exist_ok=True)
    versions = verify_toolchain(args.rules)
    controls(args.rules, args.output)
    git_executable = shutil.which("git")
    if git_executable is None:
        message = "Git is required to identify the complete source inventory"
        raise RuntimeError(message)
    tracked = subprocess.check_output([git_executable, "ls-files", "-z", "--", "*.py"]).decode().split("\0")  # ruff: ignore[subprocess-without-shell-equals-true] -- resolved Git executable and fixed read-only arguments
    targets = [name for name in tracked if name]
    if not targets:
        message = "No tracked Python files were selected"
        raise RuntimeError(message)
    digests = {name: hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in targets}
    sg = semgrep(args.rules, targets, args.output / "semgrep.json")
    bd = bandit(targets, args.output / "bandit.json")
    review_findings(sg["results"], digests)
    if any(item["issue_severity"] != "LOW" for item in bd["results"]):
        message = "Security findings require correction or explicit adjudication"
        raise RuntimeError(message)
    scanned = {str(Path(name).resolve()) for name in sg["paths"]["scanned"]}
    if scanned != {str(Path(name).resolve()) for name in targets}:
        message = "Semgrep did not analyse the complete tracked Python inventory"
        raise RuntimeError(message)
    for name, digest in digests.items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            message = "Source changed during security analysis"
            raise RuntimeError(message)
    receipt = {
        "passed": True,
        "python": sys.version,
        "tool_versions": versions,
        "source_sha256": digests,
        "native_engine_sha256": hashlib.sha256(engine_path().read_bytes()).hexdigest(),
        "rules_executed": len(sg["rules_by_engine"]),
        "rules_sha256": hashlib.sha256(args.rules.read_bytes()).hexdigest(),
        "controls_passed": 22,
        "configuration_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in (
                "rules-lock.json",
                "engine-lock.json",
                "reviewed-findings.json",
                "uv.lock",
            )
        },
        "bandit_low_severity_review": len(bd["results"]),
        "semgrep_reviewed_audit_style_findings": len(sg["results"]),
        "unreviewed_findings": 0,
        "scanner_errors": 0,
        "telemetry": False,
        "projection_contract": (
            "All statements/expressions retained. Native AST equality after lazy-import, simple-alias "
            "and unbounded generic-declaration normalization; exception parentheses have identical AST. "
            "Bounds/defaults and generic aliases fail closed. Bandit parses original Python 3.15 source."
        ),
    }
    (args.output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
