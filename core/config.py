# core/config.py

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import json
import os
import sys

try:  # Python >=3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    import tomli as tomllib

if getattr(sys, 'frozen', False):  # Running from PyInstaller bundle
    bindir = Path(sys.executable).parent
    ext = '.exe' if os.name == 'nt' else ''
    MKVMERGE = str(bindir / f"mkvmerge{ext}")
    MKVEXTRACT = str(bindir / f"mkvextract{ext}")
    FFMPEG = str(bindir / f"ffmpeg{ext}")
    FFPROBE = str(bindir / f"ffprobe{ext}")
else:
    MKVMERGE = "mkvmerge"
    MKVEXTRACT = "mkvextract"
    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"

DEFAULTS: Dict[str, Any] = {
    "backend": "mkvtoolnix",  # or "ffmpeg"
    "mkvmerge_cmd": MKVMERGE,
    "mkvextract_cmd": MKVEXTRACT,
    "ffmpeg_cmd": FFMPEG,
    "ffprobe_cmd": FFPROBE,
    "output_dir": "cleaned",
    "max_workers": 4,
}

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

def setup_logging(level: int | str = logging.INFO) -> None:
    logging.basicConfig(format=LOG_FORMAT, level=level)
    logging.getLogger("core").setLevel(level)

def load_config(path: Path | None = None) -> Dict[str, Any]:
    """Load configuration from ``path`` and merge with :data:`DEFAULTS`."""

    cfg = DEFAULTS.copy()
    if path:
        suffix = path.suffix.lower()
        with open(path, "rb") as fh:
            if suffix == ".json":
                data = json.load(fh)
            elif suffix == ".toml":
                data = tomllib.load(fh)
            else:
                raise ValueError(f"Unsupported config format: {suffix}")
        if isinstance(data, dict):
            cfg.update(data)
    return cfg
