import logging
import sys
import os
from pathlib import Path
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.tracks as tracks  # noqa: E402


def test_run_command_missing(monkeypatch, caplog):
    def fake_run(*a, **kw):
        raise FileNotFoundError()

    monkeypatch.setattr(tracks.subprocess, "run", fake_run)
    caplog.set_level(logging.ERROR)
    with pytest.raises(tracks.CommandNotFoundError):
        tracks.run_command(["mkvmerge", "-J", str(Path("in.mkv"))])
    assert "mkvmerge not found on PATH" in caplog.text

