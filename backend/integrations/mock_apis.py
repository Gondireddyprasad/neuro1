import time
from typing import Dict, Any

# Multi-Tenant Customer Registry
CUSTOMER_PROFILES = {
    "CUST-101": {"name": "Alex Johnson", "tier": "Gold Tier Member", "past_disputes": 0, "trust_score": 92.5},
    "CUST-204": {"name": "Mark Davis", "tier": "Silver Tier Member", "past_disputes": 1, "trust_score": 81.0},
    "CUST-666": {"name": "Sam Scammer", "tier": "High Risk Account", "past_disputes": 5, "trust_score": 12.0},
    "FIN-4022": {"name": "Sarah Connor", "tier": "Premier Banking Client", "past_disputes": 0, "trust_score": 98.0},
    "FIN-5102": {"name": "Kevin Vance", "tier": "Standard Checking Account", "past_disputes": 1, "trust_score": 85.0},
    "INS-9081": {"name": "David Miller", "tier": "Auto Policyholder (Preferred)", "past_disputes": 0, "trust_score": 95.0},
    "INS-3021": {"name": "Anna Bell", "tier": "Health Plan Subscriber", "past_disputes": 0, "trust_score": 90.0},
    "TEL-3310": {"name": "Emily Davis", "tier": "5G Unlimited Subscriber", "past_disputes": 0, "trust_score": 88.0},
    "TEL-9901": {"name": "TechCorp Inc", "tier": "Enterprise Fiber Tier", "past_disputes": 2, "trust_score": 79.0},
    "LOG-8819": {"name": "Cargo Freight LLC", "tier": "Cold-Chain Logistics Partner", "past_disputes": 1, "trust_score": 87.0},
    "HLT-1102": {"name": "Robert Taylor", "tier": "Primary Care Member", "past_disputes": 0, "trust_score": 94.0},
    "SUB-5541": {"name": "Jessica White", "tier": "SaaS Annual Subscriber", "past_disputes": 0, "trust_score": 96.0},
    "SUB-7701": {"name": "CloudNet Systems", "tier": "Enterprise Cloud Partner", "past_disputes": 1, "trust_score": 83.0},
    "RET-4491": {"name": "Michael Brown", "tier": "In-Store Rewards Member", "past_disputes": 0, "trust_score": 89.0},
    "TRV-6610": {"name": "Laura Martinez", "tier": "Frequent Flyer Platinum", "past_disputes": 0, "trust_score": 97.0},
    "CIT-2026": {"name": "Citizen James Wilson", "tier": "Verified Municipal Resident", "past_disputes": 0, "trust_score": 99.0}
}

# Order & Service Reference Registry
ORDER_PROFILES = {
    "ORD-8821": {"item_name": "Mechanical Gaming Keyboard", "category": "E-Commerce", "amount": 149.99},
    "ORD-9912": {"item_name": "Wireless Studio Headphones", "category": "E-Commerce", "amount": 220.00},
    "ORD-1002": {"item_name": "Wireless Noise-Canceling Headphones", "category": "E-Commerce", "amount": 299.99},
    "TX-99821": {"item_name": "International Wire Transfer", "category": "Banking", "amount": 450.00},
    "ATM-3301": {"item_name": "ATM Checking Cash Withdrawal", "category": "Banking", "amount": 200.00},
    "CLAIM-7712": {"item_name": "Rear Bumper Collision Repair", "category": "Insurance", "amount": 1200.00},
    "CLAIM-1102": {"item_name": "ER Outpatient Treatment Copay", "category": "Insurance", "amount": 350.00},
    "BILL-4410": {"item_name": "5G Roaming Package Fee", "category": "Telecommunications", "amount": 85.50},
    "BILL-7721": {"item_name": "Dedicated Fiber Enterprise Line", "category": "Telecommunications", "amount": 450.00},
    "WAYBILL-9901": {"item_name": "Refrigerated Pharma Freight Shipment", "category": "Logistics", "amount": 850.00},
    "MED-3301": {"item_name": "Diagnostic Brain MRI Scan", "category": "Healthcare", "amount": 650.00},
    "SUB-99120": {"item_name": "Annual Enterprise SaaS Renewal", "category": "Subscription", "amount": 299.00},
    "SUB-10022": {"item_name": "Cloud Hosting Enterprise Tier", "category": "Subscription", "amount": 400.00},
    "RCP-88301": {"item_name": "Cordless Power Drill Set", "category": "Retail", "amount": 180.00},
    "PNR-X8911": {"item_name": "Transcontinental Flight Fare", "category": "Travel", "amount": 520.00},
    "PERMIT-5510": {"item_name": "Building Renovation Permit Fee", "category": "Government", "amount": 210.00}
}


def get_customer_details(customer_id: str) -> Dict[str, Any]:
    """Fetches real profile details from registry, or generates dynamic domain record."""
    if customer_id in CUSTOMER_PROFILES:
        return CUSTOMER_PROFILES[customer_id]
    
    # Dynamic fallback for new customer IDs
    return {
        "name": f"Customer ({customer_id})",
        "tier": "Standard Verified Member",
        "past_disputes": 0,
        "trust_score": 85.0
    }


def get_order_details(order_id: str) -> Dict[str, Any]:
    """Fetches real order/asset details from registry, or generates dynamic record."""
    if order_id in ORDER_PROFILES:
        return ORDER_PROFILES[order_id]
        
    # Dynamic fallback for new order IDs
    return {
        "item_name": f"Asset/Service Ref ({order_id})",
        "category": "Enterprise Services",
        "amount": 100.00
    }


def execute_payment_refund(order_id: str, amount: float) -> Dict[str, Any]:
    """Executes resolution credit via gateway API."""
    return {
        "status": "SUCCESS",
        "message": f"Successfully disbursed resolution credit of ${amount:.2f} for Ref #{order_id} via Payment Gateway API.",
        "transaction_id": f"TXN-REFUND-{int(time.time())}"
    }