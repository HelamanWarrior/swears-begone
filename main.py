import argparse
import config
import utils.search as search
import utils.sub_helper as subs
import utils.file_helper as files
import utils.ffmpeg_helper as ffmpeg
import utils.swears_parser as swears
import utils.whisper_helper as whisper

def subs_approach(input_video, output_srt, tmp_dir):    
    # Parsing subtitle segments where swearing is presents
    swears_dict = swears.parse_swears_list(config.SWEARS_FILE)
    swears_list = list(swears_dict)

    srt_swear_intervals = subs.find_swear_intervals(output_srt, swears_list)
    if len(srt_swear_intervals) == 0:
        raise RuntimeError("Embedded subtitles contains no profanity.")
    
    swear_intervals = subs.srt_time_interval_to_seconds(srt_swear_intervals)

    # Save each audio segment
    ffmpeg.extract_audio_segments(input_video, swear_intervals, tmp_dir)

    # Whisper identifies word-level timestamps for profanity
    model = whisper.load_model(config.WHISPER_MODEL)
    mute_segments = whisper.transcribe_swear_audio_segments(model, swear_intervals, swears_list, tmp_dir)

    # Clean subtitles
    clean_subs_file = files.dir_filepath(tmp_dir, f"{config.LANGUAGE}.srt")
    subs.clean_subtitles(output_srt, swears_dict, clean_subs_file)

    # Generate EDL (Edit Decision List) file
    if config.CREATE_EDL:
        edl_file = files.update_file_ext(input_video, ".edl")
        ffmpeg.write_edl_file(mute_segments, edl_file)
    
    ffmpeg.export_cleaned_video(input_video, mute_segments, clean_subs_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='input video file', metavar='<input video>')
    parser.add_argument(
        '-m',
        '--model',
        help=f'whisper model to use for word-level transcription and detection (default is "{config.WHISPER_MODEL}")',
        default=config.WHISPER_MODEL,
        metavar='<model>'
    )
    parser.add_argument(
        '-l',
        '--lang',
        help=f'default language for extracting srt and swears detection (default is "{config.LANGUAGE}")',
        default=config.LANGUAGE,
        metavar='<language>'
    )
    parser.add_argument(
        '--edl',
        help='generate MPlayer EDL file with mute actions',
        dest='edl',
        action='store_true'
    )
    parser.add_argument(
        '-w',
        '--swears',
        help='text file containing profanity (with optional mapping)',
        default=config.SWEARS_FILE,
        metavar='<profanity file>'
    )
    args = parser.parse_args()

    input_video = args.input
    config.LANGUAGE = args.lang
    config.WHISPER_MODEL = args.model
    config.SWEARS_FILE = args.swears
    if args.edl:
        config.CREATE_EDL = True

    tmp_dir = files.tmp_dir()
    
    try:
        output_srt = tmp_dir / files.update_file_ext(input_video, ".srt")

        channel = subs.extract_embedded_subs(input_video, output_srt)

        if channel == -1:
            raise RuntimeError("No compatible subtitles found.")
        
        subs_approach(input_video, output_srt, tmp_dir)
    except Exception as e:
        print(f"Skipping subtitle approach: {e}")
    
    files.rm_tmp(tmp_dir)

if __name__ == "__main__":
    main()