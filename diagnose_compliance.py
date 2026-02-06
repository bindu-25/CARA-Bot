"""
CARA Bot - Compliance Checker Diagnostic v2
Tests all three services with the updated system message prompts.
Usage: python diagnose_compliance.py
"""

import os
import sys
import json
import re
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("CARA Bot - Service Diagnostic v2")
print("=" * 60)

# ─── TEST 1: Environment Variable ───
print("\n[TEST 1] Checking OPENROUTER_API_KEY...")
api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    print("  ❌ OPENROUTER_API_KEY not found!")
    sys.exit(1)
print(f"  ✅ API key found (starts with: {api_key[:8]}...)")

# ─── TEST 2: OpenAI Package ───
print("\n[TEST 2] Checking OpenAI package...")
try:
    from openai import OpenAI
    print("  ✅ OpenAI package imported")
except ImportError:
    print("  ❌ pip install openai")
    sys.exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

sample_contract = """
EMPLOYMENT AGREEMENT
This Employment Agreement is entered into on January 15, 2024, between:
Employer: TechVision Solutions Private Limited, Bangalore, Karnataka
Employee: Rajesh Kumar Sharma, residing at #42, MG Road, Bangalore

Term: 3 years commencing February 1, 2024, ending January 31, 2027.
Salary: INR 1,50,000 per month (gross), payable on last working day.
Medical Insurance: INR 5,00,000 annual coverage.
Performance Bonus: Up to 20% of annual base salary.

Non-Compete: Employee shall not work for any competing business within India
for a period of 2 years after termination of employment.

Termination: Either party may terminate with 3 months written notice.
Employee shall indemnify employer for any losses caused by misconduct.

Intellectual Property: All work created during employment belongs to employer.
Confidentiality: Employee must maintain confidentiality for 5 years post-employment.
Arbitration: Disputes to be resolved by arbitration in Bangalore.
"""


# ─── TEST 3: Compliance Check (new prompt) ───
print("\n[TEST 3] Testing COMPLIANCE CHECK with system message...")
try:
    response = client.chat.completions.create(
        model="anthropic/claude-opus-4.6",
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
                "content": f"""Contract text:
{sample_contract}

Return JSON:
{{"is_compliant": false, "applicable_laws": ["..."], "violations": [{{"law": "...", "issue": "..."}}], "recommendations": ["..."]}}"""
            }
        ],
        max_tokens=1500,
        temperature=0.1
    )
    
    content = response.choices[0].message.content.strip()
    finish_reason = getattr(response.choices[0], 'finish_reason', None)
    
    print(f"  Finish reason: {finish_reason}")
    print(f"  Response length: {len(content)} chars")
    
    # Clean
    if content.startswith("```"):
        content = re.sub(r'^```json?\s*|\s*```$', '', content, flags=re.MULTILINE).strip()
    
    result = json.loads(content)
    print(f"  ✅ COMPLIANCE CHECK PASSED!")
    print(f"  is_compliant: {result.get('is_compliant')}")
    print(f"  laws: {len(result.get('applicable_laws', []))}")
    print(f"  violations: {len(result.get('violations', []))}")
    print(f"  recommendations: {len(result.get('recommendations', []))}")
    
    # Check verbosity
    for v in result.get('violations', []):
        issue_words = len(v.get('issue', '').split())
        if issue_words > 35:
            print(f"  ⚠️ Violation too verbose ({issue_words} words): {v['issue'][:80]}...")
    
except json.JSONDecodeError as e:
    print(f"  ❌ JSON PARSE FAILED: {e}")
    print(f"  Response preview: {content[:300]}...")
except Exception as e:
    print(f"  ❌ ERROR: {e}")


