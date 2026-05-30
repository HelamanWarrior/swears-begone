from pathlib import Path
import whisperx as whisper
from swears_begone.search import contains_any

def load_model(model: str, device = None):
    """
    Loads Whisper model into memory, ready for action!

    Args:
        model: Whisper model to use. (e.g., 'tiny', 'medium.en', 'large-v3', ...)
        device: Hardware device to run model on. ('cpu', 'cuda')
    """
    vad_options = {
        "vad_onset": 0.3,   # Lower = triggers speech detection easier
        "vad_offset": 0.3   # Lower = holds onto the speech window longer before cutting
    }

    return whisper.load_model(model,
        device=device,
        compute_type="float16",
        vad_options=vad_options,
        asr_options={"condition_on_previous_text": False}
    )

def transcribe_wordlevel_audio(
    audio_file: str | Path,
    model,
    lang: str,
    device = None,
    batch_size: int = 16
) -> dict:
    """
    Uses Whisper to transcribe word-level audio of a preferred language.

    Args:
        audio_file: Path to audio file to transcribe.
        model: Loaded Whisper model object
    """

    audio = whisper.load_audio(str(audio_file))
    result = model.transcribe(audio, batch_size=batch_size)

    # Align whisper timestamps
    model_a, metadata = whisper.load_align_model(language_code=lang[:-1], device=device)
    result = whisper.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

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
        model: Loaded Whisper model object.
        segments: A list of [start, end] timestamps in seconds.
        swears_list: list of strings to identify word-level timestamps for.
        lang: Language code (e.g., 'eng')
        audio_dir (str | Path): Directory containing the source audio files.

    Returns: 
        A list of dictionaries, [{word, start, end, confidence}, ...]
    """
    all_detected_swears = []

    for i, segment in enumerate(segments):
        audio_file = audio_dir / f"audio_{i}.wav"
        start_offset = segment[0]
        print(f"Transcribing {audio_file}...")

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
    transcript: dict,
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
        A list of dictionaries [{word, start, end, score}, ...]
    """
    word_timestamps = []

    for segment in transcript["segments"]:
        for word in segment.get("words", []):
            if not contains_any(word["word"], swears_list):
                continue
            word_timestamps.append({
                "word": word["word"],
                "start": float(word["start"]) - padding[0],
                "end": float(word["end"]) + padding[1],
                "score": word["score"]
            })
    
    return word_timestamps
