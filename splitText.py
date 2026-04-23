def split_text(text, max_length=200):
    sentences = text.split("\n")
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_length:
            current += " " + sentence
        else:
            chunks.append(current)
            current = sentence

    chunks.append(current)
    return chunks