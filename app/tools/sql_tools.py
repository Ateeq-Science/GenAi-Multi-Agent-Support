from __future__ import annotations

import json
import re
import sqlite3
from typing import Any

from app.utils.config import DB_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def extract_customer_name(query: str) -> str | None:
    patterns = [
        r"customer\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
        r"for\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)'?s",
        r"overview of\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
        r"profile of\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            return match.group(1).strip()

    words = re.findall(r"\b[A-Z][a-zA-Z]+\b", query)
    if words:
        return " ".join(words[:2]) if len(words) >= 2 else words[0]
    return None


def get_customer_by_name(name: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        row = conn.execute(
            """
            SELECT * FROM customers
            WHERE lower(full_name) LIKE lower(?)
            ORDER BY customer_id ASC
            LIMIT 1
            """,
            (f"%{name}%",),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_tickets_by_customer(customer_id: int) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        rows = conn.execute(
            """
            SELECT * FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
            """,
            (customer_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def build_customer_context_from_query(query: str) -> str:
    name = extract_customer_name(query)
    if not name:
        return "No customer name could be identified from the query."

    customer = get_customer_by_name(name)
    if not customer:
        return f"No customer record found for '{name}'."

    tickets = get_tickets_by_customer(int(customer["customer_id"]))
    payload = {
        "customer": customer,
        "tickets": tickets,
    }
    return json.dumps(payload, indent=2)
