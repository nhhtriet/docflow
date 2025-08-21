import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT_DIR / "migrations"


def get_connection(db_path: str):
    """Return a SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection):
    """Initialize database using migration SQL."""
    sql_file = MIGRATIONS_DIR / "001_create_doc_text.sql"
    with open(sql_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
