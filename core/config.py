from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import json
import os
import sys

from core.bootstrap import ensure_binary

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
    ext = '.exe' if os.name == 'nt' else ''
    if os.environ.get('MKVCLEANER_SKIP_BOOTSTRAP'):
        MKVMERGE = f"mkvmerge{ext}"
        MKVEXTRACT = f"mkvextract{ext}"
        FFMPEG = f"ffmpeg{ext}"
        FFPROBE = f"ffprobe{ext}"
    else:
        if os.name == 'nt':
            mkv_url = 'https://mkvtoolnix.download/windows/latest-release/mkvtoolnix-cli.zip'
            ff_url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        else:
            mkv_url = 'https://mkvtoolnix.download/linux/latest-release/mkvtoolnix-cli.tar.xz'
            ff_url = 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz'

        MKVMERGE = ensure_binary(f"mkvmerge{ext}", mkv_url)
        MKVEXTRACT = ensure_binary(f"mkvextract{ext}", mkv_url)
        FFMPEG = ensure_binary(f"ffmpeg{ext}", ff_url)
        FFPROBE = ensure_binary(f"ffprobe{ext}", ff_url)

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
