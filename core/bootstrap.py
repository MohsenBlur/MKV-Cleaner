from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

# Directory containing ``mkv_cleaner.py``
APP_DIR = Path(__file__).resolve().parents[1]


def ensure_binary(exe_name: str, url: str) -> str:
    """Ensure ``exe_name`` exists next to ``mkv_cleaner.py``.

    If the executable is missing it will be downloaded from ``url`` which is
    expected to be an archive containing the program. The executable is
    extracted and its local path is returned.
    """
    exe_path = APP_DIR / exe_name
    if exe_path.exists():
        return str(exe_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        suffix = Path(url).suffix or '.zip'
        archive = Path(tmpdir) / f"download{suffix}"
        urllib.request.urlretrieve(url, archive)
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
    try:
        __import__(pkg)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", pkg], check=True)

