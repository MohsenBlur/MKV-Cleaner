import logging
import sys
import os
from pathlib import Path
import subprocess
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


def test_run_command_capture(monkeypatch):
    called = {}

    def fake_run(cmd, **kw):
        called.update(kw)
        return subprocess.CompletedProcess(cmd, 0, stdout="out", stderr="")

    monkeypatch.setattr(tracks.subprocess, "run", fake_run)
    res = tracks.run_command(["echo", "hi"])
    assert called.get("capture_output") is True
    assert res.stdout == "out"


def test_run_command_no_capture(monkeypatch):
    called = {}

    def fake_run(cmd, **kw):
        called.update(kw)
        return subprocess.CompletedProcess(cmd, 0, stdout="out", stderr="")

    monkeypatch.setattr(tracks.subprocess, "run", fake_run)
    res = tracks.run_command(["echo", "hi"], capture=False)
    assert called.get("capture_output") is True
    assert res.stdout == ""


def test_run_command_error_no_stderr(monkeypatch, caplog):
    called = {}

    def fake_run(cmd, **kw):
        called.update(kw)
        raise subprocess.CalledProcessError(1, cmd, stderr=None)

    monkeypatch.setattr(tracks.subprocess, "run", fake_run)
    caplog.set_level(logging.ERROR)
    with pytest.raises(subprocess.CalledProcessError):
        tracks.run_command(["bad"], capture=False)
    assert called.get("capture_output") is True
    assert "Command failed" in caplog.text

