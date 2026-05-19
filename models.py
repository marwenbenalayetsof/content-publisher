"""
Database models and initialization
"""

import sqlite3
from config import DATABASE_PATH


def get_db():
    """Get database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Social media accounts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS social_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT UNIQUE NOT NULL,
            access_token TEXT,
            refresh_token TEXT,
            account_name TEXT DEFAULT '',
            account_id TEXT DEFAULT '',
            connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # TTS history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tts_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            voice_name TEXT NOT NULL,
            preset_name TEXT NOT NULL,
            prompt_preview TEXT DEFAULT '',
            file_path TEXT NOT NULL,
            file_size_kb REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Publishing history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publish_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_filename TEXT NOT NULL,
            platforms TEXT NOT NULL,
            results TEXT DEFAULT '{}',
            all_success BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_tts_record(filename, voice_name, preset_name, prompt_preview, file_path, file_size_kb):
    """Save a TTS generation record."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tts_history (filename, voice_name, preset_name, prompt_preview, file_path, file_size_kb)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, voice_name, preset_name, prompt_preview, file_path, file_size_kb))
    conn.commit()
    conn.close()


def get_tts_history(limit=50):
    """Get recent TTS generation history."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM tts_history ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records


def save_publish_record(video_filename, platforms, results, all_success):
    """Save a publishing record."""
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publish_history (video_filename, platforms, results, all_success)
        VALUES (?, ?, ?, ?)
    """, (video_filename, json.dumps(platforms), json.dumps(results), all_success))
    conn.commit()
    conn.close()


def get_publish_history(limit=50):
    """Get recent publishing history."""
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM publish_history ORDER BY created_at DESC LIMIT ?
    """, (limit,))
    records = []
    for row in cursor.fetchall():
        r = dict(row)
        r["platforms"] = json.loads(r["platforms"]) if r["platforms"] else []
        r["results"] = json.loads(r["results"]) if r["results"] else {}
        records.append(r)
    conn.close()
    return records
