from pathlib import Path

import whisper_timestamped as whisper
from swears_begone.search import contains_any

def load_model(model: str, device=None) -> whisper.model:
    """
    Loads Whisper model into memory, ready for action!

    Args:
        model: str of the whisper model to use. ('tiny', 'medium.en', 'large-v3', ...)
        device: str of the hardware device to run model on. ('cpu', 'cuda')
            If None, use CUDA if available, otherwise CPU.
    """
    return whisper.load_model(model, device=device)

def transcribe_wordlevel_audio(audio_file: Path, model: whisper.model, lang: str) -> dict:
    """
    Uses Whisper to transcribe word-level audio of a perferred language.

    Args:
        audio_file (str | Path): path to audio file to transcribe.
        model: loaded Whisper model object
    """
    print(f"Transcribing {audio_file}...")

    audio = whisper.load_audio(str(audio_file))
    result = whisper.transcribe(
        model,
        audio,
        beam_size=5,
        temperature=0.0,
        refine_whisper_precision=0.04,
        detect_disfluencies=True,
        language=lang[:-1]
    )
    return result

def transcribe_swear_audio_segments(
    model: str, 
    segments: list[list[float]], 
    swears_list: list[str], 
    lang: str, 
    audio_dir: Path
) -> list[dict]:
    """
    Transcribes all the extracted audio files to find the word-level timestamps
    for any word contained in the swears_list.

    Returns: a list of dictionaries, [{word, start, end, confidence}, ...]
    
    Args:
        segments: list of timecode pairs, each are float intervals in seconds.
        model: loaded Whisper model object.
        swears_list: list of strings to identify word-level timestamps for.
        audio_dir (str | Path): directory to examine audio segments.
    """
    all_detected_swears = []

    for i, segment in enumerate(segments):
        audio_file = audio_dir / f"audio_{i}.wav"
        start_offset = segment[0]

        raw_data = transcribe_wordlevel_audio(audio_file, model, lang)
        word_timestamps = parse_whisper_swear_timestamps(raw_data, swears_list)

        """Aligns Whisper's segment-relative timestamps with the global video timeline
        by applying the segment's start offset."""
        for entry in word_timestamps:
            for key in ('start', 'end'):
                entry[key] = round(entry[key] + start_offset, 3)

        all_detected_swears.extend(word_timestamps)
    print(f"Identified {len(all_detected_swears)} swears timestamps!")
    return all_detected_swears

def parse_whisper_swear_timestamps(
    transcript: dict,
    swears_list: list[str],
    padding: tuple=(0.05, 0.08)
) -> list[dict]:
    """
    Looks at a whisper word-level audio transcript and filters it only to the 
    words contained in the swears_list.

    Returns: a list of dictionaries [{word, start, end, confidence}, ...]

    Args:
        transcript: json output from whisper's wordlevel audio transcription.
        swears_list: list of strings to identify word-level timestamps for.
    """
    word_timestamps = []

    for segment in transcript["segments"]:
        for word in segment.get("words", []):
            if not contains_any(word["text"], swears_list):
                continue
            word_timestamps.append({
                "word": word["text"],
                "start": float(word["start"]) - padding[0],
                "end": float(word["end"]) + padding[1],
                "confidence": word["confidence"]
            })
    
    return word_timestamps
