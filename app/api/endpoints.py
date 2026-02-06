from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from services.contract_analyzer import ContractAnalyzer
from services.risk_scorer import RiskScorer
from services.compliance_checker import ComplianceChecker
from utils.file_handler import FileHandler
from models.schemas import (
    ContractAnalysisResponse,
    RiskAssessmentResponse,
    ComplianceCheckResponse
)

app = FastAPI(title="CARA Bot API", version="1.0.0")

# Initialize services
file_handler = FileHandler()
analyzer = ContractAnalyzer()
risk_scorer = RiskScorer()
compliance_checker = ComplianceChecker()


@app.get("/")
def root():
    return {"message": "CARA Bot API", "version": "1.0.0"}


@app.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(file: UploadFile = File(...)):
    """Analyze uploaded contract"""
    try:
        # Save and extract text
        filepath = file_handler.save_upload(file)
        text = file_handler.extract_text(filepath)
        
        # Analyze
        result = analyzer.analyze(text)
        
        return ContractAnalysisResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/assess-risk", response_model=RiskAssessmentResponse)
async def assess_risk(file: UploadFile = File(...)):
    """Assess contract risks"""
    try:
        filepath = file_handler.save_upload(file)
        text = file_handler.extract_text(filepath)
        
        result = risk_scorer.assess(text)
        
        return RiskAssessmentResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-compliance", response_model=ComplianceCheckResponse)
async def check_compliance(file: UploadFile = File(...)):
    """Check compliance with Indian laws"""
    try:
        filepath = file_handler.save_upload(file)
        text = file_handler.extract_text(filepath)
        
        result = compliance_checker.check(text)
        
        return ComplianceCheckResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy"}