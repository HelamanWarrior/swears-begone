def parse_swears_list(input_file):
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
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list