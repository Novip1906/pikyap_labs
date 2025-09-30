import aiohttp
from typing import Optional
from .config import ISS_BASE
import logging

logger = logging.getLogger(__name__)

async def fetch_price_from_moex(symbol: str, session: aiohttp.ClientSession) -> Optional[float]:
    """
    Пытаемся получить последнюю цену тикера symbol с MOEX ISS.
    Возвращает float (price) или None, если не удалось.
    """
    endpoints = [
        f"{ISS_BASE}/engines/stock/markets/shares/boards/TQBR/securities/{symbol}.json?iss.only=marketdata,securities",
        f"{ISS_BASE}/engines/stock/markets/shares/securities/{symbol}.json?iss.only=marketdata,securities",
        f"{ISS_BASE}/securities/{symbol}.json?iss.only=securities",
    ]
    for url in endpoints:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    continue
                j = await resp.json()
                for table_name in ("marketdata", "securities"):
                    if table_name not in j:
                        continue
                    table = j.get(table_name)
                    cols = table.get("columns", [])
                    data = table.get("data", [])
                    if not cols or not data:
                        continue
                    row = data[0]
                    candidates = ["LAST", "LASTVALUE", "PRICE", "CLOSE", "PREVPRICE"]
                    for cand in candidates:
                        if cand in cols:
                            idx = cols.index(cand)
                            try:
                                val = row[idx]
                                if val is None:
                                    continue
                                return float(val)
                            except Exception:
                                continue
        except Exception as e:
            logger.debug(f"Ошибка при запросе {url}: {e}")
            continue
    return None