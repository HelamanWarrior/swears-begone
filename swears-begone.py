import whisper_timestamped as whisper
import subprocess
import json
import re

LANGUAGE = "eng"
SWEARS_FILE = "swears.txt"
WHISPER_MODEL = "medium.en"
WHISPER_DEVICE = "cuda"

def contains_any(text, items):
    pattern = r'\b(' + '|'.join(re.escape(item) for item in items) + r')\b'
    return re.search(pattern, text, re.IGNORECASE) is not None

def detect_audio_codec(input_video):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries",
        "stream=codec_name,bit_rate,channels",
        "-of",
        "default=noprint_wrappers=1",
        input_video
    ]
    stdout = subprocess.check_output(cmd)
    audio_info = dict(
        line.split("=", 1)
        for line in stdout.decode().strip().split("\n")
    )
    print(audio_info)
    return audio_info

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
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list

def transcribe_wordlevel_audio(audio_file, model):
    audio = whisper.load_audio(audio_file)
    result = whisper.transcribe(model, audio, language=LANGUAGE[:-1])
    return result

def parse_swear_word_timestamps(transcription_json, swears_list):
    word_timestamps = []

    for segment in transcription_json["segments"]:
        for word in segment.get("words", []):
            if not contains_any(word["text"], swears_list):
                continue
            word_timestamps.append({
                "word": word["text"],
                "start": float(word["start"]),
                "end": float(word["end"]),
                "confidence": word["confidence"]
            })
    
    return word_timestamps

swears_list = parse_swears_list(SWEARS_FILE)
#extract_center_channel("example.mkv", "dialogue.wav")
detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_swear_word_timestamps(transcript, swears_list))

#extract_embedded_subs("example.mkv", "output.srt")
#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)