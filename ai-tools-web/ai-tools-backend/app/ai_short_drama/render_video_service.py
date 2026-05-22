from __future__ import annotations

import logging
import math
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_short_drama.audio_export import (
    AUDIO_SAMPLE_RATE,
    BGM_FADE_OUT_SEC,
    BGM_VOLUME_DEFAULT,
    build_bgm_mix_filter,
    build_silent_audio_filter,
    build_voiceover_bgm_mix_filter,
    ensure_normalized_bgm,
    ffmpeg_output_audio_flags,
    ffmpeg_output_video_flags,
    log_audio_info,
)
from app.ai_short_drama.bgm import pick_bgm_filename, pick_bgm_path
from app.ai_short_drama.material_media import (
    SVG_VIDEO_ERROR_MSG,
    is_svg,
    validate_image_path_for_video,
)
from app.ai_short_drama.material_paths import url_to_disk_path
from app.ai_short_drama.materials import DEFAULT_MATERIAL_URL
from app.ai_short_drama.schemas import (
    RenderVideoData,
    RenderVideoEnvelope,
    RenderVideoRequest,
    RenderVideoShotInput,
)
from app.ai_short_drama.vertical_image import (
    TARGET_HEIGHT,
    TARGET_WIDTH,
    ffmpeg_vertical_fit_filter,
)
from app.ai_short_drama.speech_timing import (
    TTS_DURATION_MAX_RATIO,
    estimate_speech_seconds,
    is_plausible_tts_duration,
)
from app.ai_short_drama.subtitle_style import (
    build_drawtext_filter,
    phrase_duration_seconds,
    pick_bold_font,
    split_subtitle_phrases,
    wrap_subtitle_lines,
)

logger = logging.getLogger(__name__)

# 配音轨尾部留白，避免切在字末音上
TTS_TAIL_PAD_SEC = 0.4
# 无配音时节奏引擎单镜上限；有配音时按朗读时长拉长（避免 15s 截画面不截音频导致段错位）
RHYTHM_MAX_SEGMENT_SEC = 15
TTS_MAX_SEGMENT_SEC = 60

FFMPEG_MISSING_MSG = "当前环境未安装 FFmpeg，无法生成视频"


def _effective_voice_seconds(
    ffmpeg: str,
    text: str,
    audio_path: Path,
    *,
    planned: float,
) -> float:
    """取 TTS 实际时长与文案估算的合理值，过滤异常超长配音。"""
    try:
        probed = probe_duration_seconds(ffmpeg, audio_path)
    except Exception:
        return max(planned, estimate_speech_seconds(text))

    if is_plausible_tts_duration(text, probed, ratio=TTS_DURATION_MAX_RATIO):
        return probed

    est = estimate_speech_seconds(text)
    cap = max(planned, est * TTS_DURATION_MAX_RATIO)
    logger.warning(
        "[render][tts] 配音时长异常 text_len=%d est=%.1fs probed=%.1fs cap=%.1fs preview=%r",
        len(re.sub(r"\s+", "", (text or "").strip())),
        est,
        probed,
        cap,
        (text or "").strip()[:40],
    )
    return cap


def _trim_voice_clip(ffmpeg: str, src: Path, max_sec: float, work_dir: Path, tag: str) -> Path:
    """将异常超长 TTS 裁到可用时长，避免第一段画面被拖住数十秒。"""
    out = work_dir / f"voice_trim_{tag}.mp3"
    dur = max(0.8, float(max_sec))
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-t",
            f"{dur:.3f}",
            "-c:a",
            "libmp3lame",
            "-q:a",
            "2",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out

# Homebrew 默认 ffmpeg 不含 drawtext；ffmpeg-full 才支持字幕烧录
FFMPEG_CANDIDATES = [
    "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
    "/usr/local/opt/ffmpeg-full/bin/ffmpeg",
]

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_PUBLIC = BACKEND_ROOT.parent / "ai-tools-frontend" / "public"
GENERATED_DIR = BACKEND_ROOT / "generated" / "short-drama"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

class FFmpegNotInstalledError(RuntimeError):
    pass


class VideoRenderError(RuntimeError):
    pass


def ensure_ffmpeg() -> str:
    for path in FFMPEG_CANDIDATES:
        if Path(path).is_file():
            return path
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise FFmpegNotInstalledError(FFMPEG_MISSING_MSG)
    return ffmpeg


_drawtext_cache: dict[str, bool] = {}


