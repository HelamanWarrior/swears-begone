#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <video-file>"
    exit 1
fi

input="$1"
parent_dir="$(dirname "$input")"
filename="$(basename "$input")"

scriptdir="$(cd "$(dirname "$0")" && pwd)"
workdir=$(mktemp -d)
trap 'rm -rf "$workdir"' EXIT
cd "$workdir"

run_whisper() {
    docker run --rm --gpus all \
        --user "$(id -u):$(id -g)" \
        -e XDG_CACHE_HOME=/cache \
        -v "$HOME/.cache/whisper:/cache" \
        -v "$workdir:/audio" \
        whisper_timestamped:latest \
        "$@"
}

echo "Extracting audio..."
ffmpeg -hide_banner -v warning -stats \
    -i "$input" -ac 1 -ar 16000 -vn -c:a pcm_s16le -y audio.wav

run_whisper /audio/audio.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/
"$scriptdir/build_mute_swears_cmd.sh" \
    -t "$workdir/audio.wav.words.srt" \
    -i "$input" \
    -s "$scriptdir/swears.txt" \
    -ao

run_whisper /audio/audio_processed.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/
"$scriptdir/build_mute_swears_cmd.sh" \
    -t "$workdir/audio_processed.wav.words.srt" \
    -i "$input" \
    -s "$scriptdir/swears.txt" \
    -ao

mv audio_processed.wav audio_processed_2.wav
run_whisper /audio/audio_processed_2.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/

cat "$workdir"/*.words.srt > "$workdir/final.srt"
"$scriptdir/build_mute_swears_cmd.sh" \
    -t "$workdir/final.srt" \
    -i "$input" \
    -s "$scriptdir/swears.txt"

unclean_dir="$parent_dir/unclean"
mkdir -p "$unclean_dir"
mv "$input" "$unclean_dir/$filename"
echo "Moved '$input' → '$unclean_dir/$filename'"
