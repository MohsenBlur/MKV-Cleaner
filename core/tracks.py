"""Helpers for querying tracks and building processing commands."""

from __future__ import annotations
import json
import subprocess
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from core.config import AppConfig

logger = logging.getLogger("core.tracks")

@dataclass
class Track:
    """Represents a single media track and its attributes."""
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
    orig_forced: bool = False
    orig_default_audio: bool = False
    orig_default_subtitle: bool = False

    def signature(self) -> str:
        """Return a string uniquely identifying the track."""

        return (
            f"{self.idx}-{self.type}-{self.codec}-"
            f"{self.language}-{'F' if self.forced else ''}-{self.name}"
        )

class CommandNotFoundError(RuntimeError):
    """Raised when an external command is missing."""


def run_command(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    """Run an external command and return the completed process."""

    logger.debug("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if not capture:
            result.stdout = ""
        return result
    except FileNotFoundError as exc:
        msg = f"{cmd[0]} not found on PATH"
        logger.error(msg)
        raise CommandNotFoundError(msg) from exc
    except subprocess.CalledProcessError as exc:
        err_msg = exc.stderr or ""
        logger.error("Command failed: %s\n%s", exc, err_msg)
        raise

def query_tracks(source: Path, cfg: AppConfig) -> List[Track]:
    """Query tracks using the configured backend."""
    if cfg.backend == "ffmpeg":
        result = run_command([
            cfg.ffprobe_cmd,
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
            forced = bool(disp.get("forced", 0))
            def_flag = bool(disp.get("default", 0))
            tracks.append(
                Track(
                    idx=i,
                    tid=int(t.get("index", i)),
                    type="subtitles" if t.get("codec_type") == "subtitle" else t.get("codec_type", ""),
                    codec=t.get("codec_name", ""),
                    language=tags.get("language", "und"),
                    forced=forced,
                    name=tags.get("title", ""),
                    default_audio=def_flag if t.get("codec_type") == "audio" else False,
                    default_subtitle=def_flag if t.get("codec_type") == "subtitle" else False,
                    orig_forced=forced,
                    orig_default_audio=def_flag if t.get("codec_type") == "audio" else False,
                    orig_default_subtitle=def_flag if t.get("codec_type") == "subtitle" else False,
                )
            )
        return tracks
    else:
        result = run_command([cfg.mkvmerge_cmd, "-J", str(source)])
        data = json.loads(result.stdout)
        tracks: List[Track] = []
        for i, t in enumerate(data.get("tracks", [])):
            p = t.get("properties", {})
            forced = p.get("forced_track", False)
            def_flag = p.get("default_track", False)
            tracks.append(
                Track(
                    idx=i,
                    tid=int(t["id"]),
                    type=t.get("type", ""),
                    codec=p.get("codec_id", ""),
                    language=p.get("language", "und"),
                    forced=forced,
                    name=p.get("track_name", ""),
                    default_audio=def_flag if t.get("type") == "audio" else False,
                    default_subtitle=def_flag if t.get("type") == "subtitles" else False,
                    orig_forced=forced,
                    orig_default_audio=def_flag if t.get("type") == "audio" else False,
                    orig_default_subtitle=def_flag if t.get("type") == "subtitles" else False,
                )
            )
        return tracks

def build_cmd(
    source: Path,
    destination: Path,
    tracks: List[Track],
    cfg: AppConfig,
    wipe_forced: bool = False,
    wipe_all: bool = False,
) -> list[str]:
    """Build command for the configured backend."""
    if wipe_all:
        if not any(t.type == "subtitles" and t.removed for t in tracks):
            for t in tracks:
                if t.type == "subtitles":
                    t.removed = True

    if cfg.backend == "ffmpeg":
        return _build_cmd_ffmpeg(source, destination, tracks, cfg, wipe_forced)
    return _build_cmd_mkvmerge(source, destination, tracks, cfg, wipe_forced)


def _build_cmd_mkvmerge(
    source: Path,
    destination: Path,
    tracks: List[Track],
    cfg: AppConfig,
    wipe_forced: bool,
) -> list[str]:
    cmd: list[str] = [cfg.mkvmerge_cmd]

    # Use tid (real mkvmerge track id) everywhere!
    all_audio_ids = [str(t.tid) for t in tracks if t.type == "audio"]
    all_sub_ids   = [str(t.tid) for t in tracks if t.type == "subtitles"]
    kept_audio = [str(t.tid) for t in tracks if t.type == "audio" and not t.removed]
    kept_sub = [str(t.tid) for t in tracks if t.type == "subtitles" and not t.removed]

    if kept_audio:
        if set(kept_audio) != set(all_audio_ids):
            cmd += ["--audio-tracks", ",".join(kept_audio)]
    else:
        cmd += ["--no-audio"]

    if not kept_sub:
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
    cfg: AppConfig,
    wipe_forced: bool,
) -> list[str]:
    cmd: list[str] = [
        cfg.ffmpeg_cmd,
        # Overwrite existing output without asking
        "-y",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-map",
        "0",
    ]

    for t in tracks:
        if t.type == "subtitles" and t.removed:
            cmd += ["-map", f"-0:{t.tid}"]
        elif t.type == "audio" and t.removed:
            cmd += ["-map", f"-0:{t.tid}"]

    a_idx = 0
    s_idx = 0

    for t in tracks:
        if t.type == "audio" and not t.removed:
            disp = "default" if t.default_audio else "0"
            cmd += [f"-disposition:a:{a_idx}", disp]
            a_idx += 1
        elif t.type == "subtitles" and not t.removed:
            disp_flags = []
            if not wipe_forced and t.forced:
                disp_flags.append("forced")
            if t.default_subtitle:
                disp_flags.append("default")
            disp = "+".join(disp_flags) if disp_flags else "0"
            cmd += [f"-disposition:s:{s_idx}", disp]
            s_idx += 1

    cmd += ["-c", "copy", str(destination)]
    return cmd

def peek_sub(sub_file: Path, max_blocks: int = 5) -> str:
    """Return up to ``max_blocks`` blocks from the subtitle file ``sub_file``."""
    text = sub_file.read_text(encoding="utf-8", errors="ignore")
    blocks = text.strip().split("\n\n")
    if len(blocks) > max_blocks:
        return "\n\n".join(blocks[:max_blocks]) + "\n\n..."
    return text