def has_drawtext_filter(ffmpeg: str) -> bool:
    """检测 FFmpeg 是否支持 drawtext（需 libfreetype；brew 默认 ffmpeg 不含）。"""
    if ffmpeg in _drawtext_cache:
        return _drawtext_cache[ffmpeg]
    try:
        proc = subprocess.run(
            [ffmpeg, "-h", "filter=drawtext"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        out = ((proc.stdout or "") + (proc.stderr or "")).lower()
        ok = proc.returncode == 0 and "unknown filter" not in out and "drawtext" in out
    except Exception:
        ok = False
    _drawtext_cache[ffmpeg] = ok
    if not ok:
        logger.warning(
            "FFmpeg(%s) 不支持 drawtext，视频将不含烧录字幕。"
            "请安装: brew install ffmpeg-full",
            ffmpeg,
        )
    return ok


def _default_png_path() -> Path:
    png = FRONTEND_PUBLIC / "short-drama" / "placeholders" / "default-office.png"
    if not png.is_file():
        png = FRONTEND_PUBLIC / "short-drama" / "default.png"
    if png.is_file():
        return png
    return _fallback_color_image()


def resolve_image_path(image_url: Optional[str]) -> Path:
    default = _default_png_path()
    if not image_url or not str(image_url).strip():
        return default

    raw = str(image_url).strip()
    if is_svg(raw):
        raise VideoRenderError(SVG_VIDEO_ERROR_MSG)

    if raw.startswith("http://") or raw.startswith("https://"):
        return default

    # 上传素材（含分层目录与旧版扁平路径）
    upload_path = url_to_disk_path(raw)
    if upload_path:
        return upload_path

    rel = raw.lstrip("/")
    if rel.startswith("assets/short-drama/"):
        rel = rel[len("assets/") :]

    candidates = [
        BACKEND_ROOT / rel,
        FRONTEND_PUBLIC / rel,
        FRONTEND_PUBLIC / "short-drama" / Path(rel).name,
    ]
    if rel.startswith("uploads/"):
        candidates.insert(0, BACKEND_ROOT / rel)
    for path in candidates:
        if path.is_file():
            if path.suffix.lower() == ".svg":
                raise VideoRenderError(SVG_VIDEO_ERROR_MSG)
            return path

    # 按素材库默认路径再试
    if DEFAULT_MATERIAL_URL.startswith("/"):
        fallback = FRONTEND_PUBLIC / DEFAULT_MATERIAL_URL.lstrip("/")
        if fallback.is_file():
            if fallback.suffix.lower() == ".svg":
                raise VideoRenderError(SVG_VIDEO_ERROR_MSG)
            return fallback

    return default


def _fallback_color_image() -> Path:
    """无素材文件时生成纯色占位图。"""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    out = GENERATED_DIR / "_fallback.png"
    if out.is_file():
        return out
    ffmpeg = ensure_ffmpeg()
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x1e1b4b:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:d=1",
            "-frames:v",
            "1",
            str(out),
        ],
        check=True,
        capture_output=True,
    )
    return out


def rasterize_image(src: Path, dest: Path) -> Path:
    """
    竖屏成片适配：模糊背景铺满 + 前景等比居中。
    不使用 rotate/transpose，不改变图片方向。
    """
    if src.suffix.lower() == ".svg":
        raise VideoRenderError(SVG_VIDEO_ERROR_MSG)
    ffmpeg = ensure_ffmpeg()
    vf = ffmpeg_vertical_fit_filter(width=TARGET_WIDTH, height=TARGET_HEIGHT)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(src),
            "-vf",
            vf,
            "-frames:v",
            "1",
            str(dest),
        ],
        check=True,
        capture_output=True,
    )
    return dest


def _write_subtitle_file(work_dir: Path, shot_no: int, subtitle: str) -> Path:
    text_path = work_dir / f"subtitle_{shot_no}.txt"
    text_path.write_text(wrap_subtitle_lines(subtitle), encoding="utf-8")
    return text_path


