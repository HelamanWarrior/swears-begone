import config
import utils.search as search
import json
import subprocess

def identify_dialogue_subs_channel(input_video):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-of", "json",
        input_video,
        "-of", "json",
        "-show_entries", "stream=index:stream_tags=language",
        "-select_streams", "s"
    ]
    stdout = subprocess.check_output(cmd)
    video_info = json.loads(stdout)

    try:
        streams = video_info['streams']
        preferred_lang_index = 0

        for stream in streams:
            if stream['tags']['language'] == config.LANGUAGE:
                preferred_lang_index = stream['index']
                return preferred_lang_index
    except KeyError:
        print("No subtitle streams were found")
        return None

def extract_embedded_subs(input_video, output_srt):
    sub_channel = identify_dialogue_subs_channel(input_video)

    if sub_channel == None:
        print("No subtitle channel found for perferred language:" + config.LANGUAGE)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-map", "0:" + str(sub_channel),
        output_srt
    ]
    subprocess.run(cmd, check=True)

def srt_to_seconds(timestamp):
    """
    00:00:05,799
    """
    time_list = timestamp.replace(",", ":").split(":")

    h, m, s, ms = [int(x) for x in time_list]
    total_seconds = (h * 3600) + (m * 60) + s + (ms / 1000)

    return total_seconds

def swear_srt_to_seconds(swear_ts):
    ffmpeg_ts = []

    for ts_start, ts_end in swear_ts:
        seconds_start = srt_to_seconds(ts_start)
        seconds_end = srt_to_seconds(ts_end)
        ffmpeg_ts.append([seconds_start, seconds_end])
    print(ffmpeg_ts)
    
    return ffmpeg_ts

def get_subtitle_blocks(file):
    """Yields timestamp and text as a pair."""
    current_ts = None
    for line in file:
        line = line.strip()
        if "-->" in line:
            current_ts = [t.strip() for t in line.split("-->")]
        elif line and current_ts:
            yield current_ts, line

def detect_swear_time_in_subs(srt_file, swears_list):
    file = open(srt_file, "r")
    
    swear_timestamps = [ts for ts, text in get_subtitle_blocks(file) if search.contains_any(text, swears_list)]
    file.close()

    return swear_timestamps