from config import LANGUAGE, WHISPER_MODEL
import whisper_timestamped as whisper
import utils.search as search

def load_model(model, device):
    return whisper.load_model(model, device=device)

def transcribe_wordlevel_audio(audio_file, model):
    audio = whisper.load_audio(audio_file)
    result = whisper.transcribe(model, audio, language=LANGUAGE[:-1])
    return result

def transcribe_swear_audio_segments(segments, model, swears_list):
    all_detected_swears = []

    for start_offset, _, audio_file in segments:
        raw_data = transcribe_wordlevel_audio(audio_file, model)

        word_timestamps = parse_whisper_swear_timestamps(raw_data, swears_list)

        for entry in word_timestamps:
            entry['start'] += start_offset
            entry['end'] += start_offset
        
        all_detected_swears.extend(word_timestamps)
    print(all_detected_swears)
    return all_detected_swears

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