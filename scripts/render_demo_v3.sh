#!/usr/bin/env bash
set -euo pipefail

# Rebuilds the public, captioned LinkedIn demo from the same real Playwright
# capture used by V2. V3 front-loads the observable endpoint response, then
# explains the fictional scenario and execution path. It never calls an
# external API or adds an audio track.

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
media_dir="$project_root/media/generated/2026-W33"
input="finnlp-raw-v2.webm"
output="finnlp-verifiable-demo-v3.mp4"
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

render_caption 'finnlp-caption-1-v3.png' $'Resposta do endpoint real.\nHTTP 200.'
render_caption 'finnlp-caption-2-v3.png' $'Cenário público\ne fictício.'
render_caption 'finnlp-caption-3-v3.png' $'POST /api/analyze\n→ PipelineService.'
render_caption 'finnlp-caption-4-v3.png' $'Interface → endpoint HTTP\n→ serviço.'
render_caption 'finnlp-caption-5-v3.png' $'Projeto acadêmico.\nSem recomendação de investimento.'

ffmpeg -hide_banner -loglevel error -y -i "$input" \
  -loop 1 -i finnlp-caption-1-v3.png \
  -loop 1 -i finnlp-caption-2-v3.png \
  -loop 1 -i finnlp-caption-3-v3.png \
  -loop 1 -i finnlp-caption-4-v3.png \
  -loop 1 -i finnlp-caption-5-v3.png \
  -filter_complex "
    [0:v]trim=start=28:end=31,setpts=PTS-STARTPTS,crop=560:960:520:280,scale=1080:1920:flags=lanczos,setsar=1[screen_a];
    [1:v]trim=duration=3,setpts=PTS-STARTPTS[caption_a]; [screen_a][caption_a]overlay=0:1515:shortest=1[a];
    [0:v]trim=start=16:end=19,setpts=PTS-STARTPTS,crop=560:960:220:0,scale=1080:1920:flags=lanczos,setsar=1[screen_b];
    [2:v]trim=duration=3,setpts=PTS-STARTPTS[caption_b]; [screen_b][caption_b]overlay=0:1515:shortest=1[b];
    [0:v]trim=start=25:end=30,setpts=PTS-STARTPTS,crop=560:960:520:0,scale=1080:1920:flags=lanczos,setsar=1[screen_c];
    [3:v]trim=duration=5,setpts=PTS-STARTPTS[caption_c]; [screen_c][caption_c]overlay=0:1515:shortest=1[c];
    [0:v]trim=start=31:end=36,setpts=PTS-STARTPTS,crop=560:960:520:0,scale=1080:1920:flags=lanczos,setsar=1[screen_d];
    [4:v]trim=duration=5,setpts=PTS-STARTPTS[caption_d]; [screen_d][caption_d]overlay=0:1515:shortest=1[d];
    [0:v]trim=start=33:end=37,setpts=PTS-STARTPTS,crop=560:960:520:0,scale=1080:1920:flags=lanczos,setsar=1[screen_e];
    [5:v]trim=duration=4,setpts=PTS-STARTPTS[caption_e]; [screen_e][caption_e]overlay=0:1515:shortest=1[e];
    [a][b][c][d][e]concat=n=5:v=1:a=0[base];
    [base]null[v]" \
  -map "[v]" -an -c:v libx264 -pix_fmt yuv420p -movflags +faststart "$output"

ffprobe -v error -show_entries stream=codec_name,width,height -show_entries format=duration \
  -of default=noprint_wrappers=1 "$output"

# Evidence previews are generated from the final export, never from a design mockup.
for frame in 01:1 04:4 08:8 13:13 18:18; do
  label="${frame%%:*}"
  second="${frame##*:}"
  ffmpeg -hide_banner -loglevel error -y -ss "$second" -i "$output" -frames:v 1 \
    -update 1 "finnlp-v3-frame-${label}.png"
done

magick montage finnlp-v3-frame-01.png finnlp-v3-frame-04.png finnlp-v3-frame-08.png \
  finnlp-v3-frame-13.png finnlp-v3-frame-18.png -tile 5x1 -geometry 216x384+0+0 \
  -strip -define png:exclude-chunks=date,time finnlp-contact-sheet-v3.png
magick finnlp-contact-sheet-v3.png -resize 390x -strip -define png:exclude-chunks=date,time \
  finnlp-mobile-preview-v3.png
