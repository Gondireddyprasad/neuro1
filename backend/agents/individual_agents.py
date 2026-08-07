
import os
import json
from datetime import datetime
from typing import Dict, Any
from google import genai
from backend.agents.state import CaseState
from backend.integrations.mock_apis import get_customer_details, get_order_details, execute_payment_refund
from backend.integrations.rag import search_relevant_policies

MEMORY_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/case_memory.jsonl"))
os.environ["GEMINI_API_KEY"] = "AIzaSyAV0OOvS-cxLB35hAMFsAfxv1TnL-IcnmE"
# 1. Customer Context Agent
def customer_context_agent(state: CaseState) -> Dict[str, Any]:
    """Fetches customer and order details from mock CRM/ERP."""
    cust_id = state.get("customer_id", "CUST-101")
    ord_id = state.get("order_id", "ORD-8821")
    
    customer = get_customer_details(cust_id) or {}
    order = get_order_details(ord_id) or {}
    
    trail_entry = {
        "agent": "Customer Context Agent",
        "action": "Fetched metadata from CRM/ERP",
        "details": f"Customer: {customer.get('name', 'Unknown')}, Item: {order.get('item_name', 'Unknown')}"
    }
    
    return {
        "customer_info": customer,
        "order_info": order,
        "trail": state.get("trail", []) + [trail_entry]
    }

# 2. Evidence Verification Agent (With Safe Gemini Vision Integration)
# 2. Evidence Verification Agent (Using Standard Gemini Vision Models)
def evidence_verification_agent(state: CaseState) -> Dict[str, Any]:
    """Analyzes claim text & damage photo using Google Gemini vision API."""
    desc = state.get("claim_description", "")
    image_path = state.get("image_path")
    
    severity = "Low"
    tampering_risk = "Low"
    damage_verified = False
    notes = ""

    api_key = os.getenv("GEMINI_API_KEY", "")

    if image_path and os.path.exists(image_path) and api_key:
        try:
            print("📸 [DEBUG] Calling Gemini Vision API...")
            gemini_client = genai.Client(api_key=api_key)
            
            with open(image_path, "rb") as img_file:
                image_bytes = img_file.read()

            prompt = f"""
            Analyze this uploaded image for a customer support damage claim.
            Customer Description: "{desc}"
            
            Inspect carefully:
            1. Is physical damage clearly visible on the item or packaging? (Yes/No)
            2. Damage Severity: (Low/Medium/High/None)
            3. Provide a short 1-sentence visual description of what you see in the photo.
            """

            # Determine mime type based on file extension
            mime_type = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

            # Primary attempt with gemini-1.5-flash
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=[
                        prompt,
                        genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                    ]
                )
            except Exception:
                # Fallback to gemini-2.0-flash if 2.5 is unavailable
                response = gemini_client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[
                        prompt,
                        genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                    ]
                )

            res_text = response.text
            print("✅ [DEBUG] Gemini Live Response:", res_text)
            
            res_lower = res_text.lower()
            if "yes" in res_lower and "none" not in res_lower:
                damage_verified = True
                severity = "High" if "high" in res_lower else "Medium"
            else:
                damage_verified = False
                severity = "None"
            
            notes = f"Gemini Live Analysis: {res_text.strip()}"

        except Exception as e:
            print(f"❌ [DEBUG] Gemini API Call Failed: {str(e)}")
            notes = f"Gemini API Error: {str(e)}"
            damage_verified = False
            severity = "None"
    else:
        damage_verified = False
        severity = "None"
        notes = "No valid image file or API key provided."

    evidence_summary = {
        "damage_verified": damage_verified,
        "damage_severity": severity,
        "tampering_risk": tampering_risk,
        "notes": notes
    }

    trail_entry = {
        "agent": "Evidence Verification Agent",
        "action": "Visual & Document Evidence Inspection",
        "details": f"Severity: {severity} | Verified: {damage_verified} | Notes: {notes}"
    }

    return {
        "evidence_summary": evidence_summary,
        "trail": state.get("trail", []) + [trail_entry]
    }

# 3. Policy RAG Agent
def policy_rag_agent(state: CaseState) -> Dict[str, Any]:
    """Queries ChromaDB vector database for relevant return policies."""
    query = state.get("claim_description", "return policy damage")
    matched_rules = search_relevant_policies(query, top_k=2)
    
    trail_entry = {
        "agent": "Policy RAG Agent",
        "action": "Queried ChromaDB Vector DB",
        "details": f"Retrieved {len(matched_rules)} matching policy rules"
    }
    
    return {
        "retrieved_policies": matched_rules,
        "trail": state.get("trail", []) + [trail_entry]
    }

# 4. Fraud Detection Agent
def fraud_detection_agent(state: CaseState) -> Dict[str, Any]:
    """Calculates behavioral fraud risk score based on account signals."""
    customer = state.get("customer_info", {})
    past_claims = customer.get("past_claims_count", 0)
    
    base_score = past_claims * 25.0
    reasons = []
    
    if past_claims > 3:
        base_score = 85.0
        reasons.append("High claim frequency detected (>3 past claims)")
    if customer.get("account_age_days", 300) < 30:
        base_score += 20.0
        reasons.append("New account vulnerability (<30 days old)")
        
    fraud_score = min(base_score, 100.0)
    if not reasons:
        reasons.append("Normal customer behavior profile")
        
    trail_entry = {
        "agent": "Fraud Agent",
        "action": "Evaluated behavioral risk profile",
        "details": f"Risk Score: {fraud_score}/100"
    }
    
    return {
        "fraud_score": fraud_score,
        "fraud_reasons": reasons,
        "trail": state.get("trail", []) + [trail_entry]
    }

