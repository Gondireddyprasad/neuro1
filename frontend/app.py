import sys
import os
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(
    page_title="NEURO - Enterprise Customer Experience Intelligence and Autonomous Dispute Resolution Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🛡️ NEURO: Enterprise Customer Experience Intelligence and Autonomous Dispute Resolution Agent")
st.caption("Powered by LangGraph Multi-Agent Orchestration & Domain-Isolated ChromaDB Policy Search")
st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "📥 Customer Portal & Bot",
    "📊 Administrator Analytics",
    "⚖️ Human Governance Queue"
])

CUSTOMER_DATABASE = {
    "E-Commerce: Mark Davis (General Query: Package Lost in Transit)": {
        "customer_id": "CUST-204", "order_id": "ORD-9912", "platform": "E-Commerce Platforms",
        "item_name": "Wireless Studio Headphones", "default_val": 0.00,
        "default_desc": "Where is my package? It was supposed to be here last week and tracking hasn't updated for days."
    },
    "E-Commerce: Alex Johnson (Refund Claim: Damaged Mechanical Keyboard)": {
        "customer_id": "CUST-101", "order_id": "ORD-8821", "platform": "E-Commerce Platforms",
        "item_name": "Mechanical Gaming Keyboard", "default_val": 149.99,
        "default_desc": "The box came completely crushed and the keyboard inside is cracked and broken."
    },
    "E-Commerce: Sam Scammer (Discrepancy Fraud Check)": {
        "customer_id": "CUST-666", "order_id": "ORD-1002", "platform": "E-Commerce Platforms",
        "item_name": "Wireless Noise-Canceling Headphones", "default_val": 299.99,
        "default_desc": "Item arrived damaged upon delivery."
    },
    "Banking: Sarah Connor (Refund Claim: Duplicate Wire Charge)": {
        "customer_id": "FIN-4022", "order_id": "TX-99821", "platform": "Banking & Financial Services",
        "item_name": "International Wire Transfer", "default_val": 450.00,
        "default_desc": "I see two identical charges on my bank statement for the exact same amount on the same day."
    },
    "Banking: Kevin Vance (Dispute: ATM Cash Dispense Failure)": {
        "customer_id": "FIN-5102", "order_id": "ATM-3301", "platform": "Banking & Financial Services",
        "item_name": "ATM Cash Withdrawal", "default_val": 200.00,
        "default_desc": "The ATM machine didn't give me my money but my mobile app says the money was withdrawn."
    },
    "Insurance: David Miller (Refund Claim: Vehicle Collision >$500)": {
        "customer_id": "INS-9081", "order_id": "CLAIM-7712", "platform": "Insurance Companies",
        "item_name": "Rear Bumper Collision Repair", "default_val": 1200.00,
        "default_desc": "Someone bumped into my car in the parking lot and smashed my rear bumper."
    }
}

