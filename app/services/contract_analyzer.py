from typing import Dict, List
import spacy
from openai import OpenAI
import os
import re
import json
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


class ContractAnalyzer:
    def __init__(self):
        """Initialize the contract analyzer"""
        self.nlp = spacy.load("en_core_web_sm")
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
        
        # Use Claude Opus 4.6
        self.model = "anthropic/claude-opus-4.6"
        
    def analyze(self, text: str, language: str = "English") -> Dict:
        """
        Analyze contract and extract key information
        
        Args:
            text: Contract text to analyze
            language: Output language (English or हिंदी (Hindi))
            
        Returns:
            Dictionary containing contract analysis
        """
        
        # Language instruction for LLM
        lang_instruction = ""
        if language == "हिंदी (Hindi)":
            lang_instruction = "Provide ALL explanations, descriptions, and text in Hindi (Devanagari script). Keep JSON keys in English but values in Hindi."
        
        print(f"Analyzing contract with Claude Opus 4.6 in {language}...")
        
        try:
            # Build example JSON outside f-string to avoid brace conflicts
            example_json = '''
{
  "contract_type": "Service Agreement",
  "parties": [
    "Client (Pvt Ltd): Orion Retail Private Limited",
    "Service Provider (LLP): BlueWave Analytics LLP",
    "Signatory: Mr. Vikram Mehta, Director of Orion Retail"
  ],
  "dates": [
    "April 10, 2024 — Agreement Execution Date",
    "May 1, 2024 — Service Commencement Date",
    "April 30, 2025 — Initial Term End Date (1 year)",
    "March 1, 2024 — Proposal Submission Date"
  ],
  "amounts": [
    "INR 2,50,000/month — Service Fee (payable by 5th of each month)",
    "INR 15,000/month — Maintenance Charges",
    "INR 5,00,000 — Security Deposit (refundable on termination)",
    "18% per annum — Late Payment Interest",
    "INR 50,000 — Early Termination Penalty"
  ],
  "clauses": [
    {"type": "Non-Compete", "risk_level": "High", "explanation": "Restricts working with competitors for 1 year post-termination."},
    {"type": "Confidentiality", "risk_level": "Low", "explanation": "Standard NDA covering proprietary data during and after contract."},
    {"type": "Termination", "risk_level": "Medium", "explanation": "Either party can terminate with 30 days written notice."},
    {"type": "Indemnification", "risk_level": "High", "explanation": "Provider bears unlimited liability for third-party IP claims."},
    {"type": "Payment Terms", "risk_level": "Medium", "explanation": "Monthly invoicing with 15-day payment window and late fees."}
  ]
}'''

            user_content = lang_instruction + "\n\nContract text:\n" + text[:5000] + "\n\nReturn JSON exactly like this example (but with ACTUAL values from the contract above):" + example_json + "\n\nIMPORTANT: Every party MUST have a role prefix (Employer/Employee/Client/Vendor etc). Every date MUST have context after an em dash. Every amount MUST have frequency and purpose. Extract ALL parties, ALL dates, and ALL monetary values from the contract."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a JSON API for contract analysis.

