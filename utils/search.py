import re

def contains_any(text, items):
    pattern = r'\b(' + '|'.join(re.escape(item) for item in items) + r')\b'
    return re.search(pattern, text, re.IGNORECASE) is not None

def replace_with_mapping(text, substitutions, default=""):
    """
    Replaces occurrences of keys in 'substitutions' with their corresponding values.

    Returns: (str) with substituted text applied.

    Args:
        text (str): input text to match with replacement.
        substitutions (dict): each key (str) found in the text, 
            is substituted with the corresponding key value (str). 
        default (str): str to substitute if no value is assigned to key.
    """
    if not substitutions:
        return text
    
    # Sort by length (descending) to ensure that whole words are matched and not just partials
    sorted_keys = sorted(substitutions.keys(), key=len, reverse=True)
    pattern = r'\b(' + "|".join(re.escape(key) for key in sorted_keys) + r')\b'

    # Gets the replacement key value to the corresponding swear
    def make_replacement(match):
        swear_word = match.group(0)
        return substitutions.get(swear_word.lower(), default)
    
    return re.sub(pattern, make_replacement, text, flags=re.IGNORECASE)