# TAB 1: CUSTOMER PORTAL & SUPPORT CHATBOT
with tab1:
    st.subheader("Submit a Dispute, Query, or Chat with AI Support Bot")
    
    left_col, right_col = st.columns([1, 1.2], gap="large")

    with left_col:
        st.markdown("### 💬 Interactive Customer Support Assistant")
        
        selected_user_key = st.selectbox("Active Account Context:", list(CUSTOMER_DATABASE.keys()))
        cust_profile = CUSTOMER_DATABASE[selected_user_key]

        st.caption(f"**Customer ID:** {cust_profile['customer_id']} | **Platform:** `{cust_profile['platform']}`")

        # Chat history state
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = [
                {"role": "assistant", "content": "Hello! I am your AI Support Assistant. How can I help you with your order, billing, or claims today?"}
            ]

        # Render Chat Container
        chat_container = st.container(height=300)
        for msg in st.session_state.chat_history:
            chat_container.chat_message(msg["role"]).write(msg["content"])

        if user_prompt := st.chat_input("Type your question or issue here..."):
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            chat_container.chat_message("user").write(user_prompt)

            payload = {
                "customer_id": cust_profile['customer_id'],
                "industry": cust_profile['platform'],
                "message": user_prompt,
                "amount": float(cust_profile['default_val'])
            }

            try:
                resp = requests.post(f"{API_BASE_URL}/chat/intake", json=payload)
                if resp.status_code == 200:
                    bot_reply = resp.json().get("reply")
                    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                    chat_container.chat_message("assistant").write(bot_reply)
                    
                    if resp.json().get("scheduled_to_db"):
                        st.toast("📥 Ticket scheduled and logged in SQLite Database!", icon="💾")
                else:
                    st.error("Support bot communication failed.")
            except requests.exceptions.ConnectionError:
                st.error("FastAPI Backend Offline!")

    with right_col:
        st.markdown("### 🚀 Manual Form & Multi-Agent Stream")
        
        claim_desc = st.text_area("Customer Request / Dispute Description:", cust_profile['default_desc'], height=80)
        claim_val = st.number_input("Claim Value ($) [Set 0.00 for General Queries]:", value=float(cust_profile['default_val']), step=10.0)
        
        uploaded_file = st.file_uploader("Upload Supporting Evidence (Optional):", type=["jpg", "jpeg", "png"])
        
        saved_image_path = None
        if uploaded_file is not None:
            temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/temp_uploads"))
            os.makedirs(temp_dir, exist_ok=True)
            saved_image_path = os.path.join(temp_dir, uploaded_file.name)
            with open(saved_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.image(saved_image_path, caption="Uploaded Evidence Preview", width=180)

        submit_btn = st.button("🚀 Dispatch Direct to NEURO Engine", type="primary", width="stretch")

        if submit_btn:
            payload = {
                "industry": cust_profile['platform'],
                "customer_id": cust_profile['customer_id'],
                "order_id": cust_profile['order_id'],
                "claim_description": claim_desc,
                "claim_amount": claim_val,
                "image_path": saved_image_path
            }

            with st.spinner("Executing domain-isolated graph pipeline..."):
                try:
                    response = requests.post(f"{API_BASE_URL}/claims/submit", json=payload)
                    
                    if response.status_code == 200:
                        res_data = response.json()
                        resolution = res_data.get("proposed_resolution", {})
                        escalated = res_data.get("escalated", False)
                        exec_res = res_data.get("execution_result", {})
                        trail = res_data.get("trail", [])

                        total_time_ms = sum(step.get("execution_time_ms", 0.0) for step in trail)

                        sla_col1, sla_col2, sla_col3 = st.columns(3)
                        sla_col1.metric("Total Latency", f"{total_time_ms:.1f} ms")
                        sla_col2.metric("Target Domain", cust_profile['platform'])
                        sla_col3.metric("SLA Status", "COMPLIANT" if total_time_ms < 2000 else "EXCEEDED")

                        st.markdown("---")

                        if escalated:
                            st.error(f"⚠️ **CASE ESCALATED TO HUMAN GOVERNANCE**\n\n**Reason:** {res_data.get('escalation_reason')}\n\n*Queued in Tab 3 for human review.*")
                        elif resolution.get("action") == "QUERY_RESOLVED":
                            st.info(f"ℹ️ **INFORMATIONAL QUERY RESOLVED**\n\n**Resolution:** {resolution.get('reason')}\n\n**Status:** {exec_res.get('message')}")
                        elif "APPROVED" in resolution.get("action", ""):
                            st.success(f"✅ **CLAIM AUTOMATICALLY APPROVED**\n\n**Action:** {resolution.get('action')}\n\n**Reason:** {resolution.get('reason')}\n\n**Payout Execution:** {exec_res.get('message')}")
                        else:
                            st.warning(f"❌ **CLAIM REJECTED BY POLICY ENGINE**\n\n**Action:** {resolution.get('action')}\n\n**Reason:** {resolution.get('reason')}")

                        with st.expander("🔍 Live Agent Execution Graph & SLA Timers", expanded=True):
                            for idx, step in enumerate(trail, 1):
                                st.markdown(f"**Node {idx}: 🤖 {step.get('agent')}** — *{step.get('action')}*")
                                st.caption(f"Details: {step.get('details')} | ⏱️ Latency: `{step.get('execution_time_ms', 0.0):.2f} ms`")
                                st.markdown("---")
                    else:
                        st.error(f"Backend API Error [{response.status_code}]: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to FastAPI server at `http://127.0.0.1:8000`.")

# TAB 2: ANALYTICS
with tab2:
    st.subheader("📊 Enterprise Historical Audit Trail & Metrics")
    try:
        response = requests.get(f"{API_BASE_URL}/claims/all")
        if response.status_code == 200:
            claims = response.json()
            if not claims:
                st.info("No historical claims found in SQLite database yet.")
            else:
                st.dataframe(claims, width="stretch")
    except requests.exceptions.ConnectionError:
        st.error("FastAPI Server Offline!")

# TAB 3: HUMAN GOVERNANCE PANEL
with tab3:
    st.subheader("⚖️ Human-in-the-Loop Governance Panel")
    st.caption("Review granular agentic escalation flags, Ground Truth API findings, and ChromaDB policy rules.")
    st.markdown("---")
    
    try:
        response = requests.get(f"{API_BASE_URL}/governance/pending")
        if response.status_code == 200:
            pending_cases = response.json()
            if not pending_cases:
                st.success("🎉 All human governance queues are clear! Automated agents are resolving claims with 100% SLA compliance.")
            else:
                for idx, case in enumerate(pending_cases):
                    with st.expander(f"📋 Case ID: {case.get('case_id')} | Customer: {case.get('customer_id')} | Amount: ${case.get('claim_amount', 0.0):.2f}", expanded=True):
                        
                        diag_col1, diag_col2 = st.columns([1, 1], gap="medium")
                        
                        with diag_col1:
                            st.markdown("#### 🔍 Customer Claim & Evidence")
                            st.write(f"**Customer Description:** {case.get('claim_description', 'N/A')}")
                            st.warning(f"**Safety Gate Escalation Cause:**\n{case.get('escalation_reason', 'Flagged by Safety Gate')}")
                        
                        with diag_col2:
                            st.markdown("#### 🤖 Exact Machine & API Diagnostic")
                            st.error(f"**Ground Truth API Finding:**\n{case.get('api_notes', 'API logs checked.')}")
                            st.info(f"**ChromaDB Policy Rule Applied:**\n{case.get('detailed_reason', 'Applied escalation policy.')}")

                        st.markdown("---")
                        st.markdown("#### 🛠️ Human Manager Override Controls")
                        btn_col1, btn_col2, _ = st.columns([1, 1, 2])
                        
                        with btn_col1:
                            if st.button("✅ Approve & Disburse", key=f"btn_app_{case['case_id']}_{idx}", type="primary"):
                                override_payload = {"case_id": case['case_id'], "action": "MANUALLY_APPROVED"}
                                override_resp = requests.post(f"{API_BASE_URL}/governance/override", json=override_payload)
                                if override_resp.status_code == 200:
                                    st.success(f"Case {case['case_id']} manually approved!")
                                    st.rerun()
                                else:
                                    st.error("Failed to execute override.")
                                    
                        with btn_col2:
                            if st.button("❌ Reject Claim", key=f"btn_rej_{case['case_id']}_{idx}"):
                                override_payload = {"case_id": case['case_id'], "action": "MANUALLY_REJECTED"}
                                override_resp = requests.post(f"{API_BASE_URL}/governance/override", json=override_payload)
                                if override_resp.status_code == 200:
                                    st.warning(f"Case {case['case_id']} manually rejected!")
                                    st.rerun()
                                else:
                                    st.error("Failed to execute override.")
        else:
            st.error(f"Error fetching pending escalations: HTTP {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FastAPI backend at `http://127.0.0.1:8000`.")