ABSOLUTE RULES:
1. Output ONLY raw JSON. No markdown. No ```json blocks. No text before or after.
2. Each clause "explanation" must be under 25 words. One sentence only.
3. No case law. No court citations. No legal precedents.
4. Exactly 5-9 clauses with mix of High/Medium/Low risk levels.
5. Total response must be under 1500 tokens.
6. PARTIES: Every party string MUST start with their role (Employer/Employee/Client/Service Provider/Landlord/Tenant etc) followed by colon then name. Include ALL parties.
7. DATES: Every date string MUST have context after " — " (e.g. "Jan 1, 2024 — Contract Start Date"). Never bare dates.
8. AMOUNTS: Every amount MUST include frequency (per month/per year/one-time) AND purpose (salary/rent/penalty/deposit etc). Break down ALL monetary values separately — salary, overtime, bonuses, deductions, penalties, deposits."""
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                max_tokens=3000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content.strip()
            
            # Check if response was truncated
            finish_reason = getattr(response.choices[0], 'finish_reason', None)
            if finish_reason == 'length':
                print("⚠️ Contract analysis response was truncated. Attempting JSON repair...")
            
            # Use robust JSON parser
            fallback_result = self._basic_extraction(text, language)
            result = safe_parse_json(content, fallback_result)
            
            # Validate and return
            result_data = {
                'contract_type': result.get('contract_type', 'Unknown'),
                'parties': result.get('parties', []),
                'dates': result.get('dates', []),
                'amounts': result.get('amounts', []),
                'clauses': result.get('clauses', [])
            }
            
            # If LLM returned empty clauses, use NLP fallback
            if not result_data['clauses'] or len(result_data['clauses']) == 0:
                result_data['clauses'] = self.extract_clauses(text)
            
            return result_data
            
        except Exception as e:
            print(f"\n{'='*50}")
            print(f"❌ ANALYSIS ERROR: {type(e).__name__}: {e}")
            print(f"{'='*50}")
            traceback.print_exc()
            print(f"{'='*50}\n")
            return self._basic_extraction(text, language)
    
    def get_detailed_analysis(self, clause: Dict, full_text: str, language: str = "English") -> Dict:
        """
        Get detailed analysis for a specific clause
        
        Args:
            clause: The clause dictionary with type, risk_level, explanation
            full_text: Full contract text for context
            language: Output language
            
        Returns:
            Dictionary with detailed explanation, issues, recommendations, laws
        """
        
        lang_instruction = ""
        if language == "हिंदी (Hindi)":
            lang_instruction = "Provide ALL responses in Hindi (Devanagari script). Keep JSON keys in English but all values in Hindi."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a JSON API for detailed contract clause analysis.

ABSOLUTE RULES:
1. Output ONLY raw JSON. No markdown. No ```json blocks. No text before or after.
2. "explanation": 3-5 sentences in plain language. Under 100 words.
3. "issues": 2-4 bullet points as a single string. Under 80 words total.
4. "recommendations": 2-4 actionable steps as a single string. Under 80 words total.
5. "applicable_laws": List relevant Indian act names and sections only. Under 60 words. No case law names.
6. Total response must be under 800 tokens."""
                    },
                    {
                        "role": "user",
                        "content": f"""{lang_instruction}

CLAUSE: {clause.get('type', 'Unknown')} | Risk: {clause.get('risk_level', 'Unknown')}
SUMMARY: {clause.get('explanation', 'None')}

CONTRACT CONTEXT:
{full_text[:2000]}

