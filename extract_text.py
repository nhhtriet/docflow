"""Utilities for extracting text from PDF files.

This module uses PyMuPDF to extract embedded text. For pages where
text is not available (e.g., scanned documents), it renders the page to
an image and applies Tesseract OCR (Vietnamese + English) after a simple
OpenCV preprocessing step.

The main entry point is :func:`extract_text_from_pdf`.
"""

from __future__ import annotations

from pathlib import Path

import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract


def _preprocess_image(image: np.ndarray) -> np.ndarray:
    """Simple preprocessing to improve OCR accuracy.

    The function converts the image to grayscale and applies a binary
    threshold. The parameters are intentionally conservative so that the
    function works well on a variety of documents without requiring
    caller-specific tuning.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    return thresh


def _ocr_image(image: np.ndarray) -> str:
    """Run Tesseract OCR on an image using both Vietnamese and English."""
    processed = _preprocess_image(image)
    return pytesseract.image_to_string(processed, lang="vie+eng")


def extract_text_from_page(page: fitz.Page) -> str:
    """Extract text from a single PyMuPDF page.

    If the page contains embedded text, this text is returned. Otherwise the
    page is rasterised and OCR is applied.
    """
    text = page.get_text().strip()
    if text:
        return text

    pix = page.get_pixmap(dpi=300)
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        (pix.height, pix.width, pix.n)
    )
    if pix.n == 4:  # RGBA -> RGB
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
    return _ocr_image(image)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract concatenated text from all pages of a PDF file.

    Parameters
    ----------
    pdf_path:
        Path to the PDF file to be processed.

    Returns
    -------
    str
        Concatenated text from all pages.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)

    text_chunks: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text_chunks.append(extract_text_from_page(page))
    return "\n\n".join(text_chunks)


__all__ = ["extract_text_from_pdf", "extract_text_from_page"]
