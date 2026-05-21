# ============================================================
#  AVBOB Lead Assistant — database.py
#  SQLite with stdlib sqlite3 (zero extra dependencies)
# ============================================================
import sqlite3
import os
from datetime import datetime
from typing   import List, Optional, Dict, Any

DB_PATH = os.getenv("DB_PATH", "avbob_leads.db")


# ── Schema ──────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT,
    post_text    TEXT    NOT NULL,
    post_url     TEXT    NOT NULL DEFAULT '',
    lead_score   INTEGER NOT NULL DEFAULT 0,
    intent_level TEXT    NOT NULL DEFAULT 'low',
    status       TEXT    NOT NULL DEFAULT 'new',
    language     TEXT    NOT NULL DEFAULT 'en',
    created_at   TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_leads_status    ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_score     ON leads(lead_score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_created   ON leads(created_at DESC);
"""


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(SCHEMA)
    print(f"✅  Database ready: {DB_PATH}")


# ── CRUD ────────────────────────────────────────────────────────
def insert_lead(
    name:         Optional[str],
    post_text:    str,
    post_url:     str,
    lead_score:   int,
    intent_level: str,
    language:     str = "en",
) -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO leads
               (name, post_text, post_url, lead_score, intent_level, status, language, created_at)
               VALUES (?, ?, ?, ?, ?, 'new', ?, ?)""",
            (name, post_text, post_url, lead_score, intent_level, language, now),
        )
        conn.commit()
        return get_lead_by_id(cur.lastrowid)


def get_lead_by_id(lead_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
        return dict(row) if row else None


def get_all_leads(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM leads ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]


def update_lead_status(lead_id: int, status: str) -> bool:
    with get_conn() as conn:
        affected = conn.execute(
            "UPDATE leads SET status = ? WHERE id = ?", (status, lead_id)
        ).rowcount
        conn.commit()
        return affected > 0


def get_stats() -> Dict[str, Any]:
    with get_conn() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*)                                       AS total,
                SUM(status = 'new')                            AS new,
                SUM(status = 'contacted')                      AS contacted,
                SUM(status = 'follow-up')                      AS follow_up,
                SUM(status = 'converted')                      AS converted,
                ROUND(AVG(CAST(lead_score AS REAL)), 1)        AS avg_score
            FROM leads
        """).fetchone()
        return dict(row) if row else {}


def lead_exists(post_text: str) -> bool:
    """Prevent exact duplicate leads."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM leads WHERE post_text = ? LIMIT 1", (post_text,)
        ).fetchone()
        return row is not None
