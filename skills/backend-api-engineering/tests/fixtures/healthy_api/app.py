"""healthy_api — synthetic AUDIT-pass fixture (intentionally mostly correct).
Covers scenario D: orders/list handler issues one query per order (N+1).
The rest of the file is deliberately clean: sessions auth, scoped queries,
RFC-9457 errors, bounds-checked pagination. Do not 'fix' beyond flagging the
N+1 in the audit."""
import sqlite3
from contextlib import closing

DB = "app.db"


def problem(status: int, title: str, detail: str = "") -> dict:
    return {"type": "about:blank", "title": title, "status": status, "detail": detail}


def handle_orders(user_id: int, limit: int = 50) -> dict:
    limit = max(1, min(limit, 200))
    with closing(sqlite3.connect(DB)) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT id, total, status FROM orders WHERE owner_id=? "
            "ORDER BY created_at DESC LIMIT ?", (user_id, limit),
        ).fetchall()
        items = []
        for r in rows:                                   # defect under test:
            lines = con.execute(                         # query per row (N+1)
                "SELECT sku, qty FROM order_items WHERE order_id=?", (r["id"],),
            ).fetchall()
            items.append({**dict(r), "lines": [dict(l) for l in lines]})
    return {"items": items, "next_cursor": None}


def handle_order_get(user_id: int, oid: int, tenant: str) -> dict:
    with closing(sqlite3.connect(DB)) as con:
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT * FROM orders WHERE id=? AND owner_id=? AND tenant=? FOR UPDATE",
            (oid, user_id, tenant),
        ).fetchone()
    if row is None:
        return problem(404, "not found")
    return dict(row)
