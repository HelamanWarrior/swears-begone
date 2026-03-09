import whisper_timestamped as whisper
import utils.search as search

def transcribe_wordlevel_audio(audio_file, model):
    audio = whisper.load_audio(audio_file)
    result = whisper.transcribe(model, audio, language=LANGUAGE[:-1])
    return result

def parse_whisper_swear_timestamps(transcription_json, swears_list):
    word_timestamps = []

    for segment in transcription_json["segments"]:
        for word in segment.get("words", []):
            if not search.contains_any(word["text"], swears_list):
                continue
            word_timestamps.append({
                "word": word["text"],
                "start": float(word["start"]),
                "end": float(word["end"]),
                "confidence": word["confidence"]
            })
    
    return word_timestamps