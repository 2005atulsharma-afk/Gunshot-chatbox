def extract_txt(path):
    """
    Read a plain text file.
    """

    text = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    if not text.strip():
        return []

    return [
        {
            "text": text,
            "page": None,
            "location": "Text file",
        }
    ]