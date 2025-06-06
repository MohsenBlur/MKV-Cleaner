"""Utility functions for reading configuration and setting up logging."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
from dataclasses import dataclass
import json
import os
import sys



try:  # Python >=3.11
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - fallback for older versions
    import tomli as tomllib

if getattr(sys, 'frozen', False):  # Running from PyInstaller bundle
    bindir = Path(getattr(sys, '_MEIPASS', Path(sys.executable).parent))
    ext = '.exe' if os.name == 'nt' else ''
    MKVMERGE = str(bindir / f"mkvmerge{ext}")
    MKVEXTRACT = str(bindir / f"mkvextract{ext}")
    FFMPEG = str(bindir / f"ffmpeg{ext}")
    FFPROBE = str(bindir / f"ffprobe{ext}")
else:
    ext = '.exe' if os.name == 'nt' else ''
    MKVMERGE = f"mkvmerge{ext}"
    MKVEXTRACT = f"mkvextract{ext}"
    FFMPEG = f"ffmpeg{ext}"
    FFPROBE = f"ffprobe{ext}"

@dataclass
class AppConfig:
    """Application configuration."""

    backend: str = "ffmpeg"  # or "mkvtoolnix"
    mkvmerge_cmd: str = MKVMERGE
    mkvextract_cmd: str = MKVEXTRACT
    ffmpeg_cmd: str = FFMPEG
    ffprobe_cmd: str = FFPROBE
    output_dir: str = "cleaned"
    max_workers: int = 4
    track_font_size: int = 16
    preview_font_size: int = 16

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

def setup_logging(level: int | str = logging.INFO) -> None:
    """Configure application logging."""

    logging.basicConfig(format=LOG_FORMAT, level=level)
    logging.getLogger("core").setLevel(level)

def load_config(path: Path | None = None) -> AppConfig:
    """Load configuration from ``path`` and merge with defaults."""

    cfg = AppConfig()
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
            for key, val in data.items():
                if hasattr(cfg, key):
                    setattr(cfg, key, val)
    return cfg
