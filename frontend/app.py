import streamlit as st
import sys
import os
import json

# Add root project folder to sys.path so backend imports work smoothly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents.graph import app_graph
from backend.agents.individual_agents import MEMORY_FILE, PENDING_FILE
from backend.integrations.mock_apis import get_order_details, execute_payment_refund

st.set_page_config(
    page_title="NEURO | Autonomous CX Platform",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 NEURO: Enterprise Autonomous CX & Dispute Resolution")
st.markdown("Multi-Agent LangGraph Orchestration • Multimodal Intelligence • Human-in-the-Loop Governance")

# 3-Tab Enterprise Layout
tab1, tab2, tab3 = st.tabs([
    "💬 Customer Support Portal", 
    "📊 Administrator Analytics & Audit Log",
    "🛡️ Human Governance & Escalation Queue"
])

# ==========================================
# TAB 1: CUSTOMER SUPPORT PORTAL (Tamper-Proof)
# ==========================================
with tab1:
    st.divider()
    
    st.sidebar.header("👤 Authenticated User Session")
    user_profile = st.sidebar.radio(
        "Select Active User Profile:",
        [
            "Alex Johnson (Verified Gold Member)",
            "Sam Scammer (High Risk Account)",
            "High-Value VIP Order User"
        ]
    )

    if user_profile == "Alex Johnson (Verified Gold Member)":
        customer_id = "CUST-101"
        order_id = "ORD-8821"
    elif user_profile == "Sam Scammer (High Risk Account)":
        customer_id = "CUST-999"
        order_id = "ORD-9900"
    else:
        customer_id = "CUST-101"
        order_id = "ORD-9900"

    order_data = get_order_details(order_id) or {}
    verified_item_name = order_data.get("item_name", "Unknown Product")
    verified_amount = order_data.get("amount", 0.0)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📥 File a Dispute / Return Claim")
        
        st.info(f"**Logged In Customer:** {customer_id}\n\n**Selected Order:** {order_id} ({verified_item_name})")
        st.markdown(f"**Verified Item Value:** `${verified_amount:.2f}` *(Auto-verified via ERP)*")
        
        claim_desc = st.text_area("Describe the Issue", value="Item arrived damaged upon delivery.", height=100)
        upload_img = st.file_uploader("Upload Damage Photo (Optional)", type=["png", "jpg", "jpeg"])
        
        run_button = st.button("🚀 Submit Claim to NEURO Autonomous Engine", type="primary")

    with col2:
        st.subheader("⚡ Live Multi-Agent Execution Trail")
        
        if run_button:
            temp_image_path = None
            if upload_img is not None:
                # Save uploaded file temporarily to disk so backend agents can inspect real file path
                temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/temp_uploads"))
                os.makedirs(temp_dir, exist_ok=True)
                temp_image_path = os.path.join(temp_dir, upload_img.name)
                with open(temp_image_path, "wb") as f:
                    f.write(upload_img.getbuffer())

            initial_state = {
                "customer_id": customer_id,
                "order_id": order_id,
                "claim_amount": verified_amount,
                "claim_description": claim_desc,
                "image_path": temp_image_path,
                "trail": []
            }
            
            with st.spinner("Executing multi-agent resolution workflow..."):
                final_state = app_graph.invoke(initial_state)
                
            for step in final_state.get("trail", []):
                with st.expander(f"🔹 {step['agent']}: {step['action']}", expanded=True):
                    st.write(step["details"])
                    
            st.divider()
            st.subheader("🎯 Resolution Summary")
            
            if final_state.get("escalated"):
                st.error(f"🚨 **CLAIM ESCALATED TO HUMAN REVIEW**\n\n**Reason:** {final_state.get('escalation_reason')}")
                st.warning("🔒 Payment execution node was automatically bypassed by safety guardrails. Case sent to Tab 3 Queue.")
            else:
                st.success("✅ **CLAIM AUTOMATICALLY APPROVED & PROCESSED**")
                res = final_state.get("execution_result", {})
                st.json(res)

# ==========================================
# TAB 2: ADMINISTRATOR ANALYTICS & AUDIT LOG
# ==========================================
with tab2:
    st.divider()
    st.subheader("📊 Executive Analytics & System Metrics")
    
    memory_records = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            for line in f:
                if line.strip():
                    memory_records.append(json.loads(line.strip()))
                    
    total_cases = len(memory_records)
    escalated_cases = sum(1 for r in memory_records if r.get("escalated"))
    auto_resolved = total_cases - escalated_cases
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Claims Processed", total_cases)
    m2.metric("Auto-Resolved (Straight-Through)", auto_resolved)
    m3.metric("Escalated for Human Review", escalated_cases)
    m4.metric("Automation Rate", f"{((auto_resolved/total_cases)*100):.1f}%" if total_cases > 0 else "N/A")
    
    st.divider()
    st.subheader("📋 Historical Case Audit Memory (Learning Store)")
    
    if memory_records:
        st.dataframe(memory_records, use_container_width=True)
    else:
        st.info("No claim records logged in case memory yet.")

# ==========================================
# TAB 3: HUMAN-IN-THE-LOOP (HITL) GOVERNANCE
# ==========================================
with tab3:
    st.divider()
    st.subheader("🛡️ Manager Escalation Queue & Override Control")
    st.markdown("Review AI-flagged claims exceeding financial or behavioral risk thresholds.")
    
    pending_cases = []
    if os.path.exists(PENDING_FILE):
        try:
            with open(PENDING_FILE, "r") as pf:
                pending_cases = json.load(pf)
        except Exception:
            pending_cases = []
            
    active_queue = [c for c in pending_cases if c.get("status") == "PENDING_HUMAN_REVIEW"]
    
    if not active_queue:
        st.success("🎉 No pending cases requiring human intervention! All automated guardrails satisfied.")
    else:
        st.warning(f"⚠️ **{len(active_queue)} Pending Case(s) awaiting manager decision:**")
        
        for idx, case in enumerate(active_queue):
            with st.expander(f"⚠️ Case #{idx+1} | Customer: {case['customer_id']} | Amount: ${case['claim_amount']:.2f}", expanded=True):
                col_a, col_b = st.columns([2, 1])
                
                with col_a:
                    st.write(f"**Order ID:** {case['order_id']}")
                    st.write(f"**Claim Description:** {case['claim_description']}")
                    st.write(f"**Escalation Reason:** {case['escalation_reason']}")
                    st.write(f"**Behavioral Fraud Score:** {case['fraud_score']}/100")
                    st.write(f"**AI Proposed Action:** {case['proposed_resolution'].get('action')} (Confidence: {case['proposed_resolution'].get('confidence')*100}%)")
                
                with col_b:
                    st.subheader("Manager Action")
                    approve = st.button(f"✅ Override & Approve Refund", key=f"app_{idx}")
                    reject = st.button(f"❌ Reject Claim", key=f"rej_{idx}")
                    
                    if approve:
                        res = execute_payment_refund(case["order_id"], case["claim_amount"])
                        case["status"] = "MANUALLY_APPROVED"
                        case["execution_result"] = res
                        
                        with open(PENDING_FILE, "w") as pf:
                            json.dump(pending_cases, pf, indent=2)
                            
                        st.success(f"Refund Approved! Tx ID: {res['transaction_id']}")
                        st.rerun()
                        
                    if reject:
                        case["status"] = "MANUALLY_REJECTED"
                        with open(PENDING_FILE, "w") as pf:
                            json.dump(pending_cases, pf, indent=2)
                            
                        st.error("Claim Rejected by Human Support Manager.")
                        st.rerun()