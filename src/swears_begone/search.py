import re

CLEAN_WORD_RE = re.compile(r'<[^>]+>|[^\w\s\-]')

def _extract_clean_words(text: str) -> list[str]:
    """Helper to strip tags/punctuation and split a string into lowercase words."""
    cleaned = CLEAN_WORD_RE.sub('', text).lower()
    return cleaned.split()

def contains_any(text: str, items: list[str]) -> bool:
    """
    Determines whether any item in a list is found in a text string.

    Args:
        text: A string.
        items: A list of strings.

    Returns:
        True if any item is found within the text, False otherwise.
    """
    words_in_text = _extract_clean_words(text)

    for word in words_in_text:
        if word in items:
            return True
    
    return False

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

    tokens = text.split(' ')
    sorted_keys = sorted(substitutions.keys(), key=len, reverse=True)

    for i, token in enumerate(tokens):
        clean_word = CLEAN_WORD_RE.sub('', token).lower()

        for key in sorted_keys: 
            if key in clean_word:
                replacement = substitutions[key] if substitutions[key] else default

                pattern = re.compile(re.escape(key), re.IGNORECASE)
                tokens[i] = pattern.sub(replacement, token)
                break
    
    return ' '.join(tokens)