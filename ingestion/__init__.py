from pathlib import Path

from ingestion.pdf import extract_pdf
from ingestion.txt import extract_txt
from ingestion.docx import extract_docx
from ingestion.spreadsheet import extract_spreadsheet
from ingestion.image import extract_image
from ingestion.video import extract_video
from ingestion.code import extract_code

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    CODE_EXTENSIONS,
)


def chunk_text(
    text,
    chunk_size=CHUNK_SIZE,
    overlap=CHUNK_OVERLAP
):
    """
    Split text into overlapping chunks.

    Used for text-based files and source code.
    """

    words = text.split()

    if not words:
        return []

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        ).strip()

        if chunk:
            chunks.append(chunk)

        start += max(
            1,
            chunk_size - overlap
        )

    return chunks


def chunk_extracted_sections(sections):
    """
    Preserve the source section/page/location
    while creating chunks.
    """

    output = []

    for section in sections:

        text = section.get(
            "text",
            ""
        ).strip()

        if not text:
            continue

        page = section.get(
            "page"
        )

        location = section.get(
            "location",
            ""
        )

        language = section.get(
            "language"
        )

        chunks = chunk_text(text)

        for chunk_number, chunk in enumerate(
            chunks
        ):

            output.append(
                {
                    "text": chunk,
                    "page": page,
                    "location": location,
                    "language": language,
                    "chunk_number": chunk_number,
                }
            )

    return output


def extract_file(path: Path):
    """
    Select the correct extractor based on file type.
    """

    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_pdf(path)

    if extension == ".txt":
        return extract_txt(path)

    if extension == ".docx":
        return extract_docx(path)

    if extension in {
        ".csv",
        ".xlsx",
        ".xls",
    }:
        return extract_spreadsheet(path)

    if extension in {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tiff",
    }:
        return extract_image(path)

    if extension in {
        ".mp4",
        ".mov",
        ".mkv",
        ".wav",
        ".mp3",
    }:
        return extract_video(path)

    if extension in CODE_EXTENSIONS:
        return extract_code(path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )