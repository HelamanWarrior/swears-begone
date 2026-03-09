from config import LANGUAGE
import utils.search as search
import utils.ffmpeg_helper as ffmpeg
import json
import subprocess

def identify_dialogue_subs_channel(input_video):
    """
    Given a video (path), identifies the which channel the subtitles are found on.
    It identifies the first subtitle stream matching the perferred lang config.

    Returns: int (channel number), None (if no compatible subtitle channel found).
    """
    stdout = ffmpeg.ffprobe_subs_channel(input_video)
    video_info = json.loads(stdout)

    try:
        streams = video_info['streams']
        preferred_lang_index = 0

        for stream in streams:
            if stream['tags']['language'] == LANGUAGE:
                preferred_lang_index = stream['index']
                return preferred_lang_index
    except KeyError:
        print("No subtitle streams were found")
        return None

def extract_embedded_subs(input_video, output_srt):
    """
    Extracts and writes out the embedded subtitles into an SRT file.
    Automatically identifies correct subtitles using preferred lang config.

    input_video (str): path to the video to extract subs from.
    output_srt (str): path to output SRT subtitle file.
    """
    sub_channel = identify_dialogue_subs_channel(input_video)

    if sub_channel is None:
        print("No subtitle channel found for perferred language:" + LANGUAGE)
        return

    ffmpeg.extract_subtitle_file(input_video, sub_channel, output_srt)

def srt_to_seconds(timestamp):
    """
    Converts timestamp (str) from 'HH:MM:SS,mmm' (standard SubRip format) 
    to total seconds (float).

    >>> srt_to_seconds("01:26:02,773")
    5162.773
    """
    h, m, s_ms = timestamp.split(':')
    s, ms = s_ms.split(',')

    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

def srt_time_interval_to_seconds(interval):
    """
    Converts a list of SRT timecode pairs into a list of float intervals in seconds.

    The input format is expected to be 'HH:MM:SS,mmm' (standard SubRip).
    Each timestamp is converted to its total elapsed time in seconds.

    >>> srt_time_interval_to_seconds([
    ...    ['00:00:17,770', '00:00:18,938'], 
    ...    ['00:00:42,127', '00:00:43,921']
    ... ])
    [[17.77, 18.938], [42.127, 43.921]]
    """
    ffmpeg_ts = []

    for ts_start, ts_end in interval:
        seconds_start = srt_to_seconds(ts_start)
        seconds_end = srt_to_seconds(ts_end)
        ffmpeg_ts.append([seconds_start, seconds_end])
    
    return ffmpeg_ts

def get_subtitle_blocks(file):
    """
    Given an SRT file, yields a block of the time intervals and text dialogue.
    """
    current_ts = None
    current_text = []

    for line in file:
        line = line.strip()

        if "-->" in line:
            # If we were already tracking a block, yield it before starting new one
            if current_ts and current_text:
                yield current_ts, " ".join(current_text)
            
            current_ts = [t.strip() for t in line.split("-->")]
            current_text = []
        elif line and line.isdigit():
            # Skip the index numbers (1, 2, 3...)
            continue
        elif line:
            # Collect lines of dialogue
            current_text.append(line)
    
    # Yield the very last block in the file
    if current_ts and current_text:
        yield current_ts, " ".join(current_text)

def find_swear_intervals(srt_file, swears_list):
    """
    Locates time intervals in an SRT file containing profanity.
    Returns a list of [start, end] floats in seconds.

    swears_list: a list of swear words (str) to filter out.

    Example output:
        [[183.75, 188.62], [273.23, 276.46]]
    """
    with open(srt_file, "r") as file:
        swear_timestamps = [
            ts for ts, text in get_subtitle_blocks(file) 
            if search.contains_any(text, swears_list)
        ]

    return swear_timestamps