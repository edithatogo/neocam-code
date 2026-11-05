# ruff: ignore[implicit-namespace-package] -- standalone native-engine installer
"""Extract the unchanged native scanner from an immutable upstream archive."""

import hashlib
import json
import platform
import sys
import tarfile
from pathlib import Path


def platform_key() -> str:
    """Return the exact qualified operating-system and architecture pair.

    Returns:
        str: The engine-lock platform key.
    """
    return platform.system().lower() + "-" + platform.machine().lower()


def verify_installation(destination: Path, expected: dict[str, str]) -> None:
    """Reject missing or changed native executables, libraries and licences.

    Raises:
        RuntimeError: An installed native distribution member differs.
    """
    for name, digest in expected.items():
        target = destination / name
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            message = "Native security engine differs from its qualified bytes"
            raise RuntimeError(message)


def engine_path() -> Path:
    """Locate and verify the complete native distribution before invocation.

    Returns:
        Path: The immutable qualified executable.
    """
    lock = json.loads(Path(__file__).with_name("engine-lock.json").read_text())
    expected = lock["platforms"][platform_key()]["files_sha256"]
    destination = Path(__file__).resolve().parents[2] / ".tools/opengrep"
    verify_installation(destination, expected)
    return destination / "opengrep-core"


def install(archive: Path, destination: Path) -> None:
    """Install only native bytes and licences from a digest-verified archive.

    Raises:
        RuntimeError: Archive integrity or a selected archive path is invalid.
    """
    lock = json.loads(Path(__file__).with_name("engine-lock.json").read_text())
    pin = lock["platforms"][platform_key()]
    if hashlib.sha256(archive.read_bytes()).hexdigest() != pin["archive_sha256"]:
        message = "Native engine archive digest differs"
        raise RuntimeError(message)
    with tarfile.open(archive, "r:gz") as source:
        member = source.getmember("opengrep-core")
        stream = source.extractfile(member) if member.isfile() else None
        if stream is None:
            message = "Native engine archive has no regular core executable"
            raise RuntimeError(message)
        destination.mkdir(parents=True, exist_ok=True)
        target = destination / "opengrep-core"
        target.write_bytes(stream.read())
        target.chmod(0o755)
    licence = Path(__file__).with_name("licenses") / "OpenGrep-LICENSE"
    (destination / "LICENSE").write_bytes(licence.read_bytes())
    verify_installation(destination, pin["files_sha256"])


if __name__ == "__main__":
    install(Path(sys.argv[1]), Path(__file__).resolve().parents[2] / ".tools/opengrep")
