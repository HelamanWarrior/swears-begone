#!/bin/bash

# Ask for sudo password at the beginning (needed for removing files the docker container creates)
sudo -v

# --- First Pass ---
ffmpeg -hide_banner -v warning -stats -i "$1" -ac 1 -ar 16000 -vn -c:a pcm_s16le -y "audio.wav"
docker run --rm --gpus all -v $HOME/.cache/whisper:/root/.cache/whisper -v $HOME/Docker/whisper-timestamped:/audio whisper_timestamped:latest /audio/audio.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/
./build_mute_swears_cmd.sh -t audio.wav.words.srt -i "$1" -ao

# --- Second Pass ---
docker run --rm --gpus all -v $HOME/.cache/whisper:/root/.cache/whisper -v $HOME/Docker/whisper-timestamped:/audio whisper_timestamped:latest /audio/audio_processed.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/
./build_mute_swears_cmd.sh -t audio_processed.wav.words.srt -i "$1" -ao

# --- Third Pass ---
mv audio_processed.wav audio_processed_2.wav
sleep 3
docker run --rm --gpus all -v $HOME/.cache/whisper:/root/.cache/whisper -v $HOME/Docker/whisper-timestamped:/audio whisper_timestamped:latest /audio/audio_processed_2.wav --model medium.en --language en --accurate --output_format srt --output_dir /audio/

# Merge srts for a more complete swear word removal
cat audio.wav.words.srt audio_processed.wav.words.srt audio_processed_2.wav.words.srt > final.srt

# Remove unused files
sudo rm audio.wav.srt audio.wav.words.srt audio_processed.wav.srt audio_processed.wav.words.srt audio_processed_2.wav.srt audio_processed_2.wav.words.srt audio.wav audio_processed_2.wav

# Generate ffmpeg command
./build_mute_swears_cmd.sh -t final.srt -i "$1" 

parent_dir="$(dirname "$1")"
filename="$(basename "$1")"

unclean_dir="$parent_dir/unclean"
mkdir -p "$unclean_dir" 

mv "$1" "$unclean_dir/$filename"
echo "Moved '$1' → '$unclean_dir/$filename'"
