from utils.file_helper import update_filename, dir_filepath
import subprocess

def ffprobe_subs_metadata(input_video):
    """
    Retrieves subtitle stream metadata from a video file using ffprobe.

    Returns:
        bytes: A JSON-formatted byte string containing stream indices and language tags.

    Args:
        input_video (str | Path): Path to the video file to be analyzed.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "s",
        "-show_entries", "stream=index:stream_tags=language",
        "-of", "json",
        str(input_video)
    ]
    return subprocess.check_output(cmd)

def extract_subtitle_file(input_video, sub_channel, output_srt):
    """
    Extracts a specific subtitle stream from a video file and saves it as an SRT.

    Args:
        input_video (str | Path): Path to the source video file.
        sub_channel (int | str): The index of the subtitle stream (e.g., 0, 1, 2)
        output_srt (str): Destinatino path forr the extracted .srt file.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(input_video),
        "-map", f"0:{sub_channel}",
        str(output_srt)
    ]
    subprocess.run(cmd, check=True)

def detect_audio_info(input_video):
    """
    Given an input_video detects the audio information.

    Returns (dict): {'codec_name', 'channels', 'bitrate'}

    Args:
        input_video (str | Path): Path to the source video for audio detection.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries",
        "stream=codec_name,bit_rate,channels",
        "-of",
        "default=noprint_wrappers=1",
        str(input_video)
    ]
    stdout = subprocess.check_output(cmd).decode()
    audio_info = {
        key: value
        for line in stdout.strip().split("\n")
        for key, value in [line.split("=", 1)]
    }
    return audio_info

def extract_audio_dialogue_file(input_video, output_audio, start_time=None, end_time=None):
    """
    Extracts audio from as video file, optionally within a specific time range.
    The resultant audio is mono WAV which captures the center channels for best capturing
    the dialogue.

    Args:
        input_video (str | Path): Path to the source video.
        output_audio (str | Path): Path to save the output audio file.
        start_time, end_time (float|str): a duration of seconds.
    """
    cmd = [
        "ffmpeg",
        "-y", 
        "-hide_banner", 
        "-loglevel", "error", 
        "-i", str(input_video), 
        "-map", "0:a"
    ]

    if start_time is not None:
        cmd.extend(["-ss", str(start_time)])
    if end_time is not None:
        cmd.extend(["-to", str(end_time)])

    cmd.extend([
        "-af", "pan=mono|c0=c2",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        str(output_audio)
    ])
    subprocess.run(cmd, check=True)

def extract_audio_segments(input_video, intervals, output_dir):
    """
    Extracts many audio segments from a video file, saving them into seperate audio files.
    
    Args:
        input_video (str | Path): Path to the source video file to extract audio from.
        intervals (list): list of [start, stop] second interval lists.
        output_dir (str | Path): Path to the directory for extracted audio.
    """
    for i, interval in enumerate(intervals):
        audio_file = dir_filepath(output_dir, f"audio_{i}.wav")
        print(f"Extracting audio segment {i+1}: {audio_file}")

        start, end = interval[0], interval[1]
        extract_audio_dialogue_file(input_video, audio_file, start, end)

def mute_filter(s):
    """
    Creates an ffmpeg mute filter command for a segment of time.

    Returns: str filter command for the given segment.

    Args:
        s (dict): contains 'start' and 'end' keys both containing float seconds.
    """
    return f"volume=enable='between(t,{s['start']}, {s['end']})':volume=0"

def export_cleaned_video(input_video, mute_segments):
    """
    Creates the final filtered version of the video, with profanity segments muted.
    The resultant video is saved with "-clean" appended to the filename.

    Args:
        input_video (str | Path): Path to the input video.
        mute_segments (dict): contains {'start', 'end'} keys in float seconds.
    """
    mute_cmds = [mute_filter(segment) for segment in mute_segments]
    audio_filter = ",".join(mute_cmds)

    audio_info = detect_audio_info(input_video)

    output_video = update_filename(input_video, "", "-cleaned")
    
    print(f"Exporting: {output_video}")
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-i", str(input_video),
        "-af", audio_filter,
        "-c:v", "copy",
        "-c:a", audio_info['codec_name'],
        "-ac", audio_info['channels'],
        "-b:a", audio_info['bit_rate'],
        output_video
    ]
    subprocess.run(cmd, check=True)

def write_edl_file(mute_segments, output_edl):
    """
    Creates an EDL (Edit decision list) file, containing the segments to mute the audio.

    Args:
        mute_segments (dict): contains {'start', 'end'} keys in float seconds.
        output_edl (str | Path): Path to save the EDL file.
    """
    lines = []
    for segment in mute_segments:
        start = str(segment['start'])
        end = str(segment['end'])
        lines.append(f"{start} {end} 1\n")
    
    with open(str(output_edl), 'w') as f:
        f.writelines(lines)
    
    print(f"Written {output_edl}!\nUse this file with Kodi or MPlayer, if you wish to preserve the original file.")