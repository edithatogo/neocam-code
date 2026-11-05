# ruff: ignore[implicit-namespace-package] -- standalone security-tool entrypoint
"""Prepare the pinned upstream Python rules for internal security analysis."""

import hashlib
import json
import sys
import tarfile
from pathlib import Path

import yaml


def prepare(archive: Path, destination: Path) -> None:
    """Verify upstream bytes and compile uniquely named Python rules.

    Raises:
        ValueError: Archive, inventory or compiled-rule integrity checks fail.
    """
    lock = json.loads(Path(__file__).with_name("rules-lock.json").read_text())
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    if digest != lock["archive_sha256"]:
        message = "Upstream security-rule archive digest differs"
        raise ValueError(message)
    rules = []
    with tarfile.open(archive, "r:gz") as source:
        for member in sorted(source.getmembers(), key=lambda item: Path(item.name)):
            relative = Path(*Path(member.name).parts[1:])
            if not member.isfile() or relative.parts[0] != "python" or relative.suffix != ".yaml":
                continue
            stream = source.extractfile(member)
            if stream is None:
                message = "Cannot read a declared rule member"
                raise ValueError(message)
            content = yaml.safe_load(stream.read())
            if not content:
                continue
            for rule in content.get("rules", []):
                prefix = ".".join(relative.with_suffix("").parts)
                rule["id"] = prefix + "." + rule["id"]
                rules.append(rule)
    rendered = yaml.safe_dump({"rules": rules}, sort_keys=False).encode()
    if len(rules) != lock["python_rule_count"]:
        message = "Upstream rule inventory differs"
        raise ValueError(message)
    if hashlib.sha256(rendered).hexdigest() != lock["compiled_rules_sha256"]:
        message = "Compiled security-rule digest differs"
        raise ValueError(message)
    destination.write_bytes(rendered)


if __name__ == "__main__":
    prepare(Path(sys.argv[1]), Path(sys.argv[2]))
