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

    audio_i = 0
    for interval in swear_intervals:
        audio_file = "audio_" + str(audio_i) + ".wav"
        ffmpeg.extract_audio_dialogue_file("example.mkv", audio_file, interval[0], interval[1])
        swear_intervals[audio_i].append(audio_file)
        audio_i += 1
    print(swear_intervals)

if __name__ == "__main__":
    main()

#extract_center_channel("example.mkv", "dialogue.wav")
#detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_whisper_swear_ts(transcript, swears_list))


#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)