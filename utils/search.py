import re

def contains_any(text, items):
    pattern = r'\b(' + '|'.join(re.escape(item) for item in items) + r')\b'
    return re.search(pattern, text, re.IGNORECASE) is not None

def replace_with_mapping(text, substitutions):
    """
    Replaces occurrences of keys in 'substitutions' with their corresponding values.
    """
    if not substitutions:
        return text
    
    # Sort by length (descending) to ensure that whole words are matched and not just partials
    sorted_keys = sorted(substitutions.keys(), key=len, reverse=True)
    pattern = r'\b(' + "|".join(re.escape(key) for key in sorted_keys) + r')\b'

    # Gets the replacement key value to the corresponding swear
    def make_replacement(match):
        swear_word = match.group(0)
        return substitutions.get(swear_word.lower(), "****")
    
    return re.sub(pattern, make_replacement, text, flags=re.IGNORECASE)

def replace_any(text, items, replacement):
    """
    Replaces any occurrences of words in 'items' with 'replacement'.
    Uses word boundaries to ensure partial words aren't replaced.
    """
    if not items:
        return text
    
    pattern = r'\b(' + "|".join(re.escape(item) for item in items) + r')\b'
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)