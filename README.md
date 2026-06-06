# Swears Begone

Remove profanity from any video file with the power of Whisper.

## Approach

Currently an existing subtitle file must be attached to the video source. If not present, the `subliminal` library attempts to download the best matching subtitle. With existing subtitles, the app detects time segments where swearing is present and processes only those segments with Whisper to retrieve precise timestamps; this dramatically increases the speed of swear detection and lowers VRAM usage.

## Installation

```bash
git clone https://github.com/HelamanWarrior/swears-begone.git
cd swears-begone
pip install .
```

## Usage

```bash
swears-begone -h         
usage: swears-begone [-h] -i <input video> [-m <model>] [-l <language>] [-w <swears.txt>] [-c <sub channel>]
                     [-s <sub file>] [-e] [--cpu] [--edl]

options:
  -h, --help            show this help message and exit
  -i, --input <input video>
                        input video file
  -m, --model <model>   whisper model to use for word-level transcription and detection (default is
                        "large-v3")
  -l, --lang <language>
                        language for extracting srt and swears detection (default is "eng")
  -w, --swears <swears.txt>
                        text file containing profanity (with optional mapping)
  -c, --sub_channel <sub channel>
                        specify a subtitle channel index to clean
  -s, --srt_file <sub file>
                        external subtitle SRT file for swears detection
  -e, --embed-subs      embed subtitles in resulting video file
  --cpu                 force Whisper to use the CPU backend device
  --edl                 generate MPlayer EDL file with mute actions
```