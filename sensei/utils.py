# This file contains utility functions for the "sensei" layer

import json
import MeCab # For Japanese tokenization

# Initialize MeCab tagger once
_mecab_tagger = MeCab.Tagger("-Owakati") # -Owakati outputs only words separated by spaces

def trim_json_from_text(text: str) -> str:
    """
    Trims LLM-generated text to just the JSON content.
    Assumes the JSON starts at the first '{' or '[' and ends at the last '}' or ']'.

    Args:
        text: The input string potentially containing JSON.

    Returns:
        The extracted JSON string, or an empty string if no JSON is found.
    """
    first_brace = text.find('{')
    first_bracket = text.find('[')

    start_index = -1
    if first_brace != -1 and first_bracket != -1:
        start_index = min(first_brace, first_bracket)
    elif first_brace != -1:
        start_index = first_brace
    elif first_bracket != -1:
        start_index = first_bracket

    if start_index == -1:
        return "" # No starting brace or bracket found

    last_brace = text.rfind('}')
    last_bracket = text.rfind(']')

    end_index = -1
    if last_brace != -1 and last_bracket != -1:
        end_index = max(last_brace, last_bracket)
    elif last_brace != -1:
        end_index = last_brace
    elif last_bracket != -1:
        end_index = last_bracket

    if end_index == -1 or end_index < start_index:
        return "" # No ending brace or bracket found, or ending before start

    return text[start_index:end_index + 1]

def tokenize_japanese_text(text: str) -> list[str]:
    """
    Tokenizes input Japanese text string into words using MeCab.

    Args:
        text: The input Japanese string.

    Returns:
        A list of strings, where each string is a tokenized word.
    """
    # _mecab_tagger was initialized globally at the top of the file
    return _mecab_tagger.parse(text).strip().split()