def _align_shots_with_voiceover(
    ffmpeg: str,
    shots: List[RenderVideoShotInput],
    voiceover_paths: List[Optional[Path]],
) -> List[RenderVideoShotInput]:
    """
    用 TTS 实际时长校正每段 duration，避免节奏引擎固定 2~5s 与朗读速度不一致。
    """
    aligned: List[RenderVideoShotInput] = []
    for shot, vp in zip(shots, voiceover_paths):
        planned = float(shot.duration)
        dur = planned
        if vp and vp.is_file():
            try:
                audio_len = _effective_voice_seconds(
                    ffmpeg,
                    shot.subtitle or "",
                    vp,
                    planned=planned,
                )
                dur = max(planned, audio_len + TTS_TAIL_PAD_SEC)
                if dur > planned + 0.05:
                    logger.info(
                        "[render][tts] seg=%s duration %.1fs → %.1fs (voice=%.2fs)",
                        shot.shotNo,
                        planned,
                        dur,
                        audio_len,
                    )
            except Exception as err:
                logger.warning("[render][tts] probe audio seg=%s failed: %s", shot.shotNo, err)
        raw_dur = dur
        dur_int = max(2, min(TTS_MAX_SEGMENT_SEC, int(math.ceil(dur))))
        if raw_dur > TTS_MAX_SEGMENT_SEC + 0.05:
            logger.warning(
                "[render][tts] seg=%s 朗读过长 %.1fs，画面与配音将截断至 %ds",
                shot.shotNo,
                raw_dur,
                dur_int,
            )
        aligned.append(
            RenderVideoShotInput(
                shotNo=shot.shotNo,
                duration=dur_int,
                subtitle=shot.subtitle,
                imageUrl=shot.imageUrl,
            )
        )
    return aligned


def _expand_shots_for_phrase_subtitles(
    shots: List[RenderVideoShotInput],
) -> List[RenderVideoShotInput]:
    """同一张图下，多句文案逐句显示（每句 2~4 秒）。有配音时不使用，避免字幕句与整段配音错位。"""
    expanded: List[RenderVideoShotInput] = []
    for shot in shots:
        phrases = split_subtitle_phrases(shot.subtitle or "")
        if len(phrases) <= 1:
            expanded.append(shot)
            continue
        per_dur = phrase_duration_seconds(len(phrases), shot.duration)
        for idx, phrase in enumerate(phrases):
            expanded.append(
                RenderVideoShotInput(
                    shotNo=shot.shotNo * 1000 + idx,
                    duration=per_dur,
                    subtitle=phrase,
                    imageUrl=shot.imageUrl,
                )
            )
    return expanded


def render_shot_segment(
    ffmpeg: str,
    image_png: Path,
    duration: int,
    subtitle: str,
    segment_path: Path,
    work_dir: Path,
    shot_no: int,
    *,
    burn_subtitle: bool = True,
    max_segment_sec: int = RHYTHM_MAX_SEGMENT_SEC,
) -> None:
    cap = max(2, int(max_segment_sec))
    dur = max(2, min(cap, int(duration)))

    # 竖屏适配已在 rasterize_image 完成；此处仅烧录字幕，不再 rotate/crop
    vf_parts: List[str] = []

    if burn_subtitle and has_drawtext_filter(ffmpeg):
        text_file = _write_subtitle_file(work_dir, shot_no, subtitle)
        font_path, font_index = pick_bold_font()
        if font_path:
            vf_parts.append(
                build_drawtext_filter(text_file, font_path=font_path, font_index=font_index)
            )
        else:
            logger.warning("[render] no bold font found, skip subtitle burn for shot %s", shot_no)

    cmd = [
        ffmpeg,
        "-y",
        "-loop",
        "1",
        "-i",
        str(image_png),
        "-t",
        str(dur),
    ]
    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])
    cmd.extend(
        [
            "-r",
            str(FPS),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(segment_path),
        ]
    )

    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration_seconds(ffmpeg: str, media_path: Path) -> float:
    ffprobe = shutil.which("ffprobe") or ffmpeg.replace("ffmpeg", "ffprobe")
    if not Path(ffprobe).is_file() and ffprobe == ffmpeg.replace("ffmpeg", "ffprobe"):
        ffprobe = "ffprobe"
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if proc.returncode != 0:
        raise VideoRenderError("无法读取视频时长")
    try:
        return max(1.0, float((proc.stdout or "").strip()))
    except ValueError as err:
        raise VideoRenderError("无法解析视频时长") from err


def has_audio_stream(ffmpeg: str, media_path: Path) -> bool:
    ffprobe = shutil.which("ffprobe") or ffmpeg.replace("ffmpeg", "ffprobe")
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "csv=p=0",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    return proc.returncode == 0 and "audio" in (proc.stdout or "")


