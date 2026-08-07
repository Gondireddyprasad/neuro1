from typing import Dict, Any, Optional

# Mock Customer Database (CRM)
MOCK_CUSTOMERS: Dict[str, Dict[str, Any]] = {
    "CUST-101": {
        "name": "Alex Johnson",
        "email": "alex@example.com",
        "account_age_days": 450,
        "past_claims_count": 0,
        "loyalty_tier": "Gold"
    },
    "CUST-999": {
        "name": "Sam Scammer",
        "email": "sam@suspicious.com",
        "account_age_days": 12,
        "past_claims_count": 4,
        "loyalty_tier": "Bronze"
    }
}

# Mock Order Database (ERP)
MOCK_ORDERS: Dict[str, Dict[str, Any]] = {
    "ORD-8821": {
        "customer_id": "CUST-101",
        "item_name": "Mechanical Gaming Keyboard",
        "amount": 149.99,
        "purchase_date": "2026-03-01",
        "delivery_status": "Delivered",
        "return_eligible": True
    },
    "ORD-9900": {
        "customer_id": "CUST-999",
        "item_name": "Pro Gaming Monitor",
        "amount": 799.99,
        "purchase_date": "2026-03-10",
        "delivery_status": "Delivered",
        "return_eligible": False
    }
}

def get_customer_details(customer_id: str) -> Optional[Dict[str, Any]]:
    """Simulates a CRM API lookup for customer metadata."""
    return MOCK_CUSTOMERS.get(customer_id)

def get_order_details(order_id: str) -> Optional[Dict[str, Any]]:
    """Simulates an ERP API lookup for order details."""
    return MOCK_ORDERS.get(order_id)

def execute_payment_refund(order_id: str, amount: float) -> Dict[str, Any]:
    """Simulates calling a payment gateway (e.g., Stripe API) to issue a refund."""
    return {
        "status": "SUCCESS",
        "transaction_id": f"TXN-REFUND-{order_id}",
        "amount_refunded": amount,
        "message": f"Successfully processed refund of ${amount:.2f} for Order {order_id}"
    }