import config
import utils.sub_helper as subs_helper
import utils.search as search
import utils.whisper_helper as whisper

def parse_swears_list(input_file):
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list

swears_list = parse_swears_list(config.SWEARS_FILE)
subs_helper.extract_embedded_subs("example.mkv", "output.srt")
print(subs_helper.find_swear_intervals("output.srt", swears_list))

#extract_center_channel("example.mkv", "dialogue.wav")
#detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_whisper_swear_ts(transcript, swears_list))


#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)