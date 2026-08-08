from langgraph.graph import StateGraph, END
from backend.agents.state import CaseState
from backend.agents.individual_agents import (
    customer_context_agent,
    evidence_verification_agent,
    policy_rag_agent,
    fraud_risk_agent,
    resolution_strategy_agent,
    escalation_agent,
    learning_agent
)

# 1. Initialize State Graph
workflow = StateGraph(CaseState)

# 2. Add Multi-Agent Nodes
workflow.add_node("customer_context", customer_context_agent)
workflow.add_node("evidence_verification", evidence_verification_agent)
workflow.add_node("policy_rag", policy_rag_agent)
workflow.add_node("fraud_risk", fraud_risk_agent)
workflow.add_node("resolution_strategy", resolution_strategy_agent)
workflow.add_node("escalation", escalation_agent)
workflow.add_node("learning", learning_agent)

# 3. Define Graph Execution Edges
workflow.set_entry_point("customer_context")
workflow.add_edge("customer_context", "evidence_verification")
workflow.add_edge("evidence_verification", "policy_rag")
workflow.add_edge("policy_rag", "fraud_risk")
workflow.add_edge("fraud_risk", "resolution_strategy")
workflow.add_edge("resolution_strategy", "escalation")
workflow.add_edge("escalation", "learning")
workflow.add_edge("learning", END)

# 4. Compile and Export standard variables expected by backend/api.py
graph = workflow.compile()
claim_processing_graph = graph
app = graph