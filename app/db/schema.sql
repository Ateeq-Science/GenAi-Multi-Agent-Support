DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    city TEXT,
    plan_type TEXT,
    account_status TEXT,
    signup_date TEXT
);

CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    issue_category TEXT,
    issue_summary TEXT,
    ticket_status TEXT,
    created_at TEXT,
    resolved_at TEXT,
    priority TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
