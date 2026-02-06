from typing import Dict, List
from openai import OpenAI
import os
import json
import re
import traceback


# Try relative import (when used as package), fallback to direct import
try:
    from .data_loader import DataLoader
except ImportError:
    try:
        from data_loader import DataLoader
    except ImportError:
        DataLoader = None

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


class ComplianceChecker:
    def __init__(self):
        """Initialize compliance checker"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        self.model = "anthropic/claude-opus-4.6"
        
        if DataLoader is not None:
            self.data_loader = DataLoader()
            print("Loading Indian Acts...")
            try:
                self.indian_acts = self.data_loader.load_indian_acts()
            except Exception as e:
                print(f"⚠️ Could not load Indian Acts: {e}. Continuing with LLM knowledge only.")
                self.indian_acts = []
            print(f"Loaded {len(self.indian_acts)} acts")
        else:
            print("⚠️ DataLoader not available. Continuing with LLM knowledge only.")
            self.indian_acts = []
        
    def check(self, text: str, language: str = "English") -> Dict:
        """
        Check compliance with Indian laws
        """
        
        lang_instruction = ""
        if language == "हिंदी (Hindi)":
            lang_instruction = "Write all JSON string values in Hindi (Devanagari script). Keys stay in English."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a JSON API for Indian contract compliance checking.

ABSOLUTE RULES:
1. Output ONLY raw JSON. No markdown. No ```json blocks. No text before or after.
2. Every string value must be under 30 words. No exceptions.
3. No case law names. No court citations. No legal precedents.
4. Maximum 3 applicable_laws, 4 violations, 4 recommendations.
5. "law" field: just act name and section (e.g. "Indian Contract Act 1872 - Section 27")
6. "issue" field: one short sentence only.
7. Total response must be under 800 tokens."""
                    },
                    {
                        "role": "user",
                        "content": f"""{lang_instruction}

Contract text:
{text[:3000]}

Return JSON:
{{"is_compliant": false, "applicable_laws": ["..."], "violations": [{{"law": "...", "issue": "..."}}], "recommendations": ["..."]}}"""
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            finish_reason = getattr(response.choices[0], 'finish_reason', None)
            if finish_reason == 'length':
                print("⚠️ Compliance response truncated. Attempting repair...")
            
            fallback = {
                'is_compliant': False,
                'applicable_laws': ["Indian Contract Act 1872"],
                'violations': [{"law": "Analysis Incomplete", "issue": "Response could not be parsed. Please try again."}],
                'recommendations': ["Re-run analysis or consult a legal professional"]
            }
            
            result = safe_parse_json(content, fallback)
            
            return {
                'is_compliant': result.get('is_compliant', True),
                'applicable_laws': result.get('applicable_laws', []),
                'violations': result.get('violations', []),
                'recommendations': result.get('recommendations', [])
            }
            
        except Exception as e:
            print(f"\n{'='*50}")
            print(f"❌ COMPLIANCE CHECK ERROR: {type(e).__name__}: {e}")
            print(f"{'='*50}")
            traceback.print_exc()
            print(f"{'='*50}\n")
            return {
                'is_compliant': False,
                'applicable_laws': ["Indian Contract Act 1872", "Information Technology Act 2000"],
                'violations': [
                    {"law": "General Review Required", "issue": "Automated compliance check encountered an error. Manual legal review is recommended."}
                ],
                'recommendations': [
                    "Have the contract reviewed by a qualified legal professional",
                    "Verify all clauses comply with Indian Contract Act 1872",
                    "Ensure compliance with applicable labor and industry-specific regulations"
                ]
            }