"""Utility functions for PDF processing and metadata extraction."""

from __future__ import annotations

from typing import Any, Dict


def read_pdf(path: str) -> str:
    """Read text from a PDF file.

    Args:
        path: Path to the PDF file.

    Returns:
        Extracted text content.
    """
    import PyPDF2

    text: list[str] = []
    with open(path, "rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        for page in reader.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def ocr_image(path: str) -> str:
    """Extract text from an image using OCR.

    Requires :mod:`pytesseract` and :mod:`PIL`.

    Args:
        path: Path to the image file.

    Returns:
        Extracted text content.
    """
    from PIL import Image
    import pytesseract

    image = Image.open(path)
    return pytesseract.image_to_string(image)


def parse_metadata(path: str) -> Dict[str, Any]:
    """Return basic metadata for a file.

    For PDF files, attempts to merge PDF metadata as well.

    Args:
        path: Path to the file.

    Returns:
        A dictionary containing size, created, modified and optionally
        PDF-specific metadata.
    """
    import datetime as _dt
    import os

    stat = os.stat(path)
    metadata: Dict[str, Any] = {
        "size": stat.st_size,
        "created": _dt.datetime.fromtimestamp(stat.st_ctime),
        "modified": _dt.datetime.fromtimestamp(stat.st_mtime),
    }

    if path.lower().endswith(".pdf"):
        try:
            import PyPDF2

            with open(path, "rb") as fh:
                reader = PyPDF2.PdfReader(fh)
                docinfo = reader.metadata or {}
                for key, value in docinfo.items():
                    cleaned_key = key.lstrip("/")
                    metadata[cleaned_key] = value
        except Exception:
            # Ignore PDF metadata parsing errors
            pass

    return metadata


__all__ = ["read_pdf", "ocr_image", "parse_metadata"]

