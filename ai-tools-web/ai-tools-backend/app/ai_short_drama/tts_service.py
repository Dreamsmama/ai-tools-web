"""
DashScope CosyVoice TTS（非流式）：将短剧文案逐段合成 MP3 配音文件。

官方文档：https://help.aliyun.com/zh/model-studio/non-realtime-cosyvoice-api
逐段顺序合成 + 时长校验，避免并发时 CosyVoice 对短开口返回异常长音频。
"""
from __future__ import annotations

import asyncio
import logging
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.ai_short_drama.speech_timing import estimate_speech_seconds, is_plausible_tts_duration
from app.config.settings import settings

logger = logging.getLogger(__name__)

_TTS_URL = "https://dashscope.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"

# 顺序合成，降低 CosyVoice 并发时返回错音/超长缓存音频的概率
_SEGMENT_GAP_SEC = 0.35
_MAX_ATTEMPTS = 3

VOICE_OPTIONS: Dict[str, str] = {
    "female_warm": "longxiaochun_v2",
    "female_news": "longwan",
    "male_calm": "longhua",
    "male_young": "longshuo",
}


def _extract_audio_url(payload: Dict[str, Any]) -> str:
    output = payload.get("output") or {}
    audio = output.get("audio") or {}
    if isinstance(audio, dict):
        url = (audio.get("url") or "").strip()
        if url:
            return url
    return (output.get("audio_address") or "").strip()


def _extract_error_message(payload: Dict[str, Any], fallback: str) -> str:
    if payload.get("message"):
        return str(payload["message"])
    if payload.get("code"):
        return f"{payload['code']}"
    return fallback


def _probe_mp3_duration_seconds(path: Path) -> float:
    ffprobe = shutil.which("ffprobe") or "ffprobe"
    proc = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "ffprobe failed").strip())
    return max(0.0, float((proc.stdout or "").strip()))


def _tts_text_variants(text: str) -> List[str]:
    """短开口、冒号结尾等生成多种提交文案，用于异常音频时重试。"""
    t = (text or "").strip()
    if not t:
        return []
    variants: List[str] = []
    for cand in (
        t,
        re.sub(r"\s+", "，", t.replace("\n", "，")),
        re.sub(r"[：:]\s*$", "。", t),
        t.replace("：", "，").replace(":", ","),
    ):
        cand = cand.strip()
        if cand and cand not in variants:
            variants.append(cand)
    return variants[:_MAX_ATTEMPTS]


async def _download_tts_mp3(
    client: httpx.AsyncClient,
    *,
    text: str,
    voice: str,
    model: str,
    segment_no: int,
    work_dir: Path,
    attempt: int,
    rate: float,
) -> Optional[Path]:
    headers = {
        "Authorization": f"Bearer {settings.dashscope_api_key.strip()}",
        "Content-Type": "application/json",
    }
    body: Dict[str, Any] = {
        "model": model,
        "input": {
            "text": text,
            "voice": voice,
            "format": "mp3",
            "sample_rate": 22050,
            "rate": rate,
            "pitch": 1.0,
        },
    }

    resp = await client.post(_TTS_URL, json=body, headers=headers)
    try:
        payload = resp.json()
    except Exception:
        payload = {}

    if not resp.is_success:
        logger.warning(
            "[tts] seg=%s attempt=%s HTTP %s msg=%s text=%r",
            segment_no,
            attempt,
            resp.status_code,
            _extract_error_message(payload, resp.text[:400]),
            text[:40],
        )
        return None

    audio_url = _extract_audio_url(payload)
    if not audio_url:
        logger.warning(
            "[tts] seg=%s attempt=%s 无 audio.url body=%s",
            segment_no,
            attempt,
            str(payload)[:400],
        )
        return None

    audio_resp = await client.get(audio_url, follow_redirects=True)
    audio_resp.raise_for_status()
    if not audio_resp.content or len(audio_resp.content) < 256:
        logger.warning("[tts] seg=%s attempt=%s 音频过小", segment_no, attempt)
        return None

    work_dir.mkdir(parents=True, exist_ok=True)
    path = work_dir / f"voice_{segment_no:03d}.mp3"
    path.write_bytes(audio_resp.content)
    return path


async def synthesize_segment(
    text: str,
    voice_id: str,
    segment_no: int,
    work_dir: Path,
) -> Optional[Path]:
    """合成单段配音；时长异常时换文案重试，避免「很多人觉得：」类错音。"""
    if not (text or "").strip():
        return None
    if not settings.dashscope_api_key.strip():
        logger.warning("[tts] dashscope_api_key 未配置，跳过配音 seg=%s", segment_no)
        return None

    voice = (voice_id or settings.tts_voice_default).strip()
    model = settings.tts_model.strip() or "cosyvoice-v2"
    variants = _tts_text_variants(text)

    try:
        async with httpx.AsyncClient(timeout=settings.tts_timeout_seconds) as client:
            for attempt, variant in enumerate(variants, start=1):
                rate = 1.0 if attempt == 1 else 1.08
                path = await _download_tts_mp3(
                    client,
                    text=variant,
                    voice=voice,
                    model=model,
                    segment_no=segment_no,
                    work_dir=work_dir,
                    attempt=attempt,
                    rate=rate,
                )
                if not path or not path.is_file():
                    continue

                try:
                    probed = await asyncio.to_thread(_probe_mp3_duration_seconds, path)
                except Exception as err:
                    logger.warning("[tts] seg=%s probe failed: %s", segment_no, err)
                    probed = 0.0

                if is_plausible_tts_duration(variant, probed):
                    logger.info(
                        "[tts] seg=%s ok %.1fs %d bytes text=%r attempt=%s",
                        segment_no,
                        probed,
                        path.stat().st_size,
                        variant[:48],
                        attempt,
                    )
                    return path

                est = estimate_speech_seconds(variant)
                logger.warning(
                    "[tts] seg=%s 异常音频 %.1fs（预估%.1fs）bytes=%d text=%r attempt=%s，重试",
                    segment_no,
                    probed,
                    est,
                    path.stat().st_size,
                    variant[:48],
                    attempt,
                )
                path.unlink(missing_ok=True)

        logger.warning("[tts] seg=%s 全部重试失败 original=%r", segment_no, text[:48])
        return None

    except Exception as err:
        logger.warning("[tts] seg=%s 异常: %s", segment_no, err)
        return None


async def synthesize_all_segments(
    texts: List[str],
    durations: List[float],
    voice_id: str,
    work_dir: Path,
) -> List[Optional[Path]]:
    """顺序合成各段配音，返回与 texts 等长的路径列表。"""
    work_dir.mkdir(parents=True, exist_ok=True)
    vid = voice_id or settings.tts_voice_default
    model = settings.tts_model.strip() or "cosyvoice-v2"
    logger.info("[tts] 开始顺序合成 segments=%d model=%s voice=%s", len(texts), model, vid)

    results: List[Optional[Path]] = []
    for i, text in enumerate(texts):
        path = await synthesize_segment(text, vid, i + 1, work_dir)
        results.append(path)
        if i + 1 < len(texts):
            await asyncio.sleep(_SEGMENT_GAP_SEC)

    success = sum(1 for r in results if r is not None)
    logger.info("[tts] 配音完成 %d/%d segments voice=%s", success, len(texts), vid)
    return results