# ─── TEST 4: Risk Assessment (new prompt) ───
print("\n[TEST 4] Testing RISK ASSESSMENT with system message...")
try:
    response = client.chat.completions.create(
        model="anthropic/claude-opus-4.6",
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
                "content": f"""Contract text:
{sample_contract}

Return JSON:
{{"overall_score": 65, "legal_risk": "Medium", "financial_risk": "High", "compliance_risk": "Low", "detailed_risks": [{{"category": "...", "description": "..."}}]}}"""
            }
        ],
        max_tokens=1500,
        temperature=0.1
    )
    
    content = response.choices[0].message.content.strip()
    finish_reason = getattr(response.choices[0], 'finish_reason', None)
    
    print(f"  Finish reason: {finish_reason}")
    print(f"  Response length: {len(content)} chars")
    
    if content.startswith("```"):
        content = re.sub(r'^```json?\s*|\s*```$', '', content, flags=re.MULTILINE).strip()
    
    result = json.loads(content)
    print(f"  ✅ RISK ASSESSMENT PASSED!")
    print(f"  overall_score: {result.get('overall_score')}")
    print(f"  legal_risk: {result.get('legal_risk')}")
    print(f"  financial_risk: {result.get('financial_risk')}")
    print(f"  compliance_risk: {result.get('compliance_risk')}")
    print(f"  detailed_risks: {len(result.get('detailed_risks', []))}")
    
except json.JSONDecodeError as e:
    print(f"  ❌ JSON PARSE FAILED: {e}")
    print(f"  Response preview: {content[:300]}...")
except Exception as e:
    print(f"  ❌ ERROR: {e}")


# ─── TEST 5: Contract Analysis (new prompt) ───
print("\n[TEST 5] Testing CONTRACT ANALYSIS with system message...")
try:
    response = client.chat.completions.create(
        model="anthropic/claude-opus-4.6",
        messages=[
            {
                "role": "system",
                "content": """You are a JSON API for contract analysis. 

ABSOLUTE RULES:
1. Output ONLY raw JSON. No markdown. No ```json blocks. No text before or after.
2. Each clause "explanation" must be under 25 words. One sentence only.
3. Each date entry: "Date - Brief Description" (under 15 words).
4. Each amount entry: "Amount - Purpose" (under 15 words).
5. No case law. No court citations. No legal precedents.
6. Exactly 5-7 clauses with mix of High/Medium/Low risk levels.
7. Total response must be under 1200 tokens."""
            },
            {
                "role": "user",
                "content": f"""Contract text:
{sample_contract}

Return JSON with these keys: contract_type, parties, dates, amounts, clauses.
- parties: ["Employer: Name", "Employee: Name"]
- dates: ["Date - Description"]
- amounts: ["Amount - Purpose"]
- clauses: [{{"type": "Clause Name", "risk_level": "High/Medium/Low", "explanation": "One short sentence"}}]

Minimum 5 clauses required."""
            }
        ],
        max_tokens=3000,
        temperature=0.1
    )
    
    content = response.choices[0].message.content.strip()
    finish_reason = getattr(response.choices[0], 'finish_reason', None)
    
    print(f"  Finish reason: {finish_reason}")
    print(f"  Response length: {len(content)} chars")
    
    if content.startswith("```"):
        content = re.sub(r'^```json?\s*|\s*```$', '', content, flags=re.MULTILINE).strip()
    
    result = json.loads(content)
    print(f"  ✅ CONTRACT ANALYSIS PASSED!")
    print(f"  contract_type: {result.get('contract_type')}")
    print(f"  parties: {len(result.get('parties', []))}")
    print(f"  dates: {len(result.get('dates', []))}")
    print(f"  amounts: {len(result.get('amounts', []))}")
    print(f"  clauses: {len(result.get('clauses', []))}")
    
    # Show clauses
    for c in result.get('clauses', []):
        risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(c.get('risk_level', ''), '⚪')
        print(f"    {risk_emoji} {c.get('type')}: {c.get('explanation', '')[:80]}")

except json.JSONDecodeError as e:
    print(f"  ❌ JSON PARSE FAILED: {e}")
    print(f"  Response preview: {content[:500]}...")
except Exception as e:
    print(f"  ❌ ERROR: {e}")


print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
print("If all 3 tests show ✅, your app should work correctly.")
print("Replace the service files and restart Streamlit.")