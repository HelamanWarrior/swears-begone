def parse_swears_list(input_file):
    swears_list = []
    with open(input_file, "r") as f:
        for line in f:
            swear_array = line.strip().split("|")[0]
            swears_list.append(swear_array)
    return swears_list