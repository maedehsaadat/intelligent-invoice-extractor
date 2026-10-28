import fitz

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract selectable text from a PDF file.

    This works with text-based PDFs. Scanned PDFs may require OCR.
    """
    extracted_pages = []

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            for page in document:
                extracted_pages.append(page.get_text("text"))

    except Exception as exc:
        raise ValueError(
            "Could not read this PDF. Make sure it is a valid PDF file."
        ) from exc

    return "\n".join(extracted_pages).strip()
