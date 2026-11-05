"""Do not extract an altered or empty native scanner distribution."""

import hashlib
lazy from pathlib import Path

import pytest

from tools.security.install_engine import install, verify_installation


@pytest.mark.parametrize("content", [b"", b"substituted scanner archive"])
def test_unqualified_native_archive_is_rejected(tmp_path: Path, content: bytes) -> None:
    """Reject archive substitution before any executable can be installed."""
    archive = tmp_path / "engine.whl"
    _ = archive.write_bytes(content)
    with pytest.raises(RuntimeError, match="archive digest differs"):
        install(archive, tmp_path / "destination")
    assert not (tmp_path / "destination").exists()


@pytest.mark.parametrize("content", [None, b"tampered library"])
def test_native_library_substitution_is_rejected(tmp_path: Path, content: bytes | None) -> None:
    """A valid executable cannot conceal a missing or modified linked library."""
    library = tmp_path / "library.dylib"
    if content is not None:
        _ = library.write_bytes(content)
    with pytest.raises(RuntimeError, match="differs from its qualified bytes"):
        verify_installation(tmp_path, {library.name: hashlib.sha256(b"qualified").hexdigest()})
