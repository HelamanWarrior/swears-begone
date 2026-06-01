import re

STRIP_TAGS_AND_PUNCT = re.compile(r'<[^>]+>|[^a-zA-Z0-9]')

def _extract_clean_words(text: str) -> list[str]:
    """Helper to strip tags/punctuation and split a string into lowercase words."""
    cleaned = CLEAN_WORD_RE.sub('', text).lower()
    return cleaned.split()

def match_regex(items: list[str]) -> re.compile:
    sorted_items = sorted(items, key=len, reverse=True)
    escaped_items = [re.escape(item) for item in sorted_items]
    match_re = re.compile(rf"\b({'|'.join(escaped_items)})\b", re.IGNORECASE)
    return match_re

def contains_any(text: str, items: list[str]) -> bool:
    """
    Determines whether any item in a list is found in a text string.

    Args:
        text: A string.
        items: A list of strings.

    Returns:
        True if any item is found within the text, False otherwise.
    """
    return bool(match_regex(items).search(text.lower()))

def replace_with_mapping(
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
        return lambda text: text

    pattern = match_regex(substitutions)

    def replace_match(match: re.Match) -> str:
        matched_word = match.group(0).lower()
        replacement = substitutions.get(matched_word)
        return replacement if replacement else default

    return lambda text: pattern.sub(replace_match, text)
