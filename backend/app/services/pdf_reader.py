import io

from pypdf import PdfReader

MAX_PAGES = 10
MAX_CHARS = 20000
MIN_CHARS = 30


class PdfReadError(Exception):
    """A problem with the uploaded PDF that the user can understand."""


def extract_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise PdfReadError("This PDF is password protected")
        pages = [(p.extract_text() or "") for p in reader.pages[:MAX_PAGES]]
    except PdfReadError:
        raise
    except Exception:
        raise PdfReadError("Could not read this PDF file")

    text = "\n".join(pages).strip()
    if len(text) < MIN_CHARS:
        raise PdfReadError(
            "No readable text found. Scanned or image-only PDFs are not supported. "
            "Upload a text-based PDF or paste your resume text instead."
        )
    return text[:MAX_CHARS]