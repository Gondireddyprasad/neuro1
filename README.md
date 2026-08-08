<img width="1408" height="773" alt="neuro_scrnshot" src="https://github.com/user-attachments/assets/eff07ca6-f61a-48fc-b6a8-231f64c0e2bf" /># 🧠 NEURO Engine — Enterprise Customer Experience Intelligence and Autonomous Dispute Resolution Agent.
[Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[LangChain](https://img.shields.io/badge/LangChain-Google_GenAI-green.svg)](https://www.langchain.com/)
[License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

NEURO Engine is an enterprise-grade, multi-agent AI system built to automate domain-aware customer support, physical damage verification, and claim resolution across 10+ industries (E-Commerce, Banking, Insurance, SaaS, etc.). 

By leveraging **Gemini 1.5 Flash Multimodal Vision**, a Hybrid Dual-Database Architecture (SQLite + ChromaDB), and Fail-Safe Human Governance Gates, NEURO bridges the gap between autonomous AI operations and strict corporate risk compliance.

---

## Key Architecture Highlights
Multi-Agent Orchestration (LangGraph): Specialised autonomous agents pass structured execution state through strict inspection gates.
Multimodal Damage Inspection: Integrates Gemini 1.5 Flash Vision to perform direct diagnostic analysis on uploaded visual evidence (cracks, breakage, fraud discrepancies).
Hybrid Dual-Database Strategy:
 SQLite Relational DB: Stores structured multi-domain customer context (order IDs, tracking numbers, transaction hashes, policy coverage limits) with sub-millisecond lookup latency.
 ChromaDB Vector DB: Executes domain-isolated Retrieval-Augmented Generation (RAG) across enterprise terms and legal policies.
Fail-Safe Governance Gate: Any high-value claim ($> \$500$), visual discrepancy, fraud score spike, or network/API failure automatically routes the case to a Human Manager Override Queue rather than making unverified disbursements.
Sub-Millisecond SLA Tracking:** Every agent node records precise microsecond execution metrics (`execution_time_ms`) to provide full auditability in real time.

---
## 🏗️ System Architecture & Workflow

```text
                                  ┌──────────────────────────────┐
                                  │    Customer Request / Form   │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                NEURO Multi-Agent Graph Pipeline                                  │
│                                                                                                 │
│  ┌───────────────────────┐    ┌───────────────────────┐    ┌─────────────────────────────────┐  │
│  │ 1. Customer Context   │───►│ 2. Evidence Verification│───►│ 3. Policy RAG Agent             │  │
│  │    (SQLite Query)     │    │    (Gemini Vision)    │    │    (ChromaDB Vector Search)     │  │
│  └───────────────────────┘    └───────────────────────┘    └─────────────────────────────────┘  │
│                                                                            │                    │
│  ┌───────────────────────┐    ┌───────────────────────┐                    │                    │
│  │ 6. Learning & Memory  │◄───│ 5. Execution / Refund │◄───────────────────┘                    │
│  │    (SQL Audit Log)    │    │    (Mock Payment API) │                                         │
│  └───────────────────────┘    └───────────────────────┘                                         │
│                                           ▲                                                     │
│                                           │                                                     │
│                               ┌───────────────────────┐                                         │
│                               │ 4. Safety Gate Agent  │                                         │
│                               │    (Escalation Gate)  │                                         │
│                               └───────────┬───────────┘                                         │
└───────────────────────────────────────────┼─────────────────────────────────────────────────────┘
                                            │ (If Risk/Discrepancy Triggered)
                                            ▼
                             ┌─────────────────────────────┐
                             │ Human Governance Queue (Tab3)│
                             │   (Manager Approval/Reject) │
                             └─────────────────────────────┘

🛠️ Tech Stack 
Backend Framework: FastAPI, Uvicorn, Asyncio

Frontend UI: Streamlit (Multi-Tab Interface)

Agent Framework: LangGraph, LangChain Core

LLM & Vision Model: Google Gemini 1.5 Flash (langchain-google-genai)

Databases: SQLite3 (Customer Profiles & Audit Logs), ChromaDB (Vector Embeddings)

🚀 Quick Start & Installation
1. Prerequisites
Python 3.10 or higher

Google Gemini API Key

2. Clone the Repository

git clone [)
cd neuro-engine

3. Set Up Virtual Environment & Dependencies
Bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the root directory:

Code snippet
GEMINI_API_KEY="your_actual_gemini_api_key_here"

🏃 Running the Application
Open two separate terminal windows:

Terminal 1: Start FastAPI Backend
Bash
uvicorn backend.api:app --reload --port 8000
API Swagger Documentation will be live at: http://localhost:8000/docs

Terminal 2: Start Streamlit Frontend
Bash
streamlit run frontend/app.py
Frontend Application will open at: http://localhost:8501


