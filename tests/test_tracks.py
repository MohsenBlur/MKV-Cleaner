# test_tracks.py

from pathlib import Path
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.tracks import build_cmd, Track  # noqa: E402
from core.config import DEFAULTS


def test_build_cmd_flags():
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=True,
        ),
        Track(
            idx=1,
            tid=2,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=True,
            name="English CC",
            default_subtitle=True,
        ),
    ]
    DEFAULTS["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=True, wipe_all=False)
    assert cmd == [
        "mkvmerge",
        "--forced-track",
        "2:no",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "-o",
        str(dst),
        str(src),
    ]

    DEFAULTS["backend"] = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, wipe_forced=True, wipe_all=False)
    assert cmd == [
        "ffmpeg",
        "-i",
        str(src),
        "-map",
        "0",
        "-disposition:a:0",
        "default",
        "-disposition:s:0",
        "default",
        "-c",
        "copy",
        str(dst),
    ]


def test_build_cmd_wipe_all():
    src = Path("in.mkv")
    dst = Path("out.mkv")
    tracks = [
        Track(
            idx=0,
            tid=1,
            type="audio",
            codec="aac",
            language="eng",
            forced=False,
            name="English",
            default_audio=True,
        ),
        Track(
            idx=1,
            tid=2,
            type="subtitles",
            codec="srt",
            language="eng",
            forced=True,
            name="English CC",
            default_subtitle=True,
        ),
    ]
    DEFAULTS["backend"] = "mkvtoolnix"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "mkvmerge",
        "--no-subtitles",
        "--forced-track",
        "2:yes",
        "--default-track",
        "1:yes",
        "--default-track",
        "2:yes",
        "-o",
        str(dst),
        str(src),
    ]

    DEFAULTS["backend"] = "ffmpeg"
    cmd = build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=True)
    assert cmd == [
        "ffmpeg",
        "-i",
        str(src),
        "-map",
        "0",
        "-map",
        "-0:2",
        "-disposition:a:0",
        "default",
        "-c",
        "copy",
        str(dst),
    ]
