#!/bin/bash
# Encode a rendered WAV for distribution.
#
# MP3 is encoded at 320 kbps CBR with forced left/right stereo (no joint
# stereo). The entrainment layer depends on each channel keeping its own
# carrier, so mid/side encoding is deliberately disabled.
#
# Usage: scripts/encode.sh renders/<name>.wav
set -euo pipefail

wav="$1"
base="${wav%.wav}"

ffmpeg -hide_banner -loglevel error -y -i "$wav" \
  -c:a libmp3lame -b:a 320k -joint_stereo 0 \
  -metadata title="$(basename "$base")" \
  -metadata artist="Enlightenment (open experiment)" \
  -metadata comment="Reproducible render; parameters in filename. github.com/CitadelAI-Atlas/enlightenment" \
  "$base.mp3"

ffmpeg -hide_banner -loglevel error -y -i "$wav" \
  -c:a aac -b:a 256k "$base.m4a"

ls -lh "$wav" "$base.mp3" "$base.m4a"