def _decode_stderr(err: subprocess.CalledProcessError) -> str:
    raw = err.stderr or b""
    try:
        return raw.decode("utf-8", errors="ignore")[-800:]
    except Exception:
        return str(raw)[-800:]


def _ffprobe_path(ffmpeg: str) -> str:
    ffprobe = shutil.which("ffprobe") or ffmpeg.replace("ffmpeg", "ffprobe")
    if not Path(ffprobe).is_file() and ffprobe == ffmpeg.replace("ffmpeg", "ffprobe"):
        return "ffprobe"
    return ffprobe


def attach_silent_audio_track(
    ffmpeg: str,
    video_path: Path,
    output_path: Path,
) -> None:
    """无声成片附加静音 AAC 轨，避免播放器/平台对无音轨 MP4 的异常处理。"""
    duration = probe_duration_seconds(ffmpeg, video_path)
    filter_a = build_silent_audio_filter(duration)
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-filter_complex",
            filter_a,
            "-map",
            "0:v",
            "-map",
            "[aout]",
            *ffmpeg_output_video_flags(),
            *ffmpeg_output_audio_flags(),
            "-movflags",
            "+faststart",
            "-t",
            f"{duration:.3f}",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )


def mix_bgm_into_video(
    ffmpeg: str,
    video_path: Path,
    bgm_path: Path,
    output_path: Path,
    work_dir: Path,
    *,
    volume: float = BGM_VOLUME_DEFAULT,
    fade_out_sec: float = BGM_FADE_OUT_SEC,
) -> None:
    """BGM 预转码 44.1k AAC + anullsrc/amix 低音量混音，统一导出编码参数。"""
    ffprobe = _ffprobe_path(ffmpeg)
    duration = probe_duration_seconds(ffmpeg, video_path)
    video_has_audio = has_audio_stream(ffmpeg, video_path)

    log_audio_info("bgm_source", ffprobe, bgm_path)
    normalized_bgm = ensure_normalized_bgm(ffmpeg, bgm_path, work_dir / "bgm_cache")
    log_audio_info("bgm_normalized", ffprobe, normalized_bgm)

    filter_a = build_bgm_mix_filter(
        duration,
        volume=volume,
        fade_out_sec=fade_out_sec,
        video_has_audio=video_has_audio,
    )
    logger.info(
        "[render][audio] mix duration=%.2fs bgm_volume<=%.2f video_has_audio=%s",
        duration,
        min(0.3, max(0.05, float(volume))),
        video_has_audio,
    )

    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(normalized_bgm),
            "-filter_complex",
            filter_a,
            "-map",
            "0:v",
            "-map",
            "[aout]",
            *ffmpeg_output_video_flags(),
            *ffmpeg_output_audio_flags(),
            "-movflags",
            "+faststart",
            "-t",
            f"{duration:.3f}",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )
    if not output_path.is_file() or not has_audio_stream(ffmpeg, output_path):
        raise VideoRenderError("BGM 混入失败：输出无音轨")
    log_audio_info("export_output", ffprobe, output_path)


def build_voiceover_track(
    ffmpeg: str,
    audio_paths: List[Optional[Path]],
    durations: List[float],
    work_dir: Path,
) -> Optional[Path]:
    """
    将各 shot 的 TTS 音频（或静音）按 duration 对齐后 concat，输出 voiceover_track.mp3。
    所有 audio_paths 均为 None 时返回 None（无配音）。
    """
    if not any(p and p.is_file() for p in audio_paths):
        return None

    padded: List[Path] = []
    for idx, (ap, dur) in enumerate(zip(audio_paths, durations)):
        dur_str = f"{max(0.5, float(dur)):.3f}"
        seg_wav = work_dir / f"vpad_{idx:03d}.wav"
        if ap and ap.is_file():
            src = ap
            try:
                probed = probe_duration_seconds(ffmpeg, ap)
                slot = float(dur)
                if probed > slot + 0.35:
                    src = _trim_voice_clip(ffmpeg, ap, slot, work_dir, f"{idx:03d}")
            except Exception as err:
                logger.warning("[render][tts] trim voice idx=%s failed: %s", idx, err)
            # apad 补齐短句；atrim 裁齐，保证每段音轨秒数与画面一致
            subprocess.run(
                [
                    ffmpeg, "-y", "-i", str(src),
                    "-af", f"apad=whole_dur={dur_str},atrim=0:{dur_str}",
                    "-ar", str(AUDIO_SAMPLE_RATE), "-ac", "2",
                    "-f", "wav", str(seg_wav),
                ],
                check=True, capture_output=True,
            )
        else:
            subprocess.run(
                [
                    ffmpeg, "-y",
                    "-f", "lavfi",
                    "-i", f"anullsrc=channel_layout=stereo:sample_rate={AUDIO_SAMPLE_RATE}",
                    "-t", dur_str,
                    "-f", "wav", str(seg_wav),
                ],
                check=True, capture_output=True,
            )
        padded.append(seg_wav)

    list_file = work_dir / "voice_concat_list.txt"
    list_file.write_text("\n".join(f"file '{p.resolve()}'" for p in padded), encoding="utf-8")
    out_path = work_dir / "voiceover_track.mp3"
    subprocess.run(
        [
            ffmpeg, "-y",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-ar", str(AUDIO_SAMPLE_RATE), "-ac", "2",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out_path),
        ],
        check=True, capture_output=True,
    )
    logger.info("[render][tts] voiceover_track built: %s", out_path.name)
    return out_path


