import config
import utils.sub_helper as subs_helper
import utils.search as search
import whisper_timestamped as whisper

def parse_swears_list(input_file):
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list

def transcribe_wordlevel_audio(audio_file, model):
    audio = whisper.load_audio(audio_file)
    result = whisper.transcribe(model, audio, language=LANGUAGE[:-1])
    return result

def parse_whisper_swear_ts(transcription_json, swears_list):
    word_timestamps = []

    for segment in transcription_json["segments"]:
        for word in segment.get("words", []):
            if not contains_any(word["text"], swears_list):
                continue
            word_timestamps.append({
                "word": word["text"],
                "start": float(word["start"]),
                "end": float(word["end"]),
                "confidence": word["confidence"]
            })
    
    return word_timestamps

swears_list = parse_swears_list(config.SWEARS_FILE)
subs_helper.extract_embedded_subs("example.mkv", "output.srt")
subs_helper.swear_srt_to_seconds(subs_helper.detect_swear_time_in_subs("output.srt", swears_list))

#extract_center_channel("example.mkv", "dialogue.wav")
#detect_audio_codec("example.mkv")

#model = whisper.load_model(WHISPER_MODEL, device=WHISPER_DEVICE)
#transcript = transcribe_wordlevel_audio("dialogue.wav", model)

#print(parse_whisper_swear_ts(transcript, swears_list))


#extract_center_channel("example.mkv", "dialogue.wav")
#help(whisper.transcribe)