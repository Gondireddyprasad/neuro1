import time
import os
import re
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

from backend.agents.graph import claim_processing_graph
from backend.db.storage_handler import (
    save_claim_to_db, 
    fetch_all_claims, 
    fetch_pending_escalations, 
    update_case_status
)
from backend.integrations.rag import search_relevant_policies

app = FastAPI(
    title="NEURO Engine API",
    description="Multi-Tenant Claim Engine & Support Bot Gateway",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClaimSubmissionPayload(BaseModel):
    industry: str
    customer_id: str
    order_id: str
    claim_description: str
    claim_amount: float
    image_path: Optional[str] = None

class ManagerOverridePayload(BaseModel):
    case_id: str
    action: str  # MANUALLY_APPROVED or MANUALLY_REJECTED

class ChatIntakePayload(BaseModel):
    customer_id: str
    industry: str
    message: str
    amount: Optional[float] = 0.0


@app.get("/api/v1/health")
def health_check():
    return {"status": "ONLINE", "engine": "NEURO Multi-Agent System"}


@app.post("/api/v1/claims/submit")
def submit_claim(payload: ClaimSubmissionPayload):
    """Direct Manual Form Endpoint: Executes graph and persists claim to database."""
    try:
        initial_state = {
            "industry": payload.industry,
            "customer_id": payload.customer_id,
            "order_id": payload.order_id,
            "claim_description": payload.claim_description,
            "claim_amount": payload.claim_amount,
            "image_path": payload.image_path,
            "trail": []
        }

        final_state = claim_processing_graph.invoke(initial_state)
        exec_res = final_state.get("execution_result", {})

        # Ensure database persistence for manual form submission
        save_claim_to_db(final_state, exec_res)

        return {
            "case_id": final_state.get("case_id"),
            "proposed_resolution": final_state.get("proposed_resolution"),
            "escalated": final_state.get("escalated"),
            "escalation_reason": final_state.get("escalation_reason"),
            "execution_result": exec_res,
            "trail": final_state.get("trail")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Graph Execution Error: {str(e)}")


@app.post("/api/v1/chat/intake")
async def chat_intake_bot(payload: ChatIntakePayload):
    """Customer Support Bot Endpoint: Parses chat prompts, runs graph execution, and saves to SQLite DB."""
    msg = payload.message.lower()
    
    # 1. Extract dollar amounts directly from chat message if present (e.g., "30 dollars", "$30", "30$")
    extracted_amount = 0.0
    amount_matches = re.findall(r'(?:\$|\b)(\d+(?:\.\d{1,2})?)\s*(?:dollars?|\$)?\b', msg)
    if amount_matches:
        try:
            extracted_amount = float(amount_matches[0])
        except ValueError:
            extracted_amount = 0.0

    effective_amount = extracted_amount if extracted_amount > 0.0 else (payload.amount or 0.0)

    # 2. Pure Informational FAQ Query Check ($0 amount + question keyword)
    is_pure_faq = (effective_amount == 0.0) and any(k in msg for k in ["where is", "how do i", "policy", "hours", "status", "track", "cancel"])
    if is_pure_faq and not any(w in msg for w in ["claim", "refund", "lost", "broken", "damaged", "dollars", "money"]):
        policies = search_relevant_policies(payload.message, platform_type=payload.industry, top_k=1)
        reply_policy = policies[0] if policies else "Standard customer support terms apply."
        return {
            "type": "FAQ_RESOLVED",
            "reply": f"🤖 **AI Support Bot:** Here is the policy information regarding your inquiry:\n\n_{reply_policy}_",
            "scheduled_to_db": False
        }

    # 3. Dispute/Claim Multi-Agent Graph Execution
    initial_state = {
        "industry": payload.industry,
        "customer_id": payload.customer_id,
        "order_id": "ORD-CHAT-BOT",
        "claim_description": payload.message,
        "claim_amount": effective_amount,
        "image_path": None,
        "trail": []
    }

    try:
        final_state = await asyncio.to_thread(claim_processing_graph.invoke, initial_state)
        case_id = final_state.get("case_id") or f"CASE-{hex(int(time.time() * 1000))[2:].upper()}"
        escalated = final_state.get("escalated", False)
        exec_res = final_state.get("execution_result", {})
        exec_msg = exec_res.get("message", "")

        # 💾 HARD SAVE TO SQLITE DATABASE (Populates Tab 3 Queue)
        save_claim_to_db(final_state, exec_res)

        if escalated:
            bot_reply = f"🚨 **Ticket Logged in Database** (Case ID: `{case_id}`). Processed claim for **${effective_amount:.2f}**. This request requires photo proof or manager approval. Check Tab 3 for governance review!"
        else:
            bot_reply = f"✅ **Request Processed** (Case ID: `{case_id}`). Processed claim for **${effective_amount:.2f}**: {exec_msg}"

        return {
            "type": "TICKET_LOGGED",
            "case_id": case_id,
            "reply": bot_reply,
            "scheduled_to_db": True,
            "evaluation": final_state
        }
    except Exception as e:
        return {
            "type": "ERROR",
            "reply": f"⚠️ Error processing claim through multi-agent graph: {str(e)}",
            "scheduled_to_db": False
        }


@app.get("/api/v1/claims/all")
def get_all_claims():
    return fetch_all_claims()


@app.get("/api/v1/governance/pending")
def get_pending_escalations():
    """Fetches all pending escalations (from both form and chatbot channels)."""
    return fetch_pending_escalations()


@app.post("/api/v1/governance/override")
def manager_override(payload: ManagerOverridePayload):
    if payload.action == "MANUALLY_APPROVED":
        status = "APPROVED_BY_MANAGER"
        note = f"Human Manager manual override: Claim approved and funds disbursed."
    else:
        status = "REJECTED_BY_MANAGER"
        note = f"Human Manager manual override: Claim rejected and case closed."

    success = update_case_status(payload.case_id, status, note)
    if not success:
        raise HTTPException(status_code=404, detail="Case ID not found.")

    return {"status": "SUCCESS", "case_id": payload.case_id, "new_execution_status": status}