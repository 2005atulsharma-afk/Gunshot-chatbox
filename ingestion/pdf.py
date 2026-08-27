import fitz


def extract_pdf(path):
    """
    Extract text page-by-page from a PDF.
    """

    results = []

    pdf = fitz.open(path)

    try:

        for page_number, page in enumerate(pdf):

            text = page.get_text().strip()

            if not text:
                continue

            results.append(
                {
                    "text": text,
                    "page": page_number + 1,
                    "location": f"Page {page_number + 1}",
                }
            )

    finally:

        pdf.close()

    return results