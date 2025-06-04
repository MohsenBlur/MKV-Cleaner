# core/config.py

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

DEFAULTS: Dict[str, Any] = {
    "mkvmerge_cmd": "mkvmerge",
    "mkvextract_cmd": "mkvextract",
    "output_dir": "cleaned",
    "max_workers": 4,
}

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

def setup_logging(level: int | str = logging.INFO) -> None:
    logging.basicConfig(format=LOG_FORMAT, level=level)
    logging.getLogger("core").setLevel(level)

def load_config(path: Path | None = None) -> Dict[str, Any]:
    return DEFAULTS.copy()
