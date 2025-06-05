# core/config.py

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import json

try:  # Python >=3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    import tomli as tomllib

DEFAULTS: Dict[str, Any] = {
    "backend": "mkvtoolnix",  # or "ffmpeg"
    "mkvmerge_cmd": "mkvmerge",
    "mkvextract_cmd": "mkvextract",
    "ffmpeg_cmd": "ffmpeg",
    "ffprobe_cmd": "ffprobe",
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