def mix_voiceover_bgm_into_video(
    ffmpeg: str,
    video_path: Path,
    voiceover_path: Path,
    bgm_path: Optional[Path],
    output_path: Path,
    work_dir: Path,
    *,
    volume: float = BGM_VOLUME_DEFAULT,
    fade_out_sec: float = BGM_FADE_OUT_SEC,
) -> None:
    """将配音轨 + BGM 混入 silent.mp4，输出带音频的最终视频。"""
    ffprobe = _ffprobe_path(ffmpeg)
    duration = probe_duration_seconds(ffmpeg, video_path)

    if bgm_path and bgm_path.is_file():
        log_audio_info("bgm_source", ffprobe, bgm_path)
        normalized_bgm = ensure_normalized_bgm(ffmpeg, bgm_path, work_dir / "bgm_cache")
        filter_a = build_voiceover_bgm_mix_filter(duration, volume=volume, fade_out_sec=fade_out_sec)
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path),
            "-i", str(voiceover_path),
            "-i", str(normalized_bgm),
            "-filter_complex", filter_a,
            "-map", "0:v", "-map", "[aout]",
            *ffmpeg_output_video_flags(),
            *ffmpeg_output_audio_flags(),
            "-movflags", "+faststart",
            "-t", f"{duration:.3f}",
            str(output_path),
        ]
    else:
        cmd = [
            ffmpeg, "-y",
            "-i", str(video_path),
            "-i", str(voiceover_path),
            "-map", "0:v", "-map", "1:a",
            "-c:v", "copy",
            *ffmpeg_output_audio_flags(),
            "-movflags", "+faststart",
            "-t", f"{duration:.3f}",
            str(output_path),
        ]

    subprocess.run(cmd, check=True, capture_output=True)
    if not output_path.is_file():
        raise VideoRenderError("配音混入失败：输出文件不存在")
    log_audio_info("voiceover_output", ffprobe, output_path)


def concat_segments(ffmpeg: str, segments: List[Path], output_path: Path) -> None:
    list_file = output_path.parent / "concat_list.txt"
    lines = [f"file '{seg.resolve()}'" for seg in segments]
    list_file.write_text("\n".join(lines), encoding="utf-8")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(output_path),
        ],
        check=True,
        capture_output=True,
    )


def _resolve_render_shots(body: RenderVideoRequest) -> List[RenderVideoShotInput]:
    """优先 segments（图文成片），兼容旧 shots 字段。"""
    if body.segments:
        return [
            RenderVideoShotInput(
                shotNo=s.segmentNo,
                duration=s.duration,
                subtitle=s.text,
                imageUrl=s.imageUrl,
            )
            for s in sorted(body.segments, key=lambda x: x.segmentNo)
        ]
    return sorted(body.shots, key=lambda s: s.shotNo)


def _segments_for_bgm(body: RenderVideoRequest) -> List[Dict[str, Any]]:
    if body.segments:
        return [{"emotion": s.emotion or ""} for s in body.segments]
    return []


