from config import LANGUAGE, WHISPER_MODEL
import whisper_timestamped as whisper
import utils.search as search

def load_model(model, device=None):
    """
    Loads Whisper model into memory, ready for action!

    Args:
        model: str of the whisper model to use. ('tiny', 'medium.en', 'large-v2', ...)
        device: str of the hardware device to run model on. ('cpu', 'cuda')
            If None, use CUDA if available, otherwise CPU.
    """
    return whisper.load_model(model, device=device)

def transcribe_wordlevel_audio(audio_file, model):
    """
    Uses Whisper to transcribe word-level audio of a perferred language.

    Args:
        audio_file: str path to audio file to transcribe.
        model: loaded Whisper model object
    """
    audio = whisper.load_audio(audio_file)
    result = whisper.transcribe(model, audio, beam_size=5, best_of=5, temperature=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), language=LANGUAGE[:-1])
    return result

def transcribe_swear_audio_segments(segments, model, swears_list):
    """
    Transcribes all the extracted audio files to find the word-level timestamps
    for any word contained in the swears_list.

    Returns: a list of dictionaries, [{word, start, end, confidence}, ...]
    
    Args:
        segments: list of timecode pairs, each are float intervals in seconds.
        model: loaded Whisper model object.
        swears_list: list of strings to identify word-level timestamps for.
    """
    all_detected_swears = []

    for i, segment in enumerate(segments):
        audio_file = f"audio_{i}.wav"
        start_offset = segment[0]

        raw_data = transcribe_wordlevel_audio(audio_file, model)
        word_timestamps = parse_whisper_swear_timestamps(raw_data, swears_list)

        for entry in word_timestamps:
            entry['start'] += start_offset
            entry['end'] += start_offset

        all_detected_swears.extend(word_timestamps)
    print(f"Identified {len(all_detected_swears)} swears timestamps!")
    return all_detected_swears

def parse_whisper_swear_timestamps(transcription_json, swears_list):
    """
    Looks at a whisper word-level audio transcript and filters it only to the 
    words contained in the swears_list.

    Returns: a list of dictionaries [{word, start, end, confidence}, ...]

    Args:
        transcription_json: json output from whisper's wordlevel audio transcription.
        swears_list: list of strings to identify word-level timestamps for.
    """
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