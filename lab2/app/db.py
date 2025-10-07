import sqlite3
import asyncio
from typing import Optional, List, Tuple
from .config import DB_PATH

def _init_db_sync():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS watches (
            chat_id INTEGER,
            symbol TEXT,
            last_price REAL,
            PRIMARY KEY (chat_id, symbol)
        )
        """
    )
    conn.commit()
    conn.close()

async def init_db():
    await asyncio.to_thread(_init_db_sync)

async def db_execute(query: str, params: tuple = (), fetch: bool = False):
    def _run():
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(query, params)
        result = None
        if fetch:
            result = cur.fetchall()
        conn.commit()
        conn.close()
        return result
    return await asyncio.to_thread(_run)

async def add_watch(chat_id: int, symbol: str, last_price: Optional[float]):
    await db_execute(
        "INSERT OR REPLACE INTO watches(chat_id, symbol, last_price) VALUES (?,?,?)",
        (chat_id, symbol, last_price),
    )

async def remove_watch(chat_id: int, symbol: str) -> bool:
    await db_execute(
        "DELETE FROM watches WHERE chat_id=? AND symbol=?", (chat_id, symbol)
    )
    res = await db_execute(
        "SELECT 1 FROM watches WHERE chat_id=? AND symbol=?", (chat_id, symbol), fetch=True
    )
    return len(res) == 0

async def list_watches(chat_id: int) -> List[Tuple[str, Optional[float]]]:
    res = await db_execute(
        "SELECT symbol, last_price FROM watches WHERE chat_id=? ORDER BY symbol", (chat_id,), fetch=True
    )
    return res or []

async def get_all_tracked_symbols() -> List[str]:
    res = await db_execute("SELECT DISTINCT symbol FROM watches", fetch=True)
    return [r[0] for r in (res or [])]

async def get_chats_for_symbol(symbol: str) -> List[int]:
    res = await db_execute("SELECT chat_id FROM watches WHERE symbol=?", (symbol,), fetch=True)
    return [r[0] for r in (res or [])]

async def update_last_price(chat_id: int, symbol: str, price: Optional[float]):
    await db_execute(
        "UPDATE watches SET last_price=? WHERE chat_id=? AND symbol=?", (price, chat_id, symbol)
    )

async def get_last_price(chat_id: int, symbol: str) -> Optional[float]:
    res = await db_execute("SELECT last_price FROM watches WHERE chat_id=? AND symbol=?", (chat_id, symbol), fetch=True)
    if not res:
        return None
    return res[0][0]