Return JSON:
{{"explanation": "...", "issues": "...", "recommendations": "...", "applicable_laws": "..."}}"""
                    }
                ],
                max_tokens=1500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content.strip()
            
            # Use robust JSON parser
            fallback_detailed = {
                'explanation': 'Unable to generate detailed explanation at this time.',
                'issues': 'Analysis could not be completed. Please try again.',
                'recommendations': 'Consult a legal professional for detailed review.',
                'applicable_laws': 'Not available due to analysis error.'
            }
            
            detailed = safe_parse_json(content, fallback_detailed)
            
            return {
                'explanation': detailed.get('explanation', 'Unable to generate detailed explanation'),
                'issues': detailed.get('issues', 'No specific issues identified'),
                'recommendations': detailed.get('recommendations', 'No recommendations available'),
                'applicable_laws': detailed.get('applicable_laws', 'No specific laws referenced')
            }
            
        except Exception as e:
            print(f"Detailed analysis error: {e}")
            return {
                'explanation': f'Unable to generate detailed analysis. Error: {str(e)}',
                'issues': 'Analysis could not be completed at this time.',
                'recommendations': 'Please try again or consult a legal professional.',
                'applicable_laws': 'Not available due to analysis error.'
            }
    
    def _basic_extraction(self, text: str, language: str = "English") -> Dict:
        """
        Fallback extraction using regex when LLM fails
        
        Args:
            text: Contract text
            language: Output language
            
        Returns:
            Basic extracted information
        """
        
        print("Using fallback extraction method...")
        
        # Detect contract type from first 500 characters
        contract_type = "Unknown"
        text_upper = text.upper()[:500]
        
        if "EMPLOYMENT" in text_upper:
            contract_type = "Employment Agreement" if language == "English" else "रोजगार समझौता"
        elif "SERVICE" in text_upper:
            contract_type = "Service Agreement" if language == "English" else "सेवा समझौता"
        elif "NON-DISCLOSURE" in text_upper or "NDA" in text_upper:
            contract_type = "Non-Disclosure Agreement" if language == "English" else "गोपनीयता समझौता"
        elif "SALE" in text_upper or "PURCHASE" in text_upper:
            contract_type = "Sale/Purchase Agreement" if language == "English" else "बिक्री/खरीद समझौता"
        
        # Extract monetary amounts (INR) with surrounding context
        raw_amounts = re.findall(r'(?:[\w\s]{0,30})?INR\s*[\d,]+(?:\.\d+)?(?:\s*(?:per|/-|/)\s*\w+)?(?:[\w\s]{0,30})?', text)
        amounts = []
        for amt in list(set(raw_amounts))[:5]:
            amt_clean = amt.strip()
            # Extract just the INR figure
            inr_match = re.search(r'INR\s*[\d,]+(?:\.\d+)?(?:\s*(?:per|/-|/)\s*\w+)?', amt_clean)
            if inr_match:
                amounts.append(inr_match.group(0).strip())
        if not amounts:
            # Simpler fallback
            amounts = re.findall(r'INR\s*[\d,]+(?:\.\d+)?(?:\s*(?:per|/-|/)\s*\w+)?', text)
            amounts = list(set(amounts))[:5]
        
        # Extract dates with surrounding context
        date_pattern = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}'
        dates_raw = re.findall(date_pattern, text)
        dates = []
        for d in list(set(dates_raw))[:5]:
            # Try to find context around the date
            idx = text.find(d)
            if idx > 0:
                # Get up to 60 chars before the date for context
                before = text[max(0, idx-60):idx].strip()
                # Get last meaningful phrase
                before_words = before.split()[-6:]  # last 6 words
                context = ' '.join(before_words).strip(' .,;:')
                if context and len(context) > 3:
                    dates.append(f"{d} — {context}")
                else:
                    dates.append(d)
            else:
                dates.append(d)
        
        # Extract company/party names with role detection
        companies_raw = re.findall(
            r'([A-Z][A-Za-z\s&]+(?:Private Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?))',
            text
        )
        companies = list(set(companies_raw))[:3]
        
        # Extract person names
        persons = re.findall(r'(?:Mr\.?|Ms\.?|Mrs\.?|Dr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text)
        persons = list(set(persons))[:3]
        
        # Try to assign roles based on contract type and position
        parties = []
        text_upper_full = text.upper()
        
        if contract_type in ["Employment Agreement", "रोजगार समझौता"]:
            for i, c in enumerate(companies):
                parties.append(f"Employer: {c.strip()}")
            for i, p in enumerate(persons):
                parties.append(f"Employee: {p.strip()}")
        elif contract_type in ["Service Agreement", "सेवा समझौता"]:
            for i, c in enumerate(companies):
                if i == 0:
                    parties.append(f"Client: {c.strip()}")
                else:
                    parties.append(f"Service Provider: {c.strip()}")
            for p in persons:
                parties.append(f"Signatory: {p.strip()}")
        elif contract_type in ["Non-Disclosure Agreement", "गोपनीयता समझौता"]:
            for i, c in enumerate(companies):
                if i == 0:
                    parties.append(f"Disclosing Party: {c.strip()}")
                else:
                    parties.append(f"Receiving Party: {c.strip()}")
            for p in persons:
                parties.append(f"Signatory: {p.strip()}")
        else:
            for c in companies:
                parties.append(f"Party: {c.strip()}")
            for p in persons:
                parties.append(f"Individual: {p.strip()}")
        
        if not parties:
            parties = ['Unable to identify parties']
        
        if language == "हिंदी (Hindi)":
            if not dates:
                dates = ['कोई तिथि नहीं मिली']
            if not amounts:
                amounts = ['कोई राशि नहीं मिली']
        else:
            if not dates:
                dates = ['No dates found']
            if not amounts:
                amounts = ['No financial terms found']
        
        # Extract clauses using NLP
        extracted_clauses = self.extract_clauses(text)
        
        # If NLP found nothing, provide generic clauses
        if not extracted_clauses:
            if language == "हिंदी (Hindi)":
                extracted_clauses = [
                    {
                        "type": "सामान्य अनुबंध शर्तें",
                        "risk_level": "Medium",
                        "explanation": "अनुबंध में मानक शर्तें पाई गई हैं। दोनों पक्षों के लिए निष्पक्षता सुनिश्चित करने के लिए समीक्षा अनुशंसित है।"
                    }
                ]
            else:
                extracted_clauses = [
                    {
                        "type": "General Contract Terms",
                        "risk_level": "Medium",
                        "explanation": "Standard contractual terms detected. Review recommended to ensure fairness to both parties."
                    }
                ]
        
        return {
            'contract_type': contract_type,
            'parties': parties,
            'dates': dates,
            'amounts': amounts,
            'clauses': extracted_clauses
        }
    
    def extract_clauses(self, text: str) -> List[Dict]:
        """
        Extract specific clause types using NLP
        
        Args:
            text: Contract text
            
        Returns:
            List of identified clauses
        """
        
        doc = self.nlp(text[:10000])  # Limit to first 10k chars for performance
        
        clauses = []
        
        # Define clause patterns with risk levels and explanations
        clause_patterns = {
            'Non-Compete': {
                'patterns': ['non-compete', 'non compete', 'restraint of trade', 'competing business'],
                'risk_level': 'High',
                'explanation': 'Non-compete clause restricts future employment opportunities. May be unenforceable under Section 27 of the Indian Contract Act 1872.'
            },
            'Confidentiality': {
                'patterns': ['confidential', 'proprietary information', 'trade secret'],
                'risk_level': 'Low',
                'explanation': 'Confidentiality obligations for protecting sensitive information. Standard in most contracts but review scope and duration.'
            },
            'Termination': {
                'patterns': ['termination', 'terminate this agreement', 'notice period'],
                'risk_level': 'Medium',
                'explanation': 'Termination provisions define how either party can end the contract. Review notice period requirements and consequences of termination.'
            },
            'Indemnification': {
                'patterns': ['indemnify', 'indemnification', 'hold harmless'],
                'risk_level': 'High',
                'explanation': 'Indemnification clause may expose one party to unlimited financial liability. Ensure liability caps and mutual indemnification exist.'
            },
            'Intellectual Property': {
                'patterns': ['intellectual property', 'IP rights', 'patents', 'copyrights'],
                'risk_level': 'Medium',
                'explanation': 'IP assignment clause transfers ownership of created work. Verify scope does not extend to personal or pre-existing IP.'
            },
            'Arbitration': {
                'patterns': ['arbitration', 'dispute resolution', 'arbitrator'],
                'risk_level': 'Medium',
                'explanation': 'Dispute resolution through arbitration. Review jurisdiction, arbitrator selection process, and cost-sharing provisions.'
            },
            'Force Majeure': {
                'patterns': ['force majeure', 'act of god', 'unforeseen circumstances'],
                'risk_level': 'Low',
                'explanation': 'Force majeure clause covers unforeseen events. Standard provision but verify what events are covered and notice requirements.'
            },
            'Payment Terms': {
                'patterns': ['payment', 'salary', 'compensation', 'remuneration', 'wages'],
                'risk_level': 'Medium',
                'explanation': 'Payment and compensation terms. Verify payment frequency, deductions, and compliance with Payment of Wages Act.'
            },
            'Liability Limitation': {
                'patterns': ['limitation of liability', 'liability cap', 'maximum liability', 'aggregate liability'],
                'risk_level': 'High',
                'explanation': 'Liability limitation caps financial exposure. Verify caps are reasonable and do not unfairly disadvantage one party.'
            },
            'Renewal / Lock-in': {
                'patterns': ['auto-renewal', 'lock-in', 'lock in', 'minimum term', 'auto renewal'],
                'risk_level': 'High',
                'explanation': 'Auto-renewal or lock-in period restricts ability to exit the contract. Review duration and opt-out provisions carefully.'
            }
        }
        
        text_lower = text.lower()
        
        for clause_type, config in clause_patterns.items():
            for pattern in config['patterns']:
                if pattern in text_lower:
                    clauses.append({
                        'type': clause_type,
                        'risk_level': config['risk_level'],
                        'explanation': config['explanation']
                    })
                    break  # Only add once per clause type
        
        return clauses