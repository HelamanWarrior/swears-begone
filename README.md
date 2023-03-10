# Swares Begone

A small shell script that mutes profanity from video files.

This script requires [cleanvid](https://github.com/mmguero/cleanvid) & [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped).
Huge thanks to all the work that's gone into these amazing projects.

## Description

This script utilizes a modified version of OpenAI whispered that can generate timestamps between each word.
It outputs a subtitle `srt` file which is sent to `cleanvid` that handles muting the profanity.
By utilizing the timestamps created by `whisper-timestamped` cleanvid can find the exact location cursing is present and mute the word.

## Installation

Install `cleanvid`

```bash
python3 -m pip install -U cleanvid
```

Install `whisper-timestamped`

```bash
pip3 install git+https://github.com/linto-ai/whisper-timestamped
pip3 install matplotlib
```

## Potential drawbacks

1. Audio is converted to AAC 
    - This ensures that the audio can be used in the final container & ensures ffmpeg knows which container to extract the audio to.
    - High bitrate is used to avoid compression artifacts.
    - Surround sound channels are preserved.
2. Final video is forced to utilize the `.mp4` container
    - Timestamp issues occur when exporting to `.mkv`. Otherwise this container would be used instead.
3. Multiple passes
    - Used to ensure accuracy. 
    - Makes the script take longer to complete.

Feel free to improve the project, to help remove these drawbacks.