from __future__ import annotations

import sqlite3
from pathlib import Path

from app.utils.config import DB_PATH

SCHEMA_PATH = Path(__file__).resolve().with_name("schema.sql")

CUSTOMERS = [
    (1, "Ema Wilson", "ema.wilson@example.com", "+1-555-0101", "Toronto", "Premium", "Active", "2023-03-15"),
    (2, "Liam Chen", "liam.chen@example.com", "+1-555-0102", "Mississauga", "Standard", "Active", "2024-01-12"),
    (3, "Sophia Patel", "sophia.patel@example.com", "+1-555-0103", "Brampton", "Premium", "Paused", "2022-11-04"),
    (4, "Noah Brown", "noah.brown@example.com", "+1-555-0104", "Ottawa", "Standard", "Active", "2024-05-22"),
    (5, "Ava Martinez", "ava.martinez@example.com", "+1-555-0105", "Hamilton", "Enterprise", "Active", "2021-08-09"),
]

TICKETS = [
    (101, 1, "Refund", "Customer requested refund after receiving a damaged product.", "Resolved", "2025-11-10", "2025-11-12", "High"),
    (102, 1, "Delivery", "Asked for shipping delay update.", "Closed", "2025-12-01", "2025-12-02", "Medium"),
    (103, 2, "Billing", "Question about duplicate charge on monthly plan.", "Open", "2025-11-21", None, "High"),
    (104, 3, "Account", "Requested temporary account pause.", "Resolved", "2025-10-15", "2025-10-16", "Low"),
    (105, 4, "Technical", "Unable to access dashboard after password reset.", "In Progress", "2025-12-05", None, "Medium"),
    (106, 5, "Refund", "Requested refund for unused service credits.", "Open", "2025-12-07", None, "High"),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany(
            """
            INSERT INTO customers (customer_id, full_name, email, phone, city, plan_type, account_status, signup_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            CUSTOMERS,
        )
        conn.executemany(
            """
            INSERT INTO tickets (ticket_id, customer_id, issue_category, issue_summary, ticket_status, created_at, resolved_at, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            TICKETS,
        )
        conn.commit()
        print(f"Seeded database at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
