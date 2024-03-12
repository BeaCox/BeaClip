def shorten_text(text):
    processed_text = text
    text_lines = text.split("\n")
    # at most 4 lines
    if len(text_lines) > 4:
        processed_text = "\n".join(text_lines[:4])
    if len(text) > 50:
            processed_text = text[:50]
    if len(text) > 50 or len(text_lines) > 4:
        processed_text += "..."
    return processed_text
