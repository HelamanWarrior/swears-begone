import subprocess

def ffprobe_subs_channel(input_video):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-of", "json",
        input_video,
        "-of", "json",
        "-show_entries", "stream=index:stream_tags=language",
        "-select_streams", "s"
    ]
    return subprocess.check_output(cmd)

def extract_subtitle_file(input_video, sub_channel, output_srt):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,
        "-map", "0:" + str(sub_channel),
        output_srt
    ]
    subprocess.run(cmd, check=True)

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
    stdout = subprocess.check_output(cmd).decode()
    audio_info = {
        key: int(value) if value.isdigit() else value
        for line in stdout.strip().split("\n")
        for key, value in [line.split("=", 1)]
    }
    return audio_info

def extract_audio_dialogue_file(input_video, output_audio, start_time=None, end_time=None):
    """
    Extracts audio from as video file, optionally within a specific time range.
    The resultant audio is mono WAV which captures the center channels for best capturing
    the dialogue.
    """
    cmd = ["ffmpeg", "-y", "-i", input_video, "-map", "0:a"]

    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    if end_time is not None:
        cmd.extend(["-to", str(end_time)])

    cmd.extend([
        "-af", "pan=mono|c0=c2",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        output_audio
    ])
    subprocess.run(cmd, check=True)