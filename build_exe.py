"""Build a standalone MKV Cleaner executable using PyInstaller.

This script bundles the application and all Python dependencies into a single
``MKVCleaner.exe`` file. The backend tools (``mkvmerge``, ``mkvextract``,
``ffmpeg`` and ``ffprobe``) are intentionally excluded from the bundle. They
must be available on ``PATH`` when running the generated executable.

Run this script with ``python build_exe.py``. The resulting executable will be
placed in the ``dist`` directory.
"""

from __future__ import annotations

import os
from pathlib import Path
from PyInstaller.__main__ import run

HERE = Path(__file__).resolve().parent

logo = HERE / "MKV-Cleaner_logo.png"
fonts_dir = HERE / "fonts"

sep = ';' if os.name == 'nt' else ':'

opts = [
    "--name=MKVCleaner",
    "--onefile",
    "--noconsole",
    f"--add-data={logo}{sep}.",
    f"--add-data={fonts_dir}{sep}fonts",
    str(HERE / "mkv_cleaner.py"),
]

if __name__ == "__main__":
    run(opts)
