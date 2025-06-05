# core/tracks.py

from __future__ import annotations
import json
import subprocess
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from core.config import DEFAULTS

logger = logging.getLogger("core.tracks")

@dataclass
class Track:
    idx: int       # index in the UI/table
    tid: int       # real mkvmerge track id
    type: str
    codec: str
    language: str
    forced: bool
    name: str
    default_audio: bool = False
    default_subtitle: bool = False
    removed: bool = False

    def signature(self) -> str:
        return (
            f"{self.tid}-{self.type}-{self.codec}-"
            f"{self.language}-{'F' if self.forced else ''}-{self.name}"
        )

def run_command(cmd: list[str]) -> subprocess.CompletedProcess:
    logger.debug(f"Running: {' '.join(cmd)}")
    try:
        return subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        logger.error("Command failed: %s\n%s", exc, exc.stderr)
        raise

def query_tracks(source: Path) -> List[Track]:
    """Query tracks using the configured backend."""
    if DEFAULTS.get("backend") == "ffmpeg":
        result = run_command([
            DEFAULTS["ffprobe_cmd"],
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            str(source),
        ])
        data = json.loads(result.stdout)
        tracks: List[Track] = []
        for i, t in enumerate(data.get("streams", [])):
            tags = t.get("tags", {})
            disp = t.get("disposition", {})
            tracks.append(
                Track(
                    idx=i,
                    tid=int(t.get("index", i)),
                    type="subtitles" if t.get("codec_type") == "subtitle" else t.get("codec_type", ""),
                    codec=t.get("codec_name", ""),
                    language=tags.get("language", "und"),
                    forced=bool(disp.get("forced", 0)),
                    name=tags.get("title", ""),
                    default_audio=bool(disp.get("default", 0)) if t.get("codec_type") == "audio" else False,
                    default_subtitle=bool(disp.get("default", 0)) if t.get("codec_type") == "subtitle" else False,
                )
            )
        return tracks
    else:
        result = run_command([DEFAULTS["mkvmerge_cmd"], "-J", str(source)])
        data = json.loads(result.stdout)
        tracks: List[Track] = []
        for i, t in enumerate(data.get("tracks", [])):
            p = t.get("properties", {})
            tracks.append(
                Track(
                    idx=i,
                    tid=int(t["id"]),
                    type=t.get("type", ""),
                    codec=p.get("codec_id", ""),
                    language=p.get("language", "und"),
                    forced=p.get("forced_track", False),
                    name=p.get("track_name", ""),
                    default_audio=p.get("default_track", False) if t.get("type") == "audio" else False,
                    default_subtitle=p.get("default_track", False) if t.get("type") == "subtitles" else False,
                )
            )
        return tracks

def build_cmd(
    source: Path,
    destination: Path,
    tracks: List[Track],
    wipe_forced: bool = False,
    wipe_all: bool = False,
) -> list[str]:
    """Build command for the configured backend."""
    if DEFAULTS.get("backend") == "ffmpeg":
        return _build_cmd_ffmpeg(source, destination, tracks, wipe_forced, wipe_all)
    return _build_cmd_mkvmerge(source, destination, tracks, wipe_forced, wipe_all)


def _build_cmd_mkvmerge(
    source: Path,
    destination: Path,
    tracks: List[Track],
    wipe_forced: bool,
    wipe_all: bool,
) -> list[str]:
    cmd: list[str] = [DEFAULTS["mkvmerge_cmd"]]

    # Use tid (real mkvmerge track id) everywhere!
    all_audio_ids = [str(t.tid) for t in tracks if t.type == "audio"]
    all_sub_ids   = [str(t.tid) for t in tracks if t.type == "subtitles"]
    kept_audio    = [str(t.tid) for t in tracks if t.type == "audio" and not t.removed]
    kept_sub      = [str(t.tid) for t in tracks if t.type == "subtitles" and not t.removed]

    if kept_audio:
        if set(kept_audio) != set(all_audio_ids):
            cmd += ["--audio-tracks", ",".join(kept_audio)]
    else:
        cmd += ["--no-audio"]

    if wipe_all or not kept_sub:
        cmd += ["--no-subtitles"]
    elif set(kept_sub) != set(all_sub_ids):
        cmd += ["--subtitle-tracks", ",".join(kept_sub)]

    # Forced flags
    for t in tracks:
        if t.type == "subtitles" and not t.removed:
            if wipe_forced:
                cmd += ["--forced-track", f"{t.tid}:no"]
            else:
                val = "yes" if t.forced else "no"
                cmd += ["--forced-track", f"{t.tid}:{val}"]

    # Default flags
    for t in tracks:
        if not t.removed and t.type in {"audio", "subtitles"}:
            if t.type == "audio":
                val = "yes" if t.default_audio else "no"
            else:
                val = "yes" if t.default_subtitle else "no"
            cmd += ["--default-track", f"{t.tid}:{val}"]

    # Output and input file MUST come last
    cmd += ["-o", str(destination), str(source)]
    return cmd


def _build_cmd_ffmpeg(
    source: Path,
    destination: Path,
    tracks: List[Track],
    wipe_forced: bool,
    wipe_all: bool,
) -> list[str]:
    cmd: list[str] = [DEFAULTS["ffmpeg_cmd"], "-i", str(source), "-map", "0"]

    for t in tracks:
        if t.type in {"audio", "subtitles"}:
            if wipe_all and t.type == "subtitles":
                cmd += ["-map", f"-0:{t.tid}"]
            elif t.removed:
                cmd += ["-map", f"-0:{t.tid}"]

    audio_tracks = [t for t in tracks if t.type == "audio" and not t.removed]
    sub_tracks = [t for t in tracks if t.type == "subtitles" and not (wipe_all or t.removed)]

    for i, t in enumerate(audio_tracks):
        disp = "default" if t.default_audio else "0"
        cmd += [f"-disposition:a:{i}", disp]

    for i, t in enumerate(sub_tracks):
        disp_flags = []
        if not wipe_forced and t.forced:
            disp_flags.append("forced")
        if t.default_subtitle:
            disp_flags.append("default")
        disp = "+".join(disp_flags) if disp_flags else "0"
        cmd += [f"-disposition:s:{i}", disp]

    cmd += ["-c", "copy", str(destination)]
    return cmd

def peek_sub(sub_file: Path, max_blocks: int = 5) -> str:
    """Return up to ``max_blocks`` blocks from the subtitle file ``sub_file``."""
    text = sub_file.read_text(encoding="utf-8", errors="ignore")
    blocks = text.strip().split("\n\n")
    if len(blocks) > max_blocks:
        return "\n\n".join(blocks[:max_blocks]) + "\n\n..."
    return text
