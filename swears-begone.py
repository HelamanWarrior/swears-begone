import whisper_timestamped as whisper
import subprocess
import json

LANGUAGE = "eng"
SWEARS_FILE = "swears.txt"

def extract_center_channel(input_video, output_audio):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-map", "0:a",
        "-af", "pan=mono|c0=c2",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        output_audio
    ]
    subprocess.run(cmd, check=True)

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
            if stream['tags']['language'] == LANGUAGE:
                preferred_lang_index = stream['index']
                return preferred_lang_index
    except KeyError:
        print("No subtitle streams were found")
        return None

def extract_embedded_subs(input_video, output_srt):
    sub_channel = identify_dialogue_subs_channel(input_video)

    if sub_channel == None:
        print("No subtitle channel found for perferred language:" + LANGUAGE)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-map", "0:" + str(sub_channel),
        output_srt
    ]
    subprocess.run(cmd, check=True)

def parse_swears_list(input_file):
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")
            swears_list.append(swear_array)
    return swears_list

swears_list = parse_swears_list(SWEARS_FILE)
extract_embedded_subs("example.mkv", "output.srt")
#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)