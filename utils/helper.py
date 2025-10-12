from sensei.utils import tokenize_japanese_text

def label_target_words(selected_text: str, selected_word_idxs: list[int]) -> str:
    if not selected_word_idxs:
        return ""
    
    words = tokenize_japanese_text(selected_text)
    
    # Find the min and max index to determine the span to be wrapped
    min_idx = min(selected_word_idxs)
    max_idx = max(selected_word_idxs)

    # Construct the labeled text
    labeled_words = []
    for i, word in enumerate(words):
        if min_idx <= i <= max_idx:
            labeled_words.append(f"<target>{word}</target>")
        else:
            labeled_words.append(word)
            
    # Merge adjacent <target> tags
    result_parts = []
    in_target_block = False
    for part in labeled_words:
        if part.startswith("<target>") and not in_target_block:
            result_parts.append(part)
            in_target_block = True
        elif part.startswith("<target>") and in_target_block:
            result_parts[-1] = result_parts[-1][:-len("</target>")] + part[len("<target>"):]
        elif not part.startswith("<target>") and in_target_block:
            result_parts.append(part)
            in_target_block = False
        else: # not part.startswith("<target>") and not in_target_block
            result_parts.append(part)
            
    return "".join(result_parts)