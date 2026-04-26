def parse_swears_list(input_file: str):
    """
    Takes a swears.txt file, where each swear word is seperated by a new line.
    Profanity can have the "|" next to it, which offers a replacement word.
    This word will be used in the subtitles, taking place of the swear word.

    Returns: list of strings containing each swear word found in the file.

    Args:
        input_file (str | Path): str to the path of the swears.txt file.
    """
    swears_list = []
    with open(str(input_file), "r") as f:
        items = [line.strip().split("|") for line in f if line.strip()]
        return {parts[0]: (parts[1] if len(parts) > 1 else "****") for parts in items}
    return swears_list