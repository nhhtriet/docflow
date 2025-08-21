import os
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException

from .db import get_connection, init_db

app = FastAPI()

DB_PATH = os.getenv("DATABASE_PATH", str(Path("docflow.db")))


def _get_conn():
    return get_connection(DB_PATH)


# Ensure database exists when application starts
with _get_conn() as conn:
    init_db(conn)


@app.get("/search")
def search(query: str):
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT doc_id, page_no, text FROM fts_doc_text WHERE fts_doc_text MATCH ?",
            (query,),
        ).fetchall()
        return [dict(row) for row in rows]


@app.get("/documents/{doc_id}/text")
def document_text(doc_id: int, page: Optional[int] = None, full: bool = False):
    with _get_conn() as conn:
        if full:
            rows = conn.execute(
                "SELECT text FROM doc_text WHERE doc_id=? ORDER BY page_no",
                (doc_id,),
            ).fetchall()
            if not rows:
                raise HTTPException(status_code=404, detail="Document not found")
            combined = "\n".join(r["text"] for r in rows)
            return {"doc_id": doc_id, "text": combined}
        if page is not None:
            row = conn.execute(
                "SELECT page_no, text FROM doc_text WHERE doc_id=? AND page_no=?",
                (doc_id, page),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Page not found")
            return {"doc_id": doc_id, "page_no": row["page_no"], "text": row["text"]}
        rows = conn.execute(
            "SELECT page_no, text FROM doc_text WHERE doc_id=? ORDER BY page_no",
            (doc_id,),
        ).fetchall()
        return [{"page_no": r["page_no"], "text": r["text"]} for r in rows]
