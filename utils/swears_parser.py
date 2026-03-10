def parse_swears_list(input_file):
    """
    Takes a swears.txt file, where each swear word is seperated by a new line.
    Profanity can have the "|" next to it, which offers a replacement word.
    This word will be used in replacement of the profanity, in the subtitles.

    Returns a list of strings containing each swear word found in the file.
    """
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list