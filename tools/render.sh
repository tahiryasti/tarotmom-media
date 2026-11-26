#!/usr/bin/env bash
# Usage: tools/render.sh specs/2026-11-25.json videos/2026-11-25.mp4
set -euo pipefail
SPEC="$1"; OUT="$2"; TMP=$(mktemp -d)
python3 "$(dirname "$0")/make_video.py" "$TMP/v.mp4" render "$SPEC"
ffmpeg -y -loglevel error -f lavfi -i "sine=f=220:d=15" -f lavfi -i "sine=f=277.18:d=15" -f lavfi -i "sine=f=329.63:d=15" -f lavfi -i "sine=f=440:d=15" \
 -filter_complex "[0]volume=0.5[a];[1]volume=0.35[b];[2]volume=0.35[c];[3]volume=0.15,tremolo=f=0.3:d=0.8[d];[a][b][c][d]amix=4,tremolo=f=0.15:d=0.4,aecho=0.8:0.7:600|1200:0.4|0.25,lowpass=f=1800,afade=t=in:d=1.5,afade=t=out:st=13.5:d=1.5,volume=0.6" -c:a aac -b:a 160k "$TMP/a.m4a"
ffmpeg -y -loglevel error -i "$TMP/v.mp4" -i "$TMP/a.m4a" -map 0:v -map 1:a -c:v copy -shortest -movflags +faststart "$TMP/out.mp4"
mv "$TMP/out.mp4" "$OUT"; rm -rf "$TMP"; echo "wrote $OUT"
