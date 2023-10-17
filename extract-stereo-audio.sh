#! /bin/bash

input="$1"
prefix="${input%.*}"
output="${prefix} (Stereo).mp3"

ffmpeg -i "${input}" -vn -ar 44100 -ac 2 -b:a 192k "${output}"