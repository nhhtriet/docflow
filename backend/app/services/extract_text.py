import io
import os
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF
import cv2
import numpy as np
import pytesseract
from PIL import Image


OCR_LANG = os.getenv("OCR_LANG", "vie+eng")


def _preprocess_image(image: Image.Image) -> np.ndarray:
    """Preprocess PIL image using OpenCV for better OCR."""
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    # Binarize using Otsu's threshold
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Deskew
    coords = np.column_stack(np.where(th > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = th.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    deskewed = cv2.warpAffine(th, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Denoise
    denoise = cv2.medianBlur(deskewed, 3)
    return denoise


def extract_text(
    conn,
    doc_id: int,
    pdf_path: Path,
    thumbnail_dir: Optional[Path] = None,
) -> None:
    """Extract text per page from PDF and store in database.

    If a text layer exists, use it directly. Otherwise perform OCR with
    Tesseract (Vietnamese + English) and OpenCV preprocessing.
    Also generates a thumbnail (PNG) for page 1.
    """
    pdf_path = Path(pdf_path)
    if thumbnail_dir is None:
        thumbnail_dir = Path("thumbnails")
    else:
        thumbnail_dir = Path(thumbnail_dir)
    thumbnail_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    # Generate thumbnail for first page
    first_pix = doc[0].get_pixmap()
    thumb_path = thumbnail_dir / f"{doc_id}.png"
    first_pix.save(thumb_path)

    # Remove existing records for doc_id
    conn.execute("DELETE FROM doc_text WHERE doc_id=?", (doc_id,))
    conn.execute("DELETE FROM fts_doc_text WHERE doc_id=?", (doc_id,))

    for page_no, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if not text:
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_bytes))
            processed = _preprocess_image(image)
            pil_img = Image.fromarray(processed)
            text = pytesseract.image_to_string(pil_img, lang=OCR_LANG)
        conn.execute(
            "INSERT OR REPLACE INTO doc_text (doc_id, page_no, text) VALUES (?, ?, ?)",
            (doc_id, page_no, text),
        )
        conn.execute(
            "INSERT INTO fts_doc_text (doc_id, page_no, text) VALUES (?, ?, ?)",
            (doc_id, page_no, text),
        )
    conn.commit()

    return thumb_path
