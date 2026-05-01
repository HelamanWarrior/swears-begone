import srt
import json
import subprocess
import subliminal
from pathlib import Path
from babelfish import Language
from swears_begone.ffmpeg_helper import (
    ffprobe_subs_metadata,
    extract_subtitle_file,
    extract_audio_dialogue_file
)
from swears_begone.search import (
    contains_any,
    replace_with_mapping
)

IMAGE_CODECS = ["hdmv_pgs_subtitle", "dvd_subtitle", "dvdsub", "pgssub"]

def identify_dialogue_subs_channel(input_video: str | Path, lang: str) -> int:
    """
    Given a video (path), identifies the which channel the subtitles are found on.
    It identifies the first subtitle stream matching the perferred lang config.

    Returns: int (channel number), None (if no compatible subtitle channel found).

    Args:
        input_video (str | path): Source video for identifying subtitle channel.
    """
    stdout = ffprobe_subs_metadata(input_video)
    video_info = json.loads(stdout)

    valid_text_subs = [
        s for s in video_info['streams']
        if s.get("codec_name") not in IMAGE_CODECS
    ]

    if not valid_text_subs:
        print("No text-based subtitles found. Skipping subtitle extraction.")
        return None

    preferred_lang_index = 0

    for stream in valid_text_subs:
        forced = stream['disposition']['forced'] == 1

        if stream['tags']['language'] == lang and not forced:
            preferred_lang_index = stream['index']
            print(f"Using subtitle index: {preferred_lang_index}")
            return preferred_lang_index

def extract_embedded_subs(
    input_video: str | Path,
    output_srt: str | Path,
    lang: str,
    target_channel: int=-1
) -> int:
    """
    Extracts and writes out the embedded subtitles into an SRT file.
    Automatically identifies correct subtitles using preferred lang config.

    Returns: (int) channel of extracted subtitle stream.
        -1 if no subtitle stream was detected.

    Args:
        input_video (str | Path): path to the video to extract subs from.
        output_srt (str | Path): path to output SRT subtitle file.
    """
    sub_channel = target_channel

    if sub_channel == -1:
        print(f"Performing automatic subtitle detection for lang: {lang}")
        sub_channel = identify_dialogue_subs_channel(input_video, lang)

        if sub_channel is None:
            print(f"- No subtitle channel found for perferred language.")
            return -1

    extract_subtitle_file(input_video, sub_channel, output_srt)
    return sub_channel

def srt_to_seconds(timestamp: str) -> float:
    """
    Converts timestamp (str) from 'HH:MM:SS.mmm' (standard SubRip format) 
    to total seconds (float).

    >>> srt_to_seconds("01:26:02.773")
    5162.773
    """
    h, m, s = timestamp.split(':')

    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_srt_time(intervals: str, padding: int = 0) -> list[list[float]]:
    """
    Converts a list of SRT timecode pairs into a list of float intervals in seconds.

    The input format is expected to be 'HH:MM:SS,mmm' (standard SubRip).
    Each timestamp is converted to its total elapsed time in seconds.

    >>> parse_srt_time([
    ...    ['00:00:17,770', '00:00:18,938'], 
    ...    ['00:00:42,127', '00:00:43,921']
    ... ])
    [[17.77, 18.938], [42.127, 43.921]]
    """
    ffmpeg_ts = []

    for ts_start, ts_end in intervals:
        seconds_start = srt_to_seconds(ts_start) - padding
        seconds_end = srt_to_seconds(ts_end) + padding
        ffmpeg_ts.append([seconds_start, seconds_end])
    
    return ffmpeg_ts

def find_swear_intervals(
    srt_file: str | Path, 
    swears_list: list[str]
) -> list[list[float]]:
    """
    Locates time intervals in an SRT file containing profanity.
    Returns a list of [start, end] floats in seconds.

    Args:
        srt_file (str | Path): subtitle file for swear interval detection.
        swears_list: a list of swear words (str) to filter out.

    Example output:
        [[183.75, 188.62], [273.23, 276.46]]
    """
    swear_timestamps = []

    with open(str(srt_file), "r") as file:
        subtitle_generator = srt.parse(file)
        subtitles = list(subtitle_generator)
        for sub in subtitles:
            if contains_any(sub.content, swears_list):
                swear_timestamps.append([str(sub.start), str(sub.end)])
    
    print(f"Identified {len(swear_timestamps)} swears in subtitles!")
    return swear_timestamps

def clean_subtitles(
    input_srt: str | Path,
    swear_dict: dict[str, str],
    output_srt: str | Path
) -> None:
    """
    Filters profanity within a SubRip (SRT) file using a replacement dictionary.

    Iterates through the subtitle text and replaces identified words with either a 
    generic mask ("****") or a specific substitute provided in the `swear_dict`.

    Args:
        input_srt (str | Path): Path to the subrip file to filter.
        swear_dict (dict): A mapping where keys are profanities (str) and
            values are their intended replacements (str).
        output_srt (str | Path): Path to the resultant filtered SRT file.
    """
    subtitles = []
    with open(str(input_srt), 'r') as f:
        subtitle_generator = srt.parse(f)
        subtitles = list(subtitle_generator)

    for sub in subtitles:
        sub.content = replace_with_mapping(sub.content, swear_dict, "****")
    
    with open(str(output_srt), 'w') as f:
        f.writelines(srt.compose(subtitles))

def download_subtitle(video: str | Path, lang: str) -> Path:
    video_path = Path(video)

    video = subliminal.scan_video(str(video_path))
    subtitles = subliminal.download_best_subtitles({video}, {Language(lang)})

    if not subtitles.get(video):
        raise FileNotFoundError(f"No subtitles found for {video_path.name}")
    
    print(f"- Subtitle search target: {video.title} ({video.year})")

    best_sub = subtitles[video][0]
    output_srt = video_path.with_suffix('.srt')

    with open(output_srt, 'w', encoding='utf-8') as f:
        f.write(best_sub.text)
    
    return output_srt