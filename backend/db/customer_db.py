import sqlite3
import os
import json

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "customer_data.db"))

def init_customer_db():
    """Initializes the multi-domain SQLite database and seeds default records."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Unified Customer Profiles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            domain TEXT NOT NULL,
            account_tier TEXT DEFAULT 'Standard',
            past_disputes INTEGER DEFAULT 0,
            domain_metadata TEXT
        )
    """)

    # Seed multi-domain records across industries if empty
    cursor.execute("SELECT COUNT(*) FROM customer_profiles")
    if cursor.fetchone()[0] == 0:
        domain_records = [
            # E-Commerce Domain
            (
                "CUST-204", "Mark Davis", "mark.davis@email.com", "E-Commerce Platforms", "Silver Tier", 1,
                json.dumps({
                    "active_order_id": "ORD-9912",
                    "item_name": "Wireless Studio Headphones",
                    "order_status": "In Transit",
                    "tracking_number": "TRK-9981273",
                    "delivery_eta": "Tomorrow by 5 PM"
                })
            ),
            (
                "CUST-101", "Alex Johnson", "alex.j@email.com", "E-Commerce Platforms", "Gold Tier", 0,
                json.dumps({
                    "active_order_id": "ORD-8821",
                    "item_name": "Mechanical Gaming Keyboard",
                    "order_status": "Delivered",
                    "tracking_number": "TRK-4410293",
                    "delivery_eta": "Delivered March 20"
                })
            ),
            (
                "CUST-666", "Sam Scammer", "sam.s@email.com", "E-Commerce Platforms", "High Risk Tier", 4,
                json.dumps({
                    "active_order_id": "ORD-1002",
                    "item_name": "Wireless Noise-Canceling Headphones",
                    "order_status": "Delivered",
                    "tracking_number": "TRK-1002938",
                    "delivery_eta": "Delivered March 18"
                })
            ),
            # Banking & Financial Services Domain
            (
                "FIN-4022", "Sarah Connor", "sarah.c@banking.com", "Banking & Financial Services", "VIP Tier", 0,
                json.dumps({
                    "account_number": "ACCT-88402911",
                    "transaction_id": "TX-99821",
                    "transaction_type": "International Wire Transfer",
                    "amount": "$450.00",
                    "transaction_status": "Settled / Duplicate Flagged"
                })
            ),
            (
                "FIN-5102", "Kevin Vance", "kevin.v@banking.com", "Banking & Financial Services", "Standard", 2,
                json.dumps({
                    "account_number": "ACCT-11029384",
                    "transaction_id": "ATM-3301",
                    "transaction_type": "ATM Cash Withdrawal",
                    "amount": "$200.00",
                    "transaction_status": "Failed / Dispense Error"
                })
            ),
            # Insurance Domain
            (
                "INS-9081", "David Miller", "david.m@insurance.com", "Insurance Companies", "Standard", 0,
                json.dumps({
                    "policy_number": "POL-AUTO-99012",
                    "claim_id": "CLAIM-7712",
                    "asset_covered": "Rear Bumper Collision Repair",
                    "claim_status": "Under Assessment",
                    "coverage_limit": "$10,000.00"
                })
            )
        ]

        cursor.executemany("""
            INSERT INTO customer_profiles (customer_id, name, email, domain, account_tier, past_disputes, domain_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, domain_records)

    conn.commit()
    conn.close()


def get_multi_domain_customer_context(customer_id: str) -> dict:
    """Queries SQLite DB for customer record and parses domain_metadata JSON."""
    init_customer_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM customer_profiles WHERE customer_id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {}

    data = dict(row)
    if data.get("domain_metadata"):
        try:
            data["domain_metadata"] = json.loads(data["domain_metadata"])
        except Exception:
            data["domain_metadata"] = {}
    return data

if __name__ == "__main__":
    init_customer_db()
    print("✅ Customer SQLite database created and seeded successfully at:", DB_PATH)