def render_short_drama_video(
    body: RenderVideoRequest,
    voiceover_paths: Optional[List[Optional[Path]]] = None,
) -> RenderVideoEnvelope:
    base_shots = _resolve_render_shots(body)
    if not base_shots:
        return RenderVideoEnvelope(code=400, message="图文段落为空，无法生成视频")

    try:
        ffmpeg = ensure_ffmpeg()
        can_burn_subs = has_drawtext_filter(ffmpeg)
    except FFmpegNotInstalledError as err:
        return RenderVideoEnvelope(code=503, message=str(err))

    if voiceover_paths:
        base_shots = _align_shots_with_voiceover(ffmpeg, base_shots, voiceover_paths)
        render_shots = base_shots
        logger.info("[render][tts] 已按配音时长对齐段落，关闭逐句拆字幕")
    else:
        render_shots = _expand_shots_for_phrase_subtitles(base_shots)

    if not render_shots:
        return RenderVideoEnvelope(code=400, message="图文段落为空，无法生成视频")

    bgm_mode = (body.bgm_mode or "auto").strip().lower()
    segment_meta = _segments_for_bgm(body)
    selected_bgm_name = pick_bgm_filename(
        bgm_mode=bgm_mode,
        bgm_file=body.bgm_file,
        emotion_style=body.emotion_style,
        segments=segment_meta,
    )
    bgm_path = pick_bgm_path(
        bgm_mode=bgm_mode,
        bgm_file=body.bgm_file,
        emotion_style=body.emotion_style,
        segments=segment_meta,
    )

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    job_id = uuid.uuid4().hex[:12]
    work_dir = GENERATED_DIR / f"job_{job_id}"
    work_dir.mkdir(parents=True, exist_ok=True)
    silent_path = GENERATED_DIR / f"{job_id}_silent.mp4"
    output_path = GENERATED_DIR / f"{job_id}.mp4"

    segment_paths: List[Path] = []
    max_seg_sec = TTS_MAX_SEGMENT_SEC if voiceover_paths else RHYTHM_MAX_SEGMENT_SEC

    try:
        for shot in render_shots:
            if shot.imageUrl and is_svg(str(shot.imageUrl)):
                return RenderVideoEnvelope(code=400, message=SVG_VIDEO_ERROR_MSG)

            src = resolve_image_path(shot.imageUrl)
            media_err = validate_image_path_for_video(src)
            if media_err:
                return RenderVideoEnvelope(code=400, message=media_err)

            png_path = work_dir / f"shot_{shot.shotNo:02d}.png"
            rasterize_image(src, png_path)
            seg_path = work_dir / f"seg_{shot.shotNo:02d}.mp4"
            render_shot_segment(
                ffmpeg,
                png_path,
                shot.duration,
                shot.subtitle,
                seg_path,
                work_dir,
                shot.shotNo,
                burn_subtitle=can_burn_subs,
                max_segment_sec=max_seg_sec,
            )
            segment_paths.append(seg_path)

        if not segment_paths:
            raise VideoRenderError("未生成任何图文片段")

        concat_segments(ffmpeg, segment_paths, silent_path)
        if not silent_path.is_file():
            raise VideoRenderError("视频文件未生成")

        final_path = silent_path
        bgm_note = ""
        ffprobe = _ffprobe_path(ffmpeg)
        log_audio_info("concat_silent", ffprobe, silent_path)

        # 配音轨：如果提供了 TTS 音频路径，先 concat+pad 成整轨
        voiceover_track: Optional[Path] = None
        if voiceover_paths:
            durations = [float(s.duration) for s in render_shots]
            try:
                voiceover_track = build_voiceover_track(ffmpeg, voiceover_paths, durations, work_dir)
            except subprocess.CalledProcessError as err:
                logger.warning("[render] voiceover track build failed: %s", _decode_stderr(err))

        if voiceover_track and voiceover_track.is_file():
            bgm_for_voice = bgm_path if (bgm_mode != "none" and bgm_path and bgm_path.is_file()) else None
            try:
                mix_voiceover_bgm_into_video(
                    ffmpeg, silent_path, voiceover_track, bgm_for_voice, output_path, work_dir,
                )
                if output_path.is_file() and has_audio_stream(ffmpeg, output_path):
                    final_path = output_path
                    bgm_note = " 已混入配音"
                    if bgm_for_voice:
                        bgm_note += f" + BGM：{selected_bgm_name or bgm_for_voice.name}"
                else:
                    logger.warning("[render] voiceover mix produced no audio, falling back to BGM-only")
                    voiceover_track = None
            except (subprocess.CalledProcessError, VideoRenderError) as err:
                stderr = _decode_stderr(err) if isinstance(err, subprocess.CalledProcessError) else str(err)
                logger.error("[render] voiceover mix failed: %s", stderr)
                voiceover_track = None

        if not voiceover_track:
            if bgm_mode != "none" and bgm_path and bgm_path.is_file():
                logger.info(
                    "[render] mixing BGM file=%s into silent=%s",
                    bgm_path.name,
                    silent_path.name,
                )
                mixed_ok = False
                try:
                    mix_bgm_into_video(
                        ffmpeg,
                        silent_path,
                        bgm_path,
                        output_path,
                        work_dir,
                    )
                    mixed_ok = output_path.is_file() and has_audio_stream(ffmpeg, output_path)
                except (subprocess.CalledProcessError, VideoRenderError) as err:
                    stderr = _decode_stderr(err) if isinstance(err, subprocess.CalledProcessError) else str(err)
                    logger.error("[render] BGM mix failed: %s", stderr)

                if mixed_ok:
                    final_path = output_path
                    bgm_note = f" 已混入 BGM：{selected_bgm_name or bgm_path.name}"
                else:
                    return RenderVideoEnvelope(
                        code=500,
                        message=(
                            "视频画面已生成，但 BGM 混入失败（成片无声音）。"
                            f"请确认 {bgm_path.parent} 下存在 mp3，并查看后端日志。"
                        ),
                        data=RenderVideoData(
                            videoUrl=f"/generated/short-drama/{silent_path.name}",
                            bgmFile=selected_bgm_name,
                            bgmMode=bgm_mode,
                        ),
                    )
            elif bgm_mode == "none" and not has_audio_stream(ffmpeg, silent_path):
                try:
                    attach_silent_audio_track(ffmpeg, silent_path, output_path)
                    if output_path.is_file():
                        final_path = output_path
                        log_audio_info("export_silent_audio", ffprobe, output_path)
                except subprocess.CalledProcessError as err:
                    logger.warning(
                        "[render] attach silent audio failed, keep video-only: %s",
                        _decode_stderr(err),
                    )
            elif bgm_mode != "none" and not bgm_path:
                return RenderVideoEnvelope(
                    code=500,
                    message=(
                        "未找到 BGM 文件。请将 mp3 放入 "
                        "ai-tools-frontend/public/short-drama/bgm/ 后重试。"
                    ),
                    data=RenderVideoData(
                        videoUrl=f"/generated/short-drama/{silent_path.name}",
                        bgmMode=bgm_mode,
                    ),
                )

        voice_ok = voiceover_track is not None and voiceover_track.is_file()
        video_url = f"/generated/short-drama/{final_path.name}"
        data = RenderVideoData(
            videoUrl=video_url,
            bgmFile=selected_bgm_name,
            bgmMode=bgm_mode,
            voiceApplied=voice_ok,
        )
        extra = ""
        if voiceover_paths and not voice_ok:
            extra = " ⚠️ 配音生成失败（TTS 全部返回错误），已改为纯BGM。"
        if not can_burn_subs:
            return RenderVideoEnvelope(
                code=0,
                data=data,
                message="视频已生成（当前 FFmpeg 不支持字幕烧录，画面正常无字幕）。"
                " 可执行 brew reinstall ffmpeg 后重启后端以启用字幕。"
                + bgm_note + extra,
            )
        msg = ("视频已生成。" + bgm_note + extra).strip() or None
        return RenderVideoEnvelope(code=0, data=data, message=msg)
    except FFmpegNotInstalledError as err:
        return RenderVideoEnvelope(code=503, message=str(err))
    except VideoRenderError as err:
        return RenderVideoEnvelope(code=400, message=str(err))
    except subprocess.CalledProcessError as err:
        stderr = ""
        if err.stderr:
            try:
                stderr = err.stderr.decode("utf-8", errors="ignore")[-400:]
            except Exception:
                stderr = str(err.stderr)[-400:]
        logger.exception("ffmpeg render failed: %s", stderr)
        return RenderVideoEnvelope(
            code=500,
            message="视频合成失败，请检查素材图片或稍后重试。",
        )
    except Exception as err:
        logger.exception("render_short_drama_video error")
        return RenderVideoEnvelope(code=500, message=str(err) or "视频合成失败")
    finally:
        # 保留 png/seg 临时文件便于排查；仅清理 concat 列表
        list_file = work_dir / "concat_list.txt"
        if list_file.is_file():
            try:
                list_file.unlink()
            except OSError:
                pass
