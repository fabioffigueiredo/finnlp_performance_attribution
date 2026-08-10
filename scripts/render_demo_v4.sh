#!/usr/bin/env bash
set -euo pipefail

# Produces a captioned vertical cut from the current evidence-first FinNLP UI.
# The source is a real local Playwright capture of the explicit demonstration
# input and POST /api/analyze response. No external API or audio is used.

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
media_dir="$project_root/media/generated/2026-W33"
input="finnlp-raw-v5.webm"
output="finnlp-verifiable-demo-v4.mp4"
font_name="Verdana"

cd "$media_dir"
test -f "$input"

render_caption() {
  local output_file="$1"
  local headline="$2"
  magick -size 1080x405 "xc:#060B14" \
    -font "$font_name" -fill white -pointsize 50 -gravity northwest -annotate +66+104 "$headline" \
    -fill '#8BB8FF' -pointsize 22 -annotate +66+325 'FinNLP · demonstração pública · sem áudio sintético' \
    "$output_file"
}

render_caption 'finnlp-caption-1-v4.png' $'HTTP 200.\nUma execução rastreável.'
render_caption 'finnlp-caption-2-v4.png' $'Escopo visível.\nDados públicos/sintéticos.'
render_caption 'finnlp-caption-3-v4.png' $'Entrada fictícia\n→ POST /api/analyze.'
render_caption 'finnlp-caption-4-v4.png' $'Contrato rastreável.\nPipelineService para JSON.'
render_caption 'finnlp-caption-5-v4.png' $'Projeto acadêmico.\nSem recomendação de investimento.'

ffmpeg -hide_banner -loglevel error -y -i "$input" \
  -loop 1 -i finnlp-caption-1-v4.png \
  -loop 1 -i finnlp-caption-2-v4.png \
  -loop 1 -i finnlp-caption-3-v4.png \
  -loop 1 -i finnlp-caption-4-v4.png \
  -loop 1 -i finnlp-caption-5-v4.png \
  -filter_complex "
    [0:v]trim=start=11:end=14,setpts=PTS-STARTPTS,crop=506:900:534:0,scale=1080:1920:flags=lanczos,setsar=1[screen_a];
    [1:v]trim=duration=3,setpts=PTS-STARTPTS[caption_a]; [screen_a][caption_a]overlay=0:1515:shortest=1[a];
    [0:v]trim=start=1:end=4,setpts=PTS-STARTPTS,crop=506:900:252:0,scale=1080:1920:flags=lanczos,setsar=1[screen_b];
    [2:v]trim=duration=3,setpts=PTS-STARTPTS[caption_b]; [screen_b][caption_b]overlay=0:1515:shortest=1[b];
    [0:v]trim=start=7:end=11,setpts=PTS-STARTPTS,crop=506:900:252:0,scale=1080:1920:flags=lanczos,setsar=1[screen_c];
    [3:v]trim=duration=4,setpts=PTS-STARTPTS[caption_c]; [screen_c][caption_c]overlay=0:1515:shortest=1[c];
    [0:v]trim=start=11:end=14,setpts=PTS-STARTPTS,crop=506:900:534:0,scale=1080:1920:flags=lanczos,setsar=1[screen_d];
    [4:v]trim=duration=3,setpts=PTS-STARTPTS[caption_d]; [screen_d][caption_d]overlay=0:1515:shortest=1[d];
    [0:v]trim=start=11:end=14,setpts=PTS-STARTPTS,crop=506:900:534:0,scale=1080:1920:flags=lanczos,setsar=1[screen_e];
    [5:v]trim=duration=3,setpts=PTS-STARTPTS[caption_e]; [screen_e][caption_e]overlay=0:1515:shortest=1[e];
    [a][b][c][d][e]concat=n=5:v=1:a=0[v]" \
  -map "[v]" -an -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$output"

for frame in 01:1 04:4 08:8 11:11 14:14; do
  label="${frame%%:*}"
  second="${frame##*:}"
  ffmpeg -hide_banner -loglevel error -y -ss "$second" -i "$output" -frames:v 1 -update 1 \
    "finnlp-v4-frame-${label}.png"
done

magick montage finnlp-v4-frame-01.png finnlp-v4-frame-04.png finnlp-v4-frame-08.png \
  finnlp-v4-frame-11.png finnlp-v4-frame-14.png -tile 5x1 -geometry 216x384+0+0 \
  -strip -define png:exclude-chunks=date,time finnlp-contact-sheet-v4.png
magick finnlp-contact-sheet-v4.png -resize 390x -strip -define png:exclude-chunks=date,time \
  finnlp-mobile-preview-v4.png

ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration \
  -of default=noprint_wrappers=1 "$output"
