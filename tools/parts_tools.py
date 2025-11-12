# tools/parts_tools.py
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import DB_PATH, SQL_DIR

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def low_stock(limit: int = 20) -> List[Dict[str, Any]]:
    sql_path = SQL_DIR / "low_stock.sql"
    q = sql_path.read_text() if sql_path.exists() else """
      SELECT p.sku, p.description, l.code AS location,
             i.on_hand, i.reorder_point, i.safety_stock,
             (i.reorder_point + i.safety_stock) - i.on_hand AS shortage
      FROM inventory i
      JOIN parts p ON p.part_id = i.part_id
      JOIN locations l ON l.location_id = i.location_id
      WHERE i.on_hand < (i.reorder_point + i.safety_stock)
      ORDER BY shortage DESC
      LIMIT ?;
    """
    with _conn() as conn:
        rows = conn.execute(q, (limit,)).fetchall()
        return [dict(r) for r in rows]

def bom_explosion(parent_sku: str, qty: float = 1.0) -> List[Dict[str, Any]]:
    q = (SQL_DIR / "bom_explosion.sql").read_text()
    with _conn() as conn:
        rows = conn.execute(q, {"parent_sku": parent_sku, "qty": qty}).fetchall()
        return [dict(r) for r in rows]

def value_on_hand_main() -> List[Dict[str, Any]]:
    q = (SQL_DIR / "value_on_hand_by_category.sql").read_text()
    with _conn() as conn:
        rows = conn.execute(q).fetchall()
        return [dict(r) for r in rows]
