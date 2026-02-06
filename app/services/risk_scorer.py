from typing import Dict
from openai import OpenAI
import os
import json
import re
import traceback

# Import JSON repair utility
try:
    from .json_utils import safe_parse_json
except ImportError:
    try:
        from json_utils import safe_parse_json
    except ImportError:
        def safe_parse_json(content, fallback=None):
            if fallback is None:
                fallback = {}
            content = content.strip()
            if content.startswith("```"):
                content = re.sub(r'^```json?\s*|\s*```$', '', content, flags=re.MULTILINE).strip()
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return fallback


class RiskScorer:
    def __init__(self):
        """Initialize the risk scorer"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "anthropic/claude-opus-4.6"
        
    def assess(self, text: str, language: str = "English") -> Dict:
        """
        Assess contract risks
        """
        
        lang_instruction = ""
        if language == "हिंदी (Hindi)":
            lang_instruction = "Write all JSON string values in Hindi (Devanagari script). Keys stay in English."
        
        # Build the example JSON as a plain string to avoid f-string brace conflicts
        example_json = '''
{
  "overall_score": 65,
  "legal_risk": "Medium",
  "financial_risk": "High",
  "compliance_risk": "Low",
  "detected_risks": {
    "penalty_clause": true,
    "indemnity_present": true,
    "unilateral_termination": true,
    "auto_renewal": false,
    "liability_cap_missing": true,
    "non_compete_present": true,
    "ip_transfer_present": true
  },
  "detailed_risks": [
    {"category": "...", "description": "..."}
  ]
}'''

        # Build user message with string concatenation (no f-string brace conflicts)
        user_content = lang_instruction + "\n\nContract text:\n" + text[:4000] + "\n\nReturn JSON:" + example_json

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a JSON API for contract risk assessment.

ABSOLUTE RULES:
1. Output ONLY raw JSON. No markdown. No ```json blocks. No text before or after.
2. Every "description" must be under 25 words. One sentence only.
3. No case law names. No court citations. No legal precedents.
4. Maximum 5 entries in detailed_risks.
5. Risk levels: only "High", "Medium", or "Low". Never "Unknown".
6. Total response must be under 600 tokens."""
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            finish_reason = getattr(response.choices[0], 'finish_reason', None)
            if finish_reason == 'length':
                print("⚠️ Risk assessment response truncated. Attempting repair...")
            
            fallback = {
                'overall_score': 50,
                'legal_risk': 'Medium',
                'financial_risk': 'Medium',
                'compliance_risk': 'Medium',
                'detailed_risks': [
                    {"category": "Analysis Incomplete", "description": "Response could not be parsed. Please try again."}
                ]
            }
            
            result = safe_parse_json(content, fallback)
            
            default_detected = {
                "penalty_clause": False,
                "indemnity_present": False,
                "unilateral_termination": False,
                "auto_renewal": False,
                "liability_cap_missing": False,
                "non_compete_present": False,
                "ip_transfer_present": False
            }
            
            return {
                'overall_score': result.get('overall_score', 50),
                'legal_risk': result.get('legal_risk', 'Medium'),
                'financial_risk': result.get('financial_risk', 'Medium'),
                'compliance_risk': result.get('compliance_risk', 'Medium'),
                'detected_risks': result.get('detected_risks', default_detected),
                'detailed_risks': result.get('detailed_risks', [])
            }
            
        except Exception as e:
            print(f"\n{'='*50}")
            print(f"❌ RISK ASSESSMENT ERROR: {type(e).__name__}: {e}")
            print(f"{'='*50}")
            traceback.print_exc()
            print(f"{'='*50}\n")
            return {
                'overall_score': 50,
                'legal_risk': 'Medium',
                'financial_risk': 'Medium',
                'compliance_risk': 'Medium',
                'detected_risks': {
                    "penalty_clause": False,
                    "indemnity_present": False,
                    "unilateral_termination": False,
                    "auto_renewal": False,
                    "liability_cap_missing": False,
                    "non_compete_present": False,
                    "ip_transfer_present": False
                },
                'detailed_risks': [
                    {"category": "Fallback", "description": "Risk analysis failed and default values were used."}
                ]
            }