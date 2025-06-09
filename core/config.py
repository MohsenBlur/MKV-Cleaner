"""Configuration helpers and executable path setup."""

from __future__ import annotations

import logging
from pathlib import Path
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
    EXT = '.exe' if os.name == 'nt' else ''
    mkvmerge_path = bindir / f"mkvmerge{EXT}"
    mkvextract_path = bindir / f"mkvextract{EXT}"
    ffmpeg_path = bindir / f"ffmpeg{EXT}"
    ffprobe_path = bindir / f"ffprobe{EXT}"
    MKVMERGE = str(mkvmerge_path) if mkvmerge_path.exists() else f"mkvmerge{EXT}"
    MKVEXTRACT = (
        str(mkvextract_path) if mkvextract_path.exists() else f"mkvextract{EXT}"
    )
    FFMPEG = str(ffmpeg_path) if ffmpeg_path.exists() else f"ffmpeg{EXT}"
    FFPROBE = str(ffprobe_path) if ffprobe_path.exists() else f"ffprobe{EXT}"
else:
    EXT = '.exe' if os.name == 'nt' else ''
    MKVMERGE = f"mkvmerge{EXT}"
    MKVEXTRACT = f"mkvextract{EXT}"
    FFMPEG = f"ffmpeg{EXT}"
    FFPROBE = f"ffprobe{EXT}"

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
