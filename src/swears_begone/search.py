import re

def contains_any(text: str, items: list[str]) -> bool:
    """
    Determines whether any item in a list is found in a text string.

    Args:
        text: A string.
        items: A list of strings.

    Returns:
        True if any item is found within the text, False otherwise.
    """
    pattern = r'\b(' + '|'.join(re.escape(item) for item in items) + r')\b'
    return re.search(pattern, text, re.IGNORECASE) is not None

def replace_with_mapping(
    text: str,
    substitutions: dict[str, str],
    default: str = ""
) -> str:
    """
    Replaces occurrences of keys in 'substitutions' with their corresponding values.

    Args:
        textinput text to match with replacement.
        substitutions: A dictionary where each key (str) found in the text, 
            is substituted with the corresponding key value.
        default: Str to substitute if no value is assigned to key.

    Returns: 
        A string with substituted text applied.
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