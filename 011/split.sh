#!/usr/bin/env bash
set -euo pipefail
mkdir -p 011/source 011/output
SRC_URL="https://raw.githubusercontent.com/rneiss/PocketTorah/master/data/audio/Noach-4.mp3"
LABEL_URL="https://raw.githubusercontent.com/rneiss/PocketTorah/master/data/torah/labels/Noach-4.txt"
curl -fL "$SRC_URL" -o 011/source/Noach-4-source.mp3
curl -fL "$LABEL_URL" -o 011/source/Noach-4-labels.txt
rm -f 011/output/*.mp3 011/output/durations.tsv
printf 'reference\tduration_seconds\n' > 011/output/durations.tsv
awk -F '\t' 'NR>1 && NF>=3 && $1 !~ /^#/ && $2 ~ /^[0-9]+([.][0-9]+)?$/ && ($3 ~ /^[0-9]+([.][0-9]+)?$/ || $3 ~ /^EOF\r?$/) {gsub(/\r/,"",$1); gsub(/\r/,"",$2); gsub(/\r/,"",$3); print $1 "\t" $2 "\t" $3}' 011/boundaries.tsv |
while IFS=$'\t' read -r ref start end; do
  if [[ -z "${ref:-}" || -z "${start:-}" || -z "${end:-}" ]]; then
    echo "Invalid boundary row: ref=<$ref> start=<$start> end=<$end>" >&2
    exit 1
  fi
  echo "Splitting $ref: $start -> $end"
  out="011/output/${ref}.mp3"
  if [[ "$end" == "EOF" ]]; then
    ffmpeg -hide_banner -loglevel error -y -ss "$start" -i 011/source/Noach-4-source.mp3 -map_metadata -1 -vn -c:a libmp3lame -q:a 2 "$out"
  else
    dur=$(awk -v e="$end" -v s="$start" 'BEGIN{printf "%.6f", e-s}')
    ffmpeg -hide_banner -loglevel error -y -ss "$start" -i 011/source/Noach-4-source.mp3 -t "$dur" -map_metadata -1 -vn -c:a libmp3lame -q:a 2 "$out"
  fi
  actual=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$out")
  printf '%s\t%s\n' "$ref" "$actual" >> 011/output/durations.tsv
done
count=$(find 011/output -maxdepth 1 -name 'Genesis-*.mp3' | wc -l)
if [[ "$count" -ne 15 ]]; then
  echo "Expected 15 clips, generated $count" >&2
  exit 1
fi
