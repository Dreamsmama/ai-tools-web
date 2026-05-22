#!/usr/bin/env bash
# 重新生成 public/short-drama/bgm 占位曲（约 -13 LUFS，可听见）
# 正式环境请替换为版权清晰的钢琴/Lo-fi 等 MP3，保持文件名不变即可。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BGM_DIR="$ROOT/ai-tools-frontend/public/short-drama/bgm"
FFMPEG="${FFMPEG:-$(command -v ffmpeg)}"
mkdir -p "$BGM_DIR"

gen() {
  local name=$1 f1=$2 f2=$3
  "$FFMPEG" -y -f lavfi -i "sine=frequency=${f1}:duration=60" -f lavfi -i "sine=frequency=${f2}:duration=60" \
    -filter_complex "[0:a][1:a]amix=inputs=2:duration=first,volume=4,alimiter=limit=0.92,loudnorm=I=-14:TP=-1:LRA=7" \
    -c:a libmp3lame -q:a 2 "$BGM_DIR/$name" -loglevel error
  echo "wrote $name"
}

gen sad_piano.mp3 196 262
gen midnight_lofi.mp3 110 165
gen stressful_office.mp3 180 227
gen light_fun.mp3 330 440
gen emotional_soft.mp3 220 277
echo "Done. Files in $BGM_DIR"
