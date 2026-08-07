from typing import TypedDict, List, Dict, Any, Optional

class CaseState(TypedDict, total=False):
    # Customer & Order Context
    customer_id: str
    order_id: str
    customer_info: Dict[str, Any]
    order_info: Dict[str, Any]
    
    # Claim Input
    claim_description: str
    image_path: Optional[str]
    claim_amount: float
    
    # Agent Outputs
    evidence_summary: Dict[str, Any]      # Filled by Evidence Agent
    retrieved_policies: List[str]          # Filled by Policy Agent
    fraud_score: float                     # Filled by Fraud Agent
    fraud_reasons: List[str]               # Filled by Fraud Agent
    proposed_resolution: Dict[str, Any]   # Filled by Resolution Agent
    
    # Escalation & Safety Flags
    escalated: bool                        # Deterministic safety gate
    escalation_reason: str
    
    # Final Action Execution
    execution_result: Dict[str, Any]       # Filled by Execution Agent
    
    # Audit & Visual Trail for UI
    trail: List[Dict[str, Any]]