# 5. Resolution Strategy Agent
# 5. Resolution Strategy Agent (Strict Verification Rules)
def resolution_strategy_agent(state: CaseState) -> Dict[str, Any]:
    """Formulates proposed resolution outcome strictly based on evidence verification."""
    order = state.get("order_info", {})
    claim_amount = state.get("claim_amount", order.get("amount", 0.0))
    evidence = state.get("evidence_summary", {})
    intent = state.get("intent", "REFUND_REQUEST")
    
    # Strict Evidence Gate
    if evidence.get("damage_verified"):
        if intent == "REPLACEMENT_REQUEST":
            action = "EXPRESS_REPLACEMENT"
            confidence = 0.95
            reasoning = "Verified item damage qualifies for immediate replacement dispatch."
        else:
            action = "FULL_REFUND"
            confidence = 0.95
            reasoning = "Verified item damage matches 100% refund policy."
    else:
        # Damage NOT verified (e.g., uploaded pristine/undamaged image while claiming damage)
        action = "CLAIM_DENIED_UNVERIFIED_EVIDENCE"
        confidence = 0.20  # Low confidence forces Escalation Agent to flag for manager review!
        reasoning = "Claim description specifies damage, but visual evidence shows an undamaged item."
        
    proposed_res = {
        "action": action,
        "confidence": confidence,
        "approved_amount": 0.0 if not evidence.get("damage_verified") else claim_amount,
        "explanation": reasoning
    }
    
    trail_entry = {
        "agent": "Resolution Strategy Agent",
        "action": "Proposed resolution outcome",
        "details": f"Action: {action} | Confidence: {confidence*100}% | Reason: {reasoning}"
    }
    
    return {
        "proposed_resolution": proposed_res,
        "trail": state.get("trail", []) + [trail_entry]
    }
# 6. Escalation Agent (Hard Safety Constraint)
def escalation_agent(state: CaseState) -> Dict[str, Any]:
    """Deterministic Python code check for human escalation thresholds."""
    claim_amount = state.get("claim_amount", 0.0)
    fraud_score = state.get("fraud_score", 0.0)
    res_confidence = state.get("proposed_resolution", {}).get("confidence", 1.0)
    
    escalate = False
    reasons = []
    
    if claim_amount > 500.0:
        escalate = True
        reasons.append("High-value claim threshold exceeded (>$500)")
    if fraud_score > 70.0:
        escalate = True
        reasons.append("High fraud risk score detected (>70/100)")
    if res_confidence < 0.60:
        escalate = True
        reasons.append("Low resolution confidence score (<60%)")
        
    reason_str = "; ".join(reasons) if escalate else "Passed all safety checks"
    
    trail_entry = {
        "agent": "Escalation Agent (Safety Gate)",
        "action": "Evaluated hard safety rules",
        "details": f"Escalated: {escalate} ({reason_str})"
    }
    
    return {
        "escalated": escalate,
        "escalation_reason": reason_str,
        "trail": state.get("trail", []) + [trail_entry]
    }

# 7. Workflow Execution Agent
def workflow_execution_agent(state: CaseState) -> Dict[str, Any]:
    """Executes transaction if claim is not escalated."""
    order_id = state.get("order_id", "")
    amount = state.get("proposed_resolution", {}).get("approved_amount", 0.0)
    
    result = execute_payment_refund(order_id, amount)
    
    trail_entry = {
        "agent": "Workflow Execution Agent",
        "action": "Executed mock payment API call",
        "details": f"Refund Status: {result['status']}, Transaction ID: {result['transaction_id']}"
    }
    
    return {
        "execution_result": result,
        "trail": state.get("trail", []) + [trail_entry]
    }


PENDING_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/pending_escalations.json"))

# 8. Learning & Governance Agent
def learning_agent(state: CaseState) -> Dict[str, Any]:
    """Saves finalized case outcomes into persistent memory and logs escalated cases to human review queue."""
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "customer_id": state.get("customer_id"),
        "order_id": state.get("order_id"),
        "claim_amount": state.get("claim_amount"),
        "claim_description": state.get("claim_description"),
        "fraud_score": state.get("fraud_score"),
        "escalated": state.get("escalated", False),
        "escalation_reason": state.get("escalation_reason"),
        "proposed_resolution": state.get("proposed_resolution"),
        "execution_result": state.get("execution_result"),
        "status": "PENDING_HUMAN_REVIEW" if state.get("escalated") else "AUTO_RESOLVED"
    }
    
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    
    # Append to full historical memory
    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
        
    # If case was escalated, also log to pending human queue
    if state.get("escalated"):
        pending_list = []
        if os.path.exists(PENDING_FILE):
            try:
                with open(PENDING_FILE, "r") as pf:
                    pending_list = json.load(pf)
            except Exception:
                pending_list = []
        
        pending_list.append(record)
        with open(PENDING_FILE, "w") as pf:
            json.dump(pending_list, pf, indent=2)

    trail_entry = {
        "agent": "Learning Agent",
        "action": "Updated Case Memory & Escalation Queue",
        "details": "Logged audit record and forwarded case to human queue if escalated."
    }
    
    return {
        "trail": state.get("trail", []) + [trail_entry]
    }