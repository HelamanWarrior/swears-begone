import config
import utils.search as search
import utils.sub_helper as subs
import utils.ffmpeg_helper as ffmpeg
import utils.swears_parser as swears
import utils.whisper_helper as whisper

def main():
    input_video = "full-example.mkv"
    output_srt = "output.srt"

    swears_list = swears.parse_swears_list(config.SWEARS_FILE)
    subs.extract_embedded_subs(input_video, output_srt)

    srt_swear_intervals = subs.find_swear_intervals(output_srt, swears_list)
    swear_intervals = subs.srt_time_interval_to_seconds(srt_swear_intervals)

    ffmpeg.extract_audio_segments(input_video, swear_intervals)

    model = whisper.load_model(config.WHISPER_MODEL)
    mute_segments = whisper.transcribe_swear_audio_segments(model, swear_intervals, swears_list)

    if config.CREATE_EDL:
        ffmpeg.write_edl_file(mute_segments, input_video + ".edl")
    
    ffmpeg.export_cleaned_video(input_video, mute_segments)
if __name__ == "__main__":
    main()