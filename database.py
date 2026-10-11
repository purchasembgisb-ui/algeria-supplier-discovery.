import sqlite3
from datetime import datetime, timezone
from pathlib import Path

FIELDS = [
    "company_name", "activity", "wilaya", "phone", "email", "website",
    "social_url", "source_url", "source_name", "evidence", "collected_at",
    "verification_status", "notes"
]

def connect(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    with connect(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT DEFAULT '',
            activity TEXT DEFAULT '',
            wilaya TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            email TEXT DEFAULT '',
            website TEXT DEFAULT '',
            social_url TEXT DEFAULT '',
            source_url TEXT UNIQUE,
            source_name TEXT DEFAULT '',
            evidence TEXT DEFAULT '',
            collected_at TEXT DEFAULT '',
            verification_status TEXT DEFAULT 'Unverified',
            notes TEXT DEFAULT ''
        )
        """)

def upsert_companies(db_path, rows):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with connect(db_path) as conn:
        for row in rows:
            clean = {k: ("" if row.get(k) is None else str(row.get(k, ""))) for k in FIELDS}
            clean["collected_at"] = clean["collected_at"] or now
            clean["verification_status"] = clean["verification_status"] or "Unverified"
            source_url = clean["source_url"].strip()
            if not source_url:
                # Keep records without URLs distinct enough to avoid accidental overwrites.
                source_url = f"no-source:{clean['company_name']}:{clean['website']}"
                clean["source_url"] = source_url
            columns = ", ".join(FIELDS)
            placeholders = ", ".join(["?"] * len(FIELDS))
            updates = ", ".join(f"{f}=excluded.{f}" for f in FIELDS if f != "source_url")
            conn.execute(
                f"INSERT INTO companies ({columns}) VALUES ({placeholders}) "
                f"ON CONFLICT(source_url) DO UPDATE SET {updates}",
                [clean[f] for f in FIELDS]
            )

def list_companies(db_path):
    with connect(db_path) as conn:
        return [dict(r) for r in conn.execute("SELECT * FROM companies ORDER BY collected_at DESC")]

def export_all(db_path):
    return list_companies(db_path)
