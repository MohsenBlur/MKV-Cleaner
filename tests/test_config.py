import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.config import load_config, DEFAULTS  # noqa: E402


def test_load_config_json(tmp_path):
    conf_file = tmp_path / "conf.json"
    conf_file.write_text(json.dumps({"backend": "ffmpeg", "output_dir": "here"}))

    cfg = load_config(conf_file)
    assert cfg["backend"] == "ffmpeg"
    assert cfg["output_dir"] == "here"
    # ensure default populated
    assert cfg["mkvmerge_cmd"] == DEFAULTS["mkvmerge_cmd"]
    assert cfg["track_font_size"] == DEFAULTS["track_font_size"]
    assert cfg["preview_font_size"] == DEFAULTS["preview_font_size"]


def test_load_config_toml(tmp_path):
    conf_file = tmp_path / "conf.toml"
    conf_file.write_text("backend='ffmpeg'\nmax_workers=8")

    cfg = load_config(conf_file)
    assert cfg["backend"] == "ffmpeg"
    assert cfg["max_workers"] == 8
    # unchanged value
    assert cfg["output_dir"] == DEFAULTS["output_dir"]
    assert cfg["track_font_size"] == DEFAULTS["track_font_size"]
    assert cfg["preview_font_size"] == DEFAULTS["preview_font_size"]
