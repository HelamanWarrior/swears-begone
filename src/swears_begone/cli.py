import argparse
import sys

from swears_begone import config
from swears_begone.main import main as swears_begone

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input',
        required=True,
        help='input video file',
        metavar='<input video>'
    )
    parser.add_argument(
        '-m',
        '--model',
        default=config.WHISPER_MODEL,
        help=f'whisper model to use for word-level transcription and detection (default is "{config.WHISPER_MODEL}")',
        metavar="<model>"
    )
    parser.add_argument(
        '-l',
        '--lang',
        default=config.LANGUAGE,
        help=f'language for extracting srt and swears detection (default is "{config.LANGUAGE}")',
        metavar="<language>"
    )
    parser.add_argument(
        '-w',
        '--swears',
        default=config.SWEARS_FILE,
        help='text file containing profanity (with optional mapping)',
        metavar="<swears.txt>"
    )
    parser.add_argument(
        '-c',
        '--sub_channel',
        default=config.TARGET_SUB_CHANNEL,
        help='specify a subtitle channel index to clean',
        dest='sub_channel',
        type=int,
        metavar="<sub channel>"
    )
    parser.add_argument(
        '-s',
        '--srt_file',
        help='external subtitle SRT file for swears detection',
        dest='sub_file',
        metavar="<sub file>"
    )
    parser.add_argument(
        '-e',
        '--embed-subs',
        default=config.EMBED_SUBS,
        help='embed subtitles in resulting video file',
        dest='embed_subs',
        action='store_true',
    )
    parser.add_argument(
        '--cpu', 
        default=config.WHISPER_DEVICE, 
        help='force Whisper to use the CPU backend device', 
        dest='device', 
        action='store_true'
    )
    parser.add_argument(
        '--edl',
        default=config.CREATE_EDL, 
        help='generate MPlayer EDL file with mute actions',
        dest='edl',
        action='store_true'
    )
    args = parser.parse_args()

    swears_begone(
        input_video=args.input,
        model=args.model,
        device=args.device,
        lang=args.lang,
        swears_file=args.swears,
        sub_file=args.sub_file,
        subs_channel=args.sub_channel,
        embed_subs=args.embed_subs,
        export_edl=args.edl
    )

def print_progress_bar(
    iteration: int,
    total: int,
    prefix: str = '',
    suffix: str = '',
    length: int = 30,
    fill: str = '#'
) -> None:
    """
    Prints a dynamic terminal progress bar on a single line.
    
    Args:
        iteration: Current progress step (int)
        total: Total steps required (int)
        prefix: Text to display before the bar (str)
        suffix: Text to display after the bar (str)
        length: Total character width of the progress bar itself (int)
        fill: The character used to represent progress (str)
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + ' ' * (length - filled_length)

    sys.stdout.write(f'\r • {prefix} [{bar}] {percent}% {suffix}\033[K')
    sys.stdout.flush()

    if iteration == total:
        print()

if __name__ == "__main__":
    main()