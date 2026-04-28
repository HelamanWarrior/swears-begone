from pathlib import Path
from importlib import resources

def parse_swears_list(input_file: str) -> dict[str, str]:
    """
    Parses a swear word mapping from a file. 
    Format: 'word|replacement' or just 'word' (defaults to ****).
    """
    if input_file:
        # User specified custom swears.txt
        file_path = Path(input_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Custom swears file not found at: {input_file}")
        cm = file_path.open('r', encoding="utf-8")
    else:
        # Default to bundled package resource swears.txt
        cm = resources.files("swears_begone.data").joinpath("swears.txt").open('r', encoding="utf-8")
    
    with cm as f:
        swears = {}
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("|", 1)
            word = parts[0].strip()
            replacement = parts[1].strip() if len(parts) > 1 else "****"

            swears[word] = replacement
        
        return swears