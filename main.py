import config
import utils.search as search
import utils.sub_helper as subs
import utils.ffmpeg_helper as ffmpeg
import utils.whisper_helper as whisper

def parse_swears_list(input_file):
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list

swears_list = parse_swears_list(config.SWEARS_FILE)
subs.extract_embedded_subs("example.mkv", "output.srt")

srt_swear_intervals = subs.find_swear_intervals("output.srt", swears_list)
swear_intervals = subs.srt_time_interval_to_seconds(srt_swear_intervals)

audio_i = 0
for interval in swear_intervals:
    ffmpeg.extract_audio_dialogue_file("example.mkv", "audio_" + str(audio_i) + ".wav", interval[0], interval[1])
    audio_i += 1

#extract_center_channel("example.mkv", "dialogue.wav")
#detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_whisper_swear_ts(transcript, swears_list))


#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)