import subprocess
from pathlib import Path

def ffprobe_subs_metadata(input_video: str | Path) -> bytes:
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
        "-show_entries", 
        "stream=index:stream_tags=language,title:disposition=forced,comment,default",
        "-of", "json",
        str(input_video)
    ]
    return subprocess.check_output(cmd)

def extract_subtitle_file(
    input_video: str | Path, 
    sub_channel: int,
    output_srt: str | Path
) -> None:
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
        "-c:s", "subrip",
        "-map", f"0:{sub_channel}",
        str(output_srt)
    ]
    subprocess.run(cmd, check=True)

def detect_audio_info(input_video: str) -> dict[str, str | int]:
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

def extract_audio_dialogue_file(
    input_video: str | Path,
    output_audio: str | Path,
    start: float | str=None,
    end: float | str=None
) -> None:
    """
    Extracts audio from as video file, optionally within a specific time range.
    The resultant audio is mono WAV which captures the center channels for best capturing
    the dialogue.

    Args:
        input_video (str | Path): Path to the source video.
        output_audio (str | Path): Path to save the output audio file.
        start, end (float|str): a duration of seconds.
    """
    cmd = [
        "ffmpeg",
        "-y", 
        "-hide_banner", 
        "-loglevel", "error"
    ]

    if start is not None:
        cmd.extend(["-ss", str(start)])
    if end is not None:
        cmd.extend(["-to", str(end)])

    cmd.extend([
        "-i", str(input_video), 
        "-map", "0:a:0",
        "-af", "pan=mono|c0=c2",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        str(output_audio)
    ])
    subprocess.run(cmd, check=True)

def extract_audio_segments(
    input_video: str | Path, 
    intervals: list[float], 
    output_dir: str | Path
) -> None:
    """
    Extracts many audio segments from a video file, saving them into seperate audio files.
    
    Args:
        input_video (str | Path): Path to the source video file to extract audio from.
        intervals (list): list of [start, stop] second interval lists.
        output_dir (str | Path): Path to the directory for extracted audio.
    """
    for i, interval in enumerate(intervals):
        audio_file = Path(output_dir) / f"audio_{i}.wav"
        print(f"Extracting audio segment {i+1}: {audio_file}")

        start, end = interval[0], interval[1]
        extract_audio_dialogue_file(input_video, audio_file, start, end)

def mute_filter(s: dict[str, float]) -> str:
    """
    Creates an ffmpeg mute filter command for a segment of time.

    Returns: str filter command for the given segment.

    Args:
        s (dict): contains 'start' and 'end' keys both containing float seconds.
    """
    return f"volume=enable='between(t,{s['start']}, {s['end']})':volume=0"

def export_cleaned_video(
    input_video: str | Path,
    mute_segments: dict[str, float],
    lang: str,
    embed_subs: str | Path=None
) -> None:
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

    path = Path(input_video)
    output_video = path.parent.resolve() / f"{path.stem}-cleaned{path.suffix}"
    
    print(f"Exporting: {output_video}")

    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(input_video)]

    if embed_subs is not None:
        cmd.extend(['-i', str(embed_subs)])
    
    cmd.extend([
        "-map", "0:v:0",
        "-map", "0:a:0",
    ])

    if embed_subs is not None:
        cmd.extend([
            "-map", "1:0",      # Map clean subs first
            #"-map", "0:s?",     # Map all existing subs
        ])
    else:
        # If no new subs, just keep original ones
        cmd.extend(["-map", "0:s:?"])
    
    cmd.extend([
        "-c:v", "copy",
        "-c:a", audio_info['codec_name'],
        "-ac", audio_info['channels'],
        "-b:a", audio_info['bit_rate'],
    ])

    if embed_subs is not None:
        cmd.extend([
            "-c:s", "copy",
            "-c:s:0", "srt",
            "-metadata:s:s:0", f"language={lang}",
            "-metadata:s:s:0", f"title=Cleaned {lang}",
            "-disposition:s:0", "default",
            "-disposition:s:1", "0",
        ])
    
    cmd.extend(["-filter:a:0", audio_filter, str(output_video)])

    subprocess.run(cmd, check=True)
    print("\u2714 Successfully sanitized. This video is now safe for Sunday School!")

def write_edl_file(mute_segments: dict[str, float], output_edl: str | Path) -> None:
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