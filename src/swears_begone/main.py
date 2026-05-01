"""
Main entry point for the 'swears-begone' command.
"""
import tempfile
import shutil
from pathlib import Path

from swears_begone import ffmpeg_helper as ffmpeg
from swears_begone import sub_helper as subs
from swears_begone.swears_parser import parse_swears_list

def main(
    input_video: str,
    model: str,
    device: str,
    lang: str,
    swears_file: str,
    sub_file: str,
    subs_channel: int,
    export_edl: bool
) -> None:
    from swears_begone import whisper_helper as whisper

    tmp = Path(tempfile.mkdtemp())
    output_srt = tmp / f"{Path(input_video).stem}.srt"
    if sub_file != None:
        # Detect swears in external SRT file
        output_srt = Path(sub_file)
        print(f"Using external SRT file: {output_srt}")
    else:
        # Detect swears in embedded subtitles
        channel = subs.extract_embedded_subs(input_video, output_srt, lang, subs_channel)
        if channel == -1:
            print("Attempting to download subtitles from online...")
            output_srt = subs.download_subtitle(input_video, lang)

    # Parsing subtitle segments where swearing is present
    swears_dict = parse_swears_list(swears_file)
    swears_list = list(swears_dict)

    srt_swear_intervals = subs.find_swear_intervals(output_srt, swears_list)
    if len(srt_swear_intervals) == 0:
        raise RuntimeError("Embedded subtitles contains no profanity.")
    
    swear_intervals = subs.parse_srt_time(srt_swear_intervals, padding=3)

    # Save each audio segment
    ffmpeg.extract_audio_segments(input_video, swear_intervals, tmp)

    # Whisper identifies word-level timestamps for profanity
    model = whisper.load_model(model, device)
    mute_segments = whisper.transcribe_swear_audio_segments(model, swear_intervals, swears_list, lang, tmp)

    # Clean subtitles
    clean_subs_file = Path(tmp) / f"{lang}.srt"
    subs.clean_subtitles(output_srt, swears_dict, clean_subs_file)

    # Generate EDL (Edit Decision List) file
    if export_edl:
        edl_file = f"{Path(input_video).stem}.edl"
        write_edl_file(mute_segments, edl_file)
    
    ffmpeg.export_cleaned_video(input_video, mute_segments, lang, embed_subs=clean_subs_file)
    
    shutil.rmtree(tmp)