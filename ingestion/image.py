def extract_image(path):
    """
    Extract text from an image using local OCR.

    Requires:
        pillow
        pytesseract
        Tesseract installed on the Mac
    """

    try:

        from PIL import Image
        import pytesseract

    except ImportError:

        raise RuntimeError(
            "Image OCR requires pillow and pytesseract."
        )

    image = Image.open(path)

    text = pytesseract.image_to_string(
        image
    ).strip()

    if not text:

        return []

    return [
        {
            "text": text,
            "page": None,
            "location": "Image",
        }
    ]