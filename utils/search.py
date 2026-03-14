import re

def contains_any(text, items):
    pattern = r'\b(' + '|'.join(re.escape(item) for item in items) + r')\b'
    return re.search(pattern, text, re.IGNORECASE) is not None

def replace_any(text, items, replacement):
    """
    Replaces any occurrences of words in 'items' with 'replacement'.
    Uses word boundaries to ensure partial words aren't replaced.
    """
    if not items:
        return text
    
    pattern = r'\b(' + "|".join(re.escape(item) for item in items) + r')\b'
    return re.sub(pattern, replacement, text, flags=re.IGNORECASE)