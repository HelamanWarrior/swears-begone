# Swears Begone!

Remove profanity from any video file with the power of Whisper (a local speech-to-text model developed by OpenAI).

## Approach

Currently an existing subtitle file must be attached to the video source. If not present, the `subliminal` library attempts to download the best matching subtitle. With existing subtitles, the app detects time segments where swearing is present and processes only those segments with Whisper to retrieve precise timestamps; this dramatically increases the speed of swear detection and lowers VRAM usage.

## Installation

### 1. Prerequisites

**swears-begone** requires **FFmpeg** to manage the video files.
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from the official [FFmpeg site](https://ffmpeg.org/download.html#build-windows) and add its `/bin` folder to your System PATH.

### 2. Setup Environment

It's recommended to install this in an isolated virtual environment to prevent dependency conflicts:

```bash
git clone https://github.com/HelamanWarrior/swears-begone.git
cd swears-begone
python3 -m venv .venv

# Activate the environment
source .venv/bin/activate  # Linux/macOS
# Or on Windows (Command Prompt): .venv\Scripts\activate.bat
# Or on Windows (Powershell): .venv\Scripts\Activate.ps1
```

### 3. Choose Your Installation Method

#### Option A: CPU Only (Simplest)

If you do not have an NVIDIA GPU, or just want to run the tool on your processor, install the base package directly:

```bash
pip install .
```

#### Option B: NVIDIA GPU Acceleration (Recommended for Speed)

To utilize your NVIDIA graphics card, you must install the CUDA runtime libraries alongside the package.

```bash
pip install ".[cuda]"
```

## 4. Verify Installation

To confirm everything is installed and working correctly, run:

```bash
swears-begone -i example-unclean-movie.mkv
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