import os
import chromadb
from chromadb.utils import embedding_functions

client = chromadb.Client()
embedding_func = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="enterprise_policies_deep",
    embedding_function=embedding_func
)

# Deep Multi-Domain Customer Query Database (Real-World Natural Language Inputs)
CUSTOMER_QUERY_DATABASE = {
    # 1. E-COMMERCE PLATFORMS
    "ECOM-01": {
        "customer_id": "CUST-101", "order_id": "ORD-8821", "platform": "E-Commerce Platforms",
        "item_name": "Mechanical Gaming Keyboard", "claim_amount": 149.99,
        "query": "The box came completely crushed and the keyboard inside is cracked and broken.",
        "expected_ground_truth": "VISUAL_DAMAGE_VERIFICATION"
    },
    "ECOM-02": {
        "customer_id": "CUST-204", "order_id": "ORD-9912", "platform": "E-Commerce Platforms",
        "item_name": "Wireless Studio Headphones", "claim_amount": 220.00,
        "query": "Where is my package? It was supposed to be here last week and tracking hasn't updated for days.",
        "expected_ground_truth": "COURIER_SLA_BREACH"
    },
    "ECOM-03": {
        "customer_id": "CUST-309", "order_id": "ORD-1102", "platform": "E-Commerce Platforms",
        "item_name": "Smart Watch Series 7", "claim_amount": 350.00,
        "query": "The box is totally fine and undamaged, but the screen is completely shattered!",
        "expected_ground_truth": "VISUAL_DISCREPANCY_CHECK"
    },

    # 2. BANKING & FINANCIAL SERVICES
    "FIN-01": {
        "customer_id": "FIN-4022", "order_id": "TX-99821", "platform": "Banking & Financial Services",
        "item_name": "International Wire Transfer", "claim_amount": 450.00,
        "query": "I see two identical charges on my bank statement for the exact same amount on the same day.",
        "expected_ground_truth": "DUPLICATE_TRANSACTION_LOG"
    },
    "FIN-02": {
        "customer_id": "FIN-5102", "order_id": "ATM-3301", "platform": "Banking & Financial Services",
        "item_name": "ATM Cash Withdrawal", "claim_amount": 200.00,
        "query": "The ATM machine didn't give me my money but my mobile app says the money was withdrawn.",
        "expected_ground_truth": "ATM_HARDWARE_ERROR_LOG"
    },

    # 3. INSURANCE COMPANIES
    "INS-01": {
        "customer_id": "INS-9081", "order_id": "CLAIM-7712", "platform": "Insurance Companies",
        "item_name": "Rear Bumper Collision Repair", "claim_amount": 1200.00,
        "query": "Someone bumped into my car in the parking lot and smashed my rear bumper.",
        "expected_ground_truth": "HIGH_VALUE_ADJUSTER_THRESHOLD"
    },

    # 4. TELECOMMUNICATIONS
    "TEL-01": {
        "customer_id": "TEL-3310", "order_id": "BILL-4410", "platform": "Telecommunications",
        "item_name": "5G Roaming Package", "claim_amount": 85.50,
        "query": "Why am I being billed extra for roaming when I was at home connected to my own Wi-Fi?",
        "expected_ground_truth": "CELLULAR_WIFI_LOG_VERIFIED"
    },

    # 5. LOGISTICS & SUPPLY CHAIN
    "LOG-01": {
        "customer_id": "LOG-8819", "order_id": "WAYBILL-9901", "platform": "Logistics & Supply Chain",
        "item_name": "Refrigerated Pharma Shipment", "claim_amount": 850.00,
        "query": "The temperature sensors in the cold container recorded a spike above safe limits during transit.",
        "expected_ground_truth": "IOT_THERMAL_SENSOR_EXCURSION"
    },

    # 6. HEALTHCARE SERVICES
    "HLT-01": {
        "customer_id": "HLT-1102", "order_id": "MED-3301", "platform": "Healthcare Services",
        "item_name": "Diagnostic Brain MRI Scan", "claim_amount": 650.00,
        "query": "My doctor approved this MRI in advance, why am I getting billed out-of-network rates?",
        "expected_ground_truth": "EHR_PRE_AUTH_RECORD_FOUND"
    },

    # 7. SUBSCRIPTION PLATFORMS
    "SUB-01": {
        "customer_id": "SUB-5541", "order_id": "SUB-99120", "platform": "Subscription Platforms",
        "item_name": "Annual Enterprise SaaS Plan", "claim_amount": 299.00,
        "query": "My annual subscription renewed yesterday automatically. I want to cancel and get my money back.",
        "expected_ground_truth": "24_HOUR_CANCEL_TIMESTAMP"
    },

    # 8. RETAIL ENTERPRISES
    "RET-01": {
        "customer_id": "RET-4491", "order_id": "RCP-88301", "platform": "Retail Enterprises",
        "item_name": "Cordless Power Drill Set", "claim_amount": 180.00,
        "query": "I bought this drill set yesterday at the store, opened the box, and the motor won't turn on at all.",
        "expected_ground_truth": "POS_RECEIPT_VERIFIED"
    },

    # 9. TRAVEL & HOSPITALITY
    "TRV-01": {
        "customer_id": "TRV-6610", "order_id": "PNR-X8911", "platform": "Travel & Hospitality",
        "item_name": "Transcontinental Flight Fare", "claim_amount": 520.00,
        "query": "The airline canceled my flight 3 hours before takeoff and didn't rebook me on another plane.",
        "expected_ground_truth": "FLIGHT_CANCEL_SLA_LOG"
    },

    # 10. GOVERNMENT CITIZEN SERVICES
    "CIT-01": {
        "customer_id": "CIT-2026", "order_id": "PERMIT-5510", "platform": "Government Citizen Services",
        "item_name": "Building Renovation Permit", "claim_amount": 210.00,
        "query": "The online portal glitched and charged my credit card twice for the same permit fee.",
        "expected_ground_truth": "TREASURY_GATEWAY_DUPLICATE"
    }
}


