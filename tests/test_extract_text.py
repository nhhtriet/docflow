import os
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
import pytesseract

from backend.app.db import get_connection, init_db
from backend.app.services.extract_text import extract_text


def create_text_pdf(path: Path, text: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(path)
    doc.close()


def create_image_pdf(path: Path, text: str):
    img = Image.new("RGB", (600, 200), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((10, 80), text, fill="black")
    img.save(path, "PDF")


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    monkeypatch.setenv("OCR_LANG", "vie+eng")
    # Import app after setting env variables
    from backend.app.main import app

    conn = get_connection(str(db_path))
    init_db(conn)
    conn.close()
    client = TestClient(app)
    return client, db_path


def test_pdf_with_text_layer(client, tmp_path):
    client, db_path = client
    conn = get_connection(str(db_path))
    pdf_path = tmp_path / "text.pdf"
    create_text_pdf(pdf_path, "Hello World")
    extract_text(conn, 1, pdf_path, thumbnail_dir=tmp_path)
    conn.close()

    response = client.get("/documents/1/text", params={"full": "true"})
    assert response.status_code == 200
    assert "Hello World" in response.json()["text"]

    page_resp = client.get("/documents/1/text", params={"page": 1})
    assert page_resp.status_code == 200
    assert page_resp.json()["text"].strip().startswith("Hello")

    search_res = client.get("/search", params={"query": "Hello"})
    assert search_res.status_code == 200
    assert any(r["doc_id"] == 1 for r in search_res.json())

    # Thumbnail exists
    thumb_path = tmp_path / "1.png"
    assert thumb_path.exists()


def test_pdf_with_ocr(client, tmp_path):
    try:
        langs = pytesseract.get_languages(config="")
    except pytesseract.TesseractNotFoundError:
        pytest.skip("Tesseract not installed")
    if "vie" not in langs:
        pytest.skip("Vietnamese language not installed")
    client, db_path = client
    conn = get_connection(str(db_path))
    pdf_path = tmp_path / "img.pdf"
    create_image_pdf(pdf_path, "Quyết định")
    extract_text(conn, 2, pdf_path, thumbnail_dir=tmp_path)
    conn.close()

    response = client.get("/documents/2/text", params={"full": "true"})
    assert response.status_code == 200
    assert "Quyết" in response.json()["text"]
