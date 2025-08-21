"""Utility functions for document processing.

This module includes helpers for extracting text from PDF files, parsing
metadata fields, and generating normalized filenames for storing
processed documents.
"""

from __future__ import annotations

import io
import re
from typing import Any, Dict, Optional

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover - optional dependency
    fitz = None  # type: ignore

try:
    import pdfplumber
except ImportError:  # pragma: no cover - optional dependency
    pdfplumber = None  # type: ignore

try:
    from PIL import Image
    import pytesseract
except ImportError:  # pragma: no cover - optional dependency
    Image = None  # type: ignore
    pytesseract = None  # type: ignore


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file.

    The function first attempts to read the PDF using PyMuPDF or pdfplumber.
    If both methods fail to produce text, it falls back to OCR using
    ``pytesseract``.

    Args:
        pdf_path: Path to the PDF file on disk.

    Returns:
        A string containing the extracted text. An empty string is returned if
        no text could be extracted.
    """

    text = ""

    # Try PyMuPDF first
    if fitz is not None:
        try:  # pragma: no branch
            with fitz.open(pdf_path) as doc:
                text = "\n".join(page.get_text() for page in doc)
        except Exception:
            text = ""

    # Fallback to pdfplumber
    if not text and pdfplumber is not None:
        try:  # pragma: no branch
            with pdfplumber.open(pdf_path) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        except Exception:
            text = ""

    # Final fallback to OCR if available
    if not text and pytesseract is not None and fitz is not None and Image is not None:
        try:  # pragma: no branch
            with fitz.open(pdf_path) as doc:
                parts = []
                for page in doc:
                    pix = page.get_pixmap()
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    parts.append(pytesseract.image_to_string(img))
                text = "\n".join(parts)
        except Exception:
            text = ""

    return text


def parse_metadata(text: str) -> Dict[str, Optional[str]]:
    """Parse basic metadata from extracted text.

    The routine uses simple heuristics and regular expressions to identify
    key fields such as document type, issuer unit, date, and personal data.

    Args:
        text: Text extracted from the document.

    Returns:
        A dictionary with possible keys ``doc_type``, ``issuer_unit``, ``date``,
        ``person_name``, ``person_signer``, ``employee_id`` and ``doc_number``.
        Missing fields will have ``None`` values.
    """

    metadata: Dict[str, Optional[str]] = {
        "doc_type": None,
        "issuer_unit": None,
        "date": None,
        "person_name": None,
        "person_signer": None,
        "employee_id": None,
        "doc_number": None,
    }

    # Document type heuristic
    doc_type_match = re.search(
        r"(certificate|report|contract|agreement|invoice)", text, re.IGNORECASE
    )
    if doc_type_match:
        metadata["doc_type"] = doc_type_match.group(1).lower()

    # Issuer unit
    issuer_match = re.search(
        r"(?:Issuer|Issued by|Department)\s*: \s*(.+)", text, re.IGNORECASE
    )
    if issuer_match:
        metadata["issuer_unit"] = issuer_match.group(1).strip()

    # Date
    date_match = re.search(
        r"(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{2}-\d{2}-\d{4})",
        text,
    )
    if date_match:
        metadata["date"] = date_match.group(1)

    # Person name
    name_match = re.search(
        r"(?:Name|Employee)\s*: \s*([A-Za-z]+(?:\s+[A-Za-z]+)*)", text
    )
    if name_match:
        metadata["person_name"] = name_match.group(1).strip()

    # Signer
    signer_match = re.search(
        r"(?:Signed by|Signer)\s*: \s*([A-Za-z]+(?:\s+[A-Za-z]+)*)", text
    )
    if signer_match:
        metadata["person_signer"] = signer_match.group(1).strip()

    # Employee ID
    emp_match = re.search(r"(?:Employee\s*ID|ID)[:#]?\s*(\w+)", text, re.I)
    if emp_match:
        metadata["employee_id"] = emp_match.group(1)

    # Document number
    doc_no_match = re.search(r"(?:Doc(?:ument)?\s*No\.?|Number)[:#]?\s*(\w+)", text, re.I)
    if doc_no_match:
        metadata["doc_number"] = doc_no_match.group(1)

    return metadata


def _sanitize(part: Optional[str]) -> str:
    """Return a filesystem-friendly version of the provided string."""
    if not part:
        return ""
    part = part.strip().lower()
    return re.sub(r"[^a-z0-9]+", "", part)


def normalize_filename(metadata: Dict[str, Any]) -> str:
    """Create a normalized filename from metadata fields.

    The filename follows the pattern:
    ``employeeid_personname_doccontent_docnumber_issuerunit_date.pdf``
    with all parts lower-cased and stripped of non-alphanumeric characters.

    Args:
        metadata: Dictionary containing metadata fields such as employee ID,
            person name, document type, document number, issuer unit, and date.

    Returns:
        A string representing the filename with a ``.pdf`` suffix.
    """

    parts = [
        _sanitize(metadata.get("employee_id")),
        _sanitize(metadata.get("person_name")),
        _sanitize(metadata.get("doc_type")),
        _sanitize(metadata.get("doc_number")),
        _sanitize(metadata.get("issuer_unit")),
        _sanitize(metadata.get("date")),
    ]

    return "_".join(filter(None, parts)) + ".pdf"