# Natural Language Vector Policy Catalog in ChromaDB
MASSIVE_NATURAL_POLICIES = [
    # 1. E-COMMERCE PLATFORMS
    {"platform": "E-Commerce Platforms", "title": "Damaged Transit Policy", "rule": "If product or box arrives damaged, broken, crushed, or shattered within 30 days of delivery, approve full refund or free replacement."},
    {"platform": "E-Commerce Platforms", "title": "Delayed Lost Delivery Policy", "rule": "If tracking has not updated for over 7 days or item is past estimated delivery date, auto-issue full refund for lost shipment."},
    {"platform": "E-Commerce Platforms", "title": "API Vision Discrepancy Rule", "rule": "If customer claims item is damaged or broken but Vision API inspection returns clean or undamaged product, block auto-refund and place case on Human Manager Hold for fraud review."},

    # 2. BANKING & FINANCIAL SERVICES
    {"platform": "Banking & Financial Services", "title": "Double Charge Policy", "rule": "If customer is charged twice or sees duplicate transactions on the same date, issue immediate provisional account credit upon ledger log confirmation."},
    {"platform": "Banking & Financial Services", "title": "ATM Cash Error Policy", "rule": "If ATM machine fails to dispense cash but account is debited, credit back the full amount within 48 hours upon terminal log audit."},

    # 3. INSURANCE COMPANIES
    {"platform": "Insurance Companies", "title": "Collision Claim Threshold", "rule": "Auto collision repairs under $500 auto-approve; claims exceeding $500 require formal insurance adjuster evaluation and human review."},

    # 4. TELECOMMUNICATIONS
    {"platform": "Telecommunications", "title": "Wi-Fi Roaming Credit Rule", "rule": "If customer is charged roaming fees while active on home Wi-Fi network, issue 100% billing credit immediately."},

    # 5. LOGISTICS & SUPPLY CHAIN
    {"platform": "Logistics & Supply Chain", "title": "Temperature Sensor Excursion", "rule": "If refrigerated pharma/perishable cargo telemetry breaches thermal limits during transit, approve full cargo loss claim."},

    # 6. HEALTHCARE SERVICES
    {"platform": "Healthcare Services", "title": "PCP Pre-Authorization Rule", "rule": "If diagnostic scan or procedure was pre-authorized by PCP, re-adjust out-of-network billing to standard in-network copay tier."},

    # 7. SUBSCRIPTION PLATFORMS
    {"platform": "Subscription Platforms", "title": "Auto-Renewal 48-Hour Cancellation", "rule": "If customer requests cancellation within 48 hours of an automatic annual subscription renewal, auto-issue full pro-rated refund."},

    # 8. RETAIL ENTERPRISES
    {"platform": "Retail Enterprises", "title": "Defective Store Merchandise", "rule": "If item is defective out of box within 14 days of receipt, approve immediate product exchange or full refund."},

    # 9. TRAVEL & HOSPITALITY
    {"platform": "Travel & Hospitality", "title": "Flight Delay Cancellation SLA", "rule": "If flight is canceled within 4 hours of departure without alternative flight provided, auto-issue full fare refund or 120% voucher."},

    # 10. GOVERNMENT CITIZEN SERVICES
    {"platform": "Government Citizen Services", "title": "Portal Duplicate Overpayment", "rule": "If portal glitched and debited duplicate municipal permit fees, refund overpayment directly back to citizen bank account."}
]


def seed_chromadb_vector_store():
    documents = []
    metadatas = []
    ids = []
    
    for idx, item in enumerate(MASSIVE_NATURAL_POLICIES):
        # We index natural phrasing so semantic cosine similarity works effortlessly!
        doc_text = f"[{item['platform']}] Query/Rule: {item['title']} - {item['rule']}"
        documents.append(doc_text)
        metadatas.append({"platform": item["platform"]})
        ids.append(f"deep_policy_v2_{idx}")

    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
    print(f"✅ ChromaDB seeded with {len(documents)} natural language policy rules across 10 platforms!")

if __name__ == "__main__":
    seed_chromadb_vector_store()