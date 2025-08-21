CREATE TABLE IF NOT EXISTS doc_text (
    doc_id INTEGER NOT NULL,
    page_no INTEGER NOT NULL,
    text TEXT,
    PRIMARY KEY (doc_id, page_no)
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_doc_text USING fts5(
    doc_id UNINDEXED,
    page_no UNINDEXED,
    text
);
