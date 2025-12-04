# Swears Begone

A small shell script that automatically detects and mutes profanity in video files.

The script relies on a dockerized version of [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped), which provides accurate per-word timestamps.

## How it Works
1. The script runs a modified version of OpenAI Whisper (via whisper-timestamped) to generate word-level timestamps.
2. It outputs an .srt subtitle file containing each word and its timing.
3. An ffmpeg command is generated muting the audio segments that contain profanity found in the word-level .srt file.
4. Multiple passes are ran to ensure that as much profanity is cleaned as currently possible.
5. The result is a new video file with profanity muted while preserving the original video and audio codecs.

## Installation

You can build the `whisper_timestamped` image using the included Dockerfile:

```bash
docker build -t whisper_timestamped:latest .
```

If you prefer not to use Docker, you may modify the script to call your local installation of whisper-timestamped directly.

## Usage

```
./clean_video.sh <path/to/inputvideo>
```

After the script completes, check the directory containing your input video.
You’ll find two new files, and the original video will be moved into the unclean/ directory:
- unclean/<inputvideo>.mkv
- <inputvideo>[swears-cleaned].mkv
- <inputvideo>[swears-cleaned].txt
The .txt file contains the full ffmpeg command used to mute the detected profanity.
You can reuse this command later if you download or re-encode the video and want to mute the same segments again.
