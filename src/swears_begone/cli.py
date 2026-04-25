import argparse

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
        help=f'default language for extracting srt and swears detection (default is "{config.LANGUAGE}")',
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
        '-s',
        '--sub_channel',
        default=config.TARGET_SUB_CHANNEL,
        help='specify a specific subtitle channel index to clean',
        dest='sub_channel',
        type=int,
        metavar="<sub channel>"
    )
    parser.add_argument(
        '--cpu', 
        default=config.WHISPER_DEVICE, 
        help='force Whisper to use the CPU backend device', 
        dest='cpu', 
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
        device=args.cpu,
        lang=args.lang,
        swears_file=args.swears,
        subs_channel=args.sub_channel,
        export_edl=args.edl
    )

if __name__ == "__main__":
    main()