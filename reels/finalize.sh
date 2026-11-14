#!/usr/bin/env bash
# Copy rendered reels into reels/output with the audio pinned to 48 kHz AAC (video stream untouched).
set -euo pipefail
SRC="${1:?render dir}"; DST="$(dirname "$0")/output"; mkdir -p "$DST"
for f in "$SRC"/R*.mp4; do
  ffmpeg -v error -y -i "$f" -map 0:v -map 0:a -c:v copy -af aresample=48000 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$DST/$(basename "$f")"
  echo "finalised $(basename "$f")"
done
