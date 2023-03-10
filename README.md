# Swares Begone

A small shell script that mutes profanity from video files.

This script requires [cleanvid](https://github.com/mmguero/cleanvid) & [whisper-timestamped](https://github.com/linto-ai/whisper-timestamped)

## Description

This script utilizes a modified version of OpenAI whispered that can generate timestamps between each word.
It outputs a subtitle `srt` file which is then sent to `cleanvid` which handles muting the profanity.
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