from langgraph.graph import StateGraph, END
from backend.agents.state import CaseState
from backend.agents.individual_agents import (
    customer_context_agent,
    evidence_verification_agent,
    policy_rag_agent,
    fraud_detection_agent,
    resolution_strategy_agent,
    escalation_agent,
    workflow_execution_agent,
    learning_agent
)

def build_graph():
    """Constructs the multi-agent LangGraph execution graph."""
    workflow = StateGraph(CaseState)
    
    # Add Agent Nodes
    workflow.add_node("customer_context", customer_context_agent)
    workflow.add_node("evidence_verification", evidence_verification_agent)
    workflow.add_node("policy_rag", policy_rag_agent)
    workflow.add_node("fraud_detection", fraud_detection_agent)
    workflow.add_node("resolution_strategy", resolution_strategy_agent)
    workflow.add_node("escalation_check", escalation_agent)
    workflow.add_node("workflow_execution", workflow_execution_agent)
    workflow.add_node("learning_node", learning_agent)
    
    # Define Sequential Execution Edges
    workflow.set_entry_point("customer_context")
    workflow.add_edge("customer_context", "evidence_verification")
    workflow.add_edge("evidence_verification", "policy_rag")
    workflow.add_edge("policy_rag", "fraud_detection")
    workflow.add_edge("fraud_detection", "resolution_strategy")
    workflow.add_edge("resolution_strategy", "escalation_check")
    
    # Deterministic Safety Router
    def route_after_escalation_check(state: CaseState) -> str:
        """Routing to learning node if escalated (skipping payout execution)."""
        if state.get("escalated", False):
            return "learning_node"  # Safety Gate: Skip payment API completely
        return "workflow_execution"
    
    # Conditional Routing Edge
    workflow.add_conditional_edges(
        "escalation_check",
        route_after_escalation_check,
        {
            "learning_node": "learning_node",
            "workflow_execution": "workflow_execution"
        }
    )
    
    workflow.add_edge("workflow_execution", "learning_node")
    workflow.add_edge("learning_node", END)
    
    return workflow.compile()

app_graph = build_graph()