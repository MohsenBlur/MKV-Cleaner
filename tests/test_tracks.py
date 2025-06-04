# test_tracks.py

from core.tracks import build_cmd, Track
from pathlib import Path

def test_build_cmd_flags():
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(idx=0, tid=1, type="audio", codec="aac", language="eng", forced=False, name="English", default_audio=True),
        Track(idx=1, tid=2, type="subtitles", codec="srt", language="eng", forced=True, name="English CC", default_subtitle=True)
    ]
    cmd = build_cmd(src, dst, tracks, wipe_forced=True, wipe_all=False)
    assert "--default-track" in cmd
    assert "--forced-track" in cmd
