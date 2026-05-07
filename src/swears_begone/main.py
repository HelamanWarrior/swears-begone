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
    embed_subs: bool,
    export_edl: bool
) -> None:
    from swears_begone import whisper_helper as whisper

    tmp = Path(tempfile.mkdtemp())
    video_name = Path(input_video).stem
    video_dir = Path(input_video).parent.resolve()
    external_subs_path = video_dir / f"{video_name}-cleaned.{lang}.srt"

    source_subs = subs.resolve_subtitle_path(
        input_video=input_video, 
        external_sub=sub_file, 
        target_channel=subs_channel, 
        lang=lang, 
        tmp=tmp
    )

    # Parsing subtitle segments where swearing is present
    swears_dict = parse_swears_list(swears_file)
    swears_list = list(swears_dict)

    srt_swear_intervals = subs.find_swear_intervals(source_subs, swears_list)
    if len(srt_swear_intervals) == 0:
        raise RuntimeError("Embedded subtitles contains no profanity.")
    
    # Save each audio segment
    swear_intervals = subs.parse_srt_time(srt_swear_intervals, padding=3)
    ffmpeg.extract_audio_segments(input_video, swear_intervals, tmp)

    # Whisper identifies word-level timestamps for profanity
    model = whisper.load_model(model, device)
    mute_segments = whisper.transcribe_swear_audio_segments(
        model=model,
        segments=swear_intervals,
        swears_list=swears_list,
        lang=lang,
        audio_dir=tmp
    )

    # Clean subtitles
    clean_subs_file = Path(tmp) / f"{lang}-cleaned.srt"
    subs.clean_subtitles(source_subs, swears_dict, clean_subs_file)

    # --------------USER OPTIONS-------------------------
    ## User chooses if subtitles will be embedded in video
    if embed_subs:
        embed_subs_file = clean_subs_file 
    else:
        shutil.move(clean_subs_file, external_subs_path)
        embed_subs_file = None

    ## Generate EDL (Edit Decision List) file
    if export_edl:
        edl_file = video_dir / f"{video_name}.edl"
        ffmpeg.write_edl_file(mute_segments, edl_file)

        shutil.rmtree(tmp) 
        return
    # ----------------------------------------------------
    
    # Final step! Export the cleaned video file
    ffmpeg.export_cleaned_video(
        input_video=input_video, 
        mute_segments=mute_segments, 
        lang=lang, 
        embed_subs=embed_subs_file
    )
    
    shutil.rmtree(tmp)