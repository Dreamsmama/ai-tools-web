"""
职业观察局 MP4 导出：统一音频采样率/编码/混音，避免 AAC 杂音与爆音。
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

AUDIO_SAMPLE_RATE = 44100
AUDIO_CHANNELS = 2
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
BGM_VOLUME_MAX = 0.3
BGM_VOLUME_DEFAULT = 0.15
BGM_FADE_OUT_SEC = 3.0


def probe_audio_info(ffprobe: str, media_path: Path) -> Dict[str, Any]:
    """读取音轨 codec / sample_rate / channels / bit_rate。"""
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "quiet",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate",
            "-of",
            "json",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    info: Dict[str, Any] = {
        "codec": None,
        "sample_rate": None,
        "channels": None,
        "bit_rate": None,
    }
    if proc.returncode != 0:
        return info
    try:
        data = json.loads(proc.stdout or "{}")
        streams = data.get("streams") or []
        if streams:
            s = streams[0]
            info["codec"] = s.get("codec_name")
            info["sample_rate"] = s.get("sample_rate")
            info["channels"] = s.get("channels")
            info["bit_rate"] = s.get("bit_rate")
    except (json.JSONDecodeError, TypeError, IndexError):
        pass
    return info


def log_audio_info(label: str, ffprobe: str, path: Path) -> None:
    if not path.is_file():
        logger.info("[render][audio] %s path=%s (missing)", label, path.name)
        return
    info = probe_audio_info(ffprobe, path)
    if info.get("codec"):
        logger.info(
            "[render][audio] %s codec=%s sample_rate=%s channels=%s bitrate=%s file=%s",
            label,
            info.get("codec"),
            info.get("sample_rate"),
            info.get("channels"),
            info.get("bit_rate"),
            path.name,
        )
    else:
        logger.info("[render][audio] %s no audio stream file=%s", label, path.name)


def normalize_audio_file(ffmpeg: str, src: Path, dest: Path) -> Path:
    """
    将任意音频统一为 44100Hz 立体声 AAC 192k（BGM 预处理）。
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    out = dest if dest.suffix.lower() in (".m4a", ".aac") else dest.with_suffix(".m4a")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-ar",
            str(AUDIO_SAMPLE_RATE),
            "-ac",
            str(AUDIO_CHANNELS),
            "-c:a",
            AUDIO_CODEC,
            "-b:a",
            AUDIO_BITRATE,
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def ensure_normalized_bgm(
    ffmpeg: str,
    bgm_path: Path,
    cache_dir: Path,
) -> Path:
    """BGM 导入后先转码，避免采样率不一致导致杂音。"""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"bgm_norm_{bgm_path.stem}_{bgm_path.stat().st_mtime_ns}.m4a"
    if cached.is_file():
        return cached
    return normalize_audio_file(ffmpeg, bgm_path, cached)


def _clamp_bgm_volume(volume: float) -> float:
    return max(0.05, min(BGM_VOLUME_MAX, float(volume)))


def build_bgm_mix_filter(
    duration: float,
    *,
    volume: float = BGM_VOLUME_DEFAULT,
    fade_out_sec: float = BGM_FADE_OUT_SEC,
    video_has_audio: bool = False,
) -> str:
    """
    混音滤镜：静音底轨 + 循环 BGM（低音量 amix），禁止 loudnorm 与过高 volume。
    """
    vol = _clamp_bgm_volume(volume)
    fade = max(1.0, min(fade_out_sec, duration * 0.4))
    fade_start = max(0.0, duration - fade)
    dur = f"{duration:.3f}"

    bgm_chain = (
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{dur},asetpts=PTS-STARTPTS,"
        f"aresample={AUDIO_SAMPLE_RATE},"
        f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"volume={vol},"
        f"afade=t=out:st={fade_start:.3f}:d={fade:.3f}[bgm]"
    )

    if video_has_audio:
        base = (
            f"[0:a]aresample={AUDIO_SAMPLE_RATE},"
            f"aformat=sample_fmts=fltp:channel_layouts=stereo[base]"
        )
        return (
            f"{base};{bgm_chain};"
            f"[base][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
        )

    silence = (
        f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_SAMPLE_RATE},"
        f"atrim=0:{dur}[base]"
    )
    return (
        f"{silence};{bgm_chain};"
        f"[base][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
    )


def ffmpeg_output_audio_flags() -> list[str]:
    return [
        "-c:a",
        AUDIO_CODEC,
        "-ar",
        str(AUDIO_SAMPLE_RATE),
        "-ac",
        str(AUDIO_CHANNELS),
        "-b:a",
        AUDIO_BITRATE,
    ]


def ffmpeg_output_video_flags() -> list[str]:
    return [
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
    ]


def build_voiceover_bgm_mix_filter(
    duration: float,
    *,
    volume: float = BGM_VOLUME_DEFAULT,
    fade_out_sec: float = BGM_FADE_OUT_SEC,
) -> str:
    """
    3-track amix（带配音）：
      input 0: 视频画面（-map 0:v 单独处理，此处不参与音频链）
      input 1: voiceover.mp3 → volume=1.0（人声）
      input 2: bgm.mp3 → 低音量 + 循环 + 淡出

    filter_complex 输出 [aout]，供 -map [aout] 使用。
    """
    vol = _clamp_bgm_volume(volume)
    fade = max(1.0, min(fade_out_sec, duration * 0.4))
    fade_start = max(0.0, duration - fade)
    dur = f"{duration:.3f}"

    voice_chain = (
        f"[1:a]aresample={AUDIO_SAMPLE_RATE},"
        f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"volume=1.0[voice]"
    )
    bgm_chain = (
        f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{dur},asetpts=PTS-STARTPTS,"
        f"aresample={AUDIO_SAMPLE_RATE},"
        f"aformat=sample_fmts=fltp:channel_layouts=stereo,"
        f"volume={vol},"
        f"afade=t=out:st={fade_start:.3f}:d={fade:.3f}[bgm]"
    )
    return (
        f"{voice_chain};{bgm_chain};"
        f"[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[aout]"
    )


def build_silent_audio_filter(duration: float) -> str:
    dur = f"{duration:.3f}"
    return (
        f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_SAMPLE_RATE},"
        f"atrim=0:{dur}[aout]"
    )
