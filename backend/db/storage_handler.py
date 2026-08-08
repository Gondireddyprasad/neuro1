import sqlite3
import os
import time
from typing import List, Dict, Any

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/neuro_enterprise.db"))


def get_db_connection():
    """Initializes and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            case_id TEXT PRIMARY KEY,
            customer_id TEXT,
            order_id TEXT,
            claim_amount REAL,
            claim_description TEXT,
            escalated INTEGER,
            escalation_reason TEXT,
            detailed_reason TEXT,
            api_notes TEXT,
            execution_status TEXT,
            execution_message TEXT,
            created_at REAL
        )
    ''')
    
    conn.commit()
    conn.close()


def save_claim_to_db(state: dict, execution_result: dict) -> str:
    """Saves claim state and detailed machine/API diagnostics into SQLite."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Generate unique Case ID if not present in state
    case_id = state.get("case_id") or f"CASE-{hex(int(time.time() * 1000))[2:].upper()}"
    cust_id = state.get("customer_id", "UNKNOWN")
    order_id = state.get("order_id", "UNKNOWN")
    amount = float(state.get("claim_amount", 0.0))
    desc = state.get("claim_description", "")
    
    escalated = 1 if state.get("escalated", False) else 0
    escalation_reason = state.get("escalation_reason", "")
    
    resolution = state.get("proposed_resolution", {})
    evidence = state.get("evidence_summary", {})
    
    detailed_reason = resolution.get("reason") or "Applied standard safety policy rules."
    api_notes = evidence.get("api_notes") or "Ground truth API checks completed."

    exec_status = execution_result.get("status", "HOLD" if escalated else "COMPLETED")
    exec_msg = execution_result.get("message", "")

    # Insert fresh claim or replace existing case ID
    cursor.execute('''
        INSERT OR REPLACE INTO claims 
        (case_id, customer_id, order_id, claim_amount, claim_description, escalated, escalation_reason, detailed_reason, api_notes, execution_status, execution_message, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        case_id, 
        cust_id, 
        order_id, 
        amount, 
        desc, 
        escalated, 
        escalation_reason, 
        detailed_reason, 
        api_notes, 
        exec_status, 
        exec_msg, 
        time.time()
    ))

    conn.commit()
    conn.close()
    return case_id


def fetch_all_claims() -> List[Dict[str, Any]]:
    """Retrieves all historical claims for Tab 2 Analytics."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM claims ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def fetch_pending_escalations() -> List[Dict[str, Any]]:
    """Retrieves pending cases flagged for Human Governance in Tab 3."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM claims WHERE escalated = 1 AND execution_status = 'HOLD' ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def update_case_status(case_id: str, status: str, message: str) -> bool:
    """Updates case execution status after a human manager override."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE claims 
        SET execution_status = ?, execution_message = ? 
        WHERE case_id = ?
    ''', (status, message, case_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated


# Ensure DB schema is initialized on import
init_db()