from docx import Document


def extract_docx(path):
    """
    Extract paragraphs from a DOCX document.
    """

    document = Document(path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    if not paragraphs:
        return []

    return [
        {
            "text": "\n".join(paragraphs),
            "page": None,
            "location": "DOCX document",
        }
    ]