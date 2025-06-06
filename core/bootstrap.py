"""Utilities to bootstrap required binaries and Python packages."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import hashlib
from pathlib import Path

# Directory containing ``mkv_cleaner.py``
APP_DIR = Path(__file__).resolve().parents[1]

# Environment variable to skip downloads/installations
SKIP_BOOTSTRAP = os.environ.get("MKVCLEANER_SKIP_BOOTSTRAP")


def ensure_binary(exe_name: str, url: str, checksum: str | None = None) -> str:
    """Ensure ``exe_name`` exists next to ``mkv_cleaner.py``.

    If the executable is missing it will be downloaded from ``url`` which is
    expected to be an archive containing the program. The optional ``checksum``
    should be the SHA256 hex digest of the archive. If provided, the downloaded
    archive is verified before unpacking and a :class:`ValueError` is raised on
    mismatch. The executable is extracted and its local path is returned.
    """
    exe_path = APP_DIR / exe_name
    if SKIP_BOOTSTRAP:
        return str(exe_path)
    if exe_path.exists():
        return str(exe_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        suffix = Path(url).suffix or '.zip'
        archive = Path(tmpdir) / f"download{suffix}"
        urllib.request.urlretrieve(url, archive)
        if checksum is not None:
            h = hashlib.sha256()
            with open(archive, "rb") as fh:
                for chunk in iter(lambda: fh.read(8192), b""):
                    h.update(chunk)
            if h.hexdigest().lower() != checksum.lower():
                raise ValueError("Checksum mismatch")
        shutil.unpack_archive(str(archive), tmpdir)

        found = None
        for root, _, files in os.walk(tmpdir):
            if exe_name in files:
                found = Path(root) / exe_name
                break
        if not found:
            raise FileNotFoundError(f"{exe_name} not found in archive")
        shutil.copy2(found, exe_path)
        exe_path.chmod(0o755)

    return str(exe_path)


def ensure_python_package(pkg: str) -> None:
    """Import ``pkg`` or install it via ``pip`` if missing."""
    if SKIP_BOOTSTRAP:
        return
    try:
        __import__(pkg)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)
