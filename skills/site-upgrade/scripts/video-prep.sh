#!/usr/bin/env bash
# Prepares a source video for the web (see references/media.md).
#   video-prep.sh <source-video> <out-dir> [name=reel] [poster-second=1]
# Prints the source streams and its scene cuts (chapter candidates), then writes to <out-dir>:
#   <name>.webm / <name>.mp4         720 on the short side, 30fps, silent, a keyframe every second
#                                    plus one at each cut (instant chapter seeks), mp4 with faststart
#   <name>-poster.webp               a frame at [poster-second]
#   <name>-preview.webm / .mp4       240px center-cropped square, 24fps, silent (live thumbnails)
#   <name>-contact.jpg               a contact sheet, one frame every 2 s of the first minute (palette, type, story)
set -euo pipefail

usage="usage: video-prep.sh <source-video> <out-dir> [name] [poster-second]"
src=${1:?$usage}
out=${2:?$usage}
name=${3:-reel}
poster_at=${4:-1}
mkdir -p "$out"

FF=$(command -v ffmpeg || python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')

echo "== source"
"$FF" -hide_banner -i "$src" 2>&1 | grep -E "Duration|Stream" || true

echo "== scene cuts (seconds)"
cuts=$("$FF" -hide_banner -i "$src" -vf "scale=180:-2,select='gt(scene,0.12)',showinfo" -an -f null - 2>&1 |
  grep -oE 'pts_time:[0-9.]+' | cut -d: -f2 |
  awk 'BEGIN { last = -1 } { if ($1 - last > 0.5) { printf "%.2f\n", $1; last = $1 } }' || true)
echo "${cuts:-none found}"
keyframes="0${cuts:+,$(echo "$cuts" | paste -sd, -)}"

# 720 on the short side whatever the orientation; full-range sources are mapped to TV range.
fit="scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)':flags=lanczos:out_range=tv"
video="$fit,fps=30,format=yuv420p"
square="crop='min(iw,ih)':'min(iw,ih)',scale=240:240:flags=lanczos:out_range=tv,fps=24,format=yuv420p"

echo "== encoding"
"$FF" -hide_banner -loglevel error -y -i "$src" -vf "$video" -an \
  -c:v libvpx-vp9 -b:v 0 -crf 36 -g 30 -force_key_frames "$keyframes" -row-mt 1 -deadline good -cpu-used 2 \
  "$out/$name.webm"
"$FF" -hide_banner -loglevel error -y -i "$src" -vf "$video" -an \
  -c:v libx264 -preset slow -crf 23 -profile:v high -g 30 -keyint_min 15 -force_key_frames "$keyframes" \
  -movflags +faststart "$out/$name.mp4"
"$FF" -hide_banner -loglevel error -y -ss "$poster_at" -i "$src" -frames:v 1 -vf "$fit" \
  -c:v libwebp -quality 82 "$out/$name-poster.webp"
"$FF" -hide_banner -loglevel error -y -i "$src" -vf "$square" -an \
  -c:v libvpx-vp9 -b:v 0 -crf 38 -row-mt 1 "$out/$name-preview.webm"
"$FF" -hide_banner -loglevel error -y -i "$src" -vf "$square" -an \
  -c:v libx264 -preset slow -crf 26 -movflags +faststart "$out/$name-preview.mp4"
# contact sheet: one frame every 2 s of the first minute, rows sized to the duration
secs=$("$FF" -hide_banner -i "$src" 2>&1 | awk -F'[:, ]+' '/Duration/ { print int($3 * 3600 + $4 * 60 + $5); exit }')
rows=$(( (${secs:-60} / 2 + 5) / 6 ))
[ "$rows" -lt 1 ] && rows=1
[ "$rows" -gt 5 ] && rows=5
"$FF" -hide_banner -loglevel error -y -i "$src" -vf "fps=1/2,scale=320:-2,tile=6x${rows}:padding=4:color=black" \
  -frames:v 1 -q:v 4 "$out/$name-contact.jpg"

echo "== written"
for f in "$out/$name".webm "$out/$name".mp4 "$out/$name"-poster.webp "$out/$name"-preview.webm "$out/$name"-preview.mp4 "$out/$name"-contact.jpg; do
  printf '%8s  %s\n' "$(du -h "$f" | cut -f1)" "$f"
done
echo "Pin exact chapter times by eyeballing a strip around each cut:"
echo "  $FF -ss <t-0.5> -t 1.2 -i \"$src\" -vf \"fps=5,scale=180:-2,tile=6x1\" -frames:v 1 strip.png"
