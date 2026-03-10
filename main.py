import config
import utils.search as search
import utils.sub_helper as subs
import utils.ffmpeg_helper as ffmpeg
import utils.swears_parser as swears
import utils.whisper_helper as whisper

def main():
    swears_list = swears.parse_swears_list(config.SWEARS_FILE)
    subs.extract_embedded_subs("example.mkv", "output.srt")

    srt_swear_intervals = subs.find_swear_intervals("output.srt", swears_list)
    swear_intervals = subs.srt_time_interval_to_seconds(srt_swear_intervals)

    swear_intervals = ffmpeg.extract_audio_segments("example.mkv", swear_intervals)

    model = whisper.load_model(config.WHISPER_MODEL, config.WHISPER_DEVICE)
    whisper.transcribe_swear_audio_segments(swear_intervals, model, swears_list)

if __name__ == "__main__":
    main()

#extract_center_channel("example.mkv", "dialogue.wav")
#detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_whisper_swear_ts(transcript, swears_list))


#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)