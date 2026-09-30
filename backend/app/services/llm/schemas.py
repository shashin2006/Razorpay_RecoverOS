from dataclasses import dataclass


@dataclass
class RecoveryAnalysis:
    summary: str
    root_cause: str
    revenue_risk: str
    ml_assessment: str
    policy_assessment: str
    recovery_strategy: str
    customer_message: str