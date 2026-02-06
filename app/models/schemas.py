from pydantic import BaseModel
from typing import List, Dict, Optional


class Clause(BaseModel):
    type: str
    text: str
    risk_level: str
    explanation: str


class ContractAnalysisResponse(BaseModel):
    contract_type: str
    parties: List[str]
    dates: List[str]
    amounts: List[str]
    clauses: List[Clause]


class RiskDetail(BaseModel):
    category: str
    description: str


class RiskAssessmentResponse(BaseModel):
    overall_score: int
    legal_risk: str
    financial_risk: str
    compliance_risk: str
    detailed_risks: List[RiskDetail]


class Violation(BaseModel):
    law: str
    issue: str


class ComplianceCheckResponse(BaseModel):
    is_compliant: bool
    applicable_laws: List[str]
    violations: List[Violation]