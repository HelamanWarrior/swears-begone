from pathlib import Path
from faster_whisper import WhisperModel
from swears_begone.search import contains_any

def load_model(model: str, device = None) -> WhisperModel:
    """
    Loads Whisper model into memory, ready for action!

    Args:
        model: Whisper model to use. (e.g., 'tiny', 'medium.en', 'large-v3', ...)
        device: Hardware device to run model on. ('cpu', 'cuda')
    """
    return WhisperModel(model, device=device, compute_type="float16")

def transcribe_wordlevel_audio(
    audio_file: str | Path,
    model: WhisperModel,
    lang: str,
    device = None,
    batch_size: int = 16
) -> tuple:
    """
    Uses Whisper to transcribe word-level audio of a preferred language.

    Args:
        audio_file: Path to audio file to transcribe.
        model: Loaded Whisper model object
    """
    result, _info = model.transcribe(
        str(audio_file), 
        word_timestamps=True, 
        language=lang[:-1],
        condition_on_previous_text=False,
        initial_prompt="Damn, it's hot out here. Go to hell! Get this piece of shit moving, fuck!"
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

    Args:
        model: Loaded WhisperModel object.
        segments: A list of [start, end] timestamps in seconds.
        swears_list: list of strings to identify word-level timestamps for.
        lang: Language code (e.g., 'eng')
        audio_dir (str | Path): Directory containing the source audio files.

    Returns: 
        A list of dictionaries, [{word, start, end}, ...]
    """
    all_detected_swears = []

    print("Transcription & Verification:")

    for i, segment in enumerate(segments):
        audio_file = audio_dir / f"audio_{i}.wav"
        start_offset = segment[0]
        print(f"  • [{start_offset} -> {segment[1]}]", end='')

        raw_data = transcribe_wordlevel_audio(audio_file, model, lang)
        word_timestamps = parse_whisper_swear_timestamps(raw_data, swears_list)

        # Aligns Whisper's segment-relative timestamps with the global video timeline
        # by applying the segment's start offset.
        for entry in word_timestamps:
            for key in ('start', 'end'):
                entry[key] = round(entry[key] + start_offset, 3)

        all_detected_swears.extend(word_timestamps)
    
    print(f"Identified {len(all_detected_swears)} swears timestamps!")
    return all_detected_swears

def parse_whisper_swear_timestamps(
    raw_data,
    swears_list: list[str],
    padding: tuple = (0.05, 0.08)
) -> list[dict]:
    """
    Looks at a whisper word-level audio transcript and filters it only to the 
    words contained in the swears_list.

    Args:
        transcript: Json output from Whisper's wordlevel audio transcription.
        swears_list: A list of strings to identify word-level timestamps for.
    
    Returns: 
        A list of dictionaries [{word, start, end}, ...]
    """
    word_timestamps = []
    segments = list(raw_data)

    for segment in segments:
        if not getattr(segment, "words", None):
            continue

        for word in segment.words:
            if not contains_any(word.word, swears_list):
                print('.', end='')
                continue

            word_timestamps.append({
                "word": word.word,
                "start": float(word.start) - padding[0],
                "end": float(word.end) + padding[1]
            })
            print('x', end="")
    
    print()
    return word_timestamps
