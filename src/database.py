from typing import Optional

import aiosqlite

DB_PATH = "urls.db"

_db: Optional[aiosqlite.Connection] = None


async def get_db() -> aiosqlite.Connection:
    assert _db is not None, "Database not initialized"
    return _db


async def init_db() -> None:
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row
    await _db.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            click_count INTEGER NOT NULL DEFAULT 0
        )
    """)
    await _db.commit()


async def close_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None


async def insert_url(short_code: str, original_url: str) -> dict:
    db = await get_db()
    await db.execute(
        "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
        (short_code, original_url),
    )
    await db.commit()
    cursor = await db.execute(
        "SELECT short_code, original_url, created_at, click_count FROM urls WHERE short_code = ?",
        (short_code,),
    )
    row = await cursor.fetchone()
    return dict(row)


async def get_url_by_code(code: str) -> Optional[dict]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT short_code, original_url, created_at, click_count FROM urls WHERE short_code = ?",
        (code,),
    )
    row = await cursor.fetchone()
    return dict(row) if row else None


async def increment_click_count(code: str) -> None:
    db = await get_db()
    await db.execute(
        "UPDATE urls SET click_count = click_count + 1 WHERE short_code = ?",
        (code,),
    )
    await db.commit()
