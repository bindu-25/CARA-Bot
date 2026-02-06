
# ⚖️ CARA Bot – Contract Analysis & Risk Assessment for SMEs

CARA (Contract Analysis & Risk Assessment) Bot is an AI-powered legal assistant designed to help **Indian Small and Medium Enterprises (SMEs)** understand contracts, identify risks, and check compliance with Indian laws through automated legal NLP techniques.

---

## 🚀 Core Objectives

* Simplify complex legal contracts for non-legal users
* Identify legal, financial, and compliance risks early
* Highlight ambiguous and high-risk clauses
* Provide SME-friendly insights and templates
* Enable interactive Q&A on uploaded contracts

---

## 🧠 Core Legal NLP Capabilities

### 1. Contract Understanding

* Automatic **contract type classification** (e.g., Service Agreement, Employment Agreement)
* Extraction of:

  * Parties involved
  * Key dates
  * Financial amounts
  * Clause structure

### 2. Clause-Level Analysis

Each clause is analyzed and tagged with:

* **Clause Type** (Termination, Payment, IP, Non-Compete, etc.)
* **Risk Level** (High / Medium / Low)
* **Clause Nature** (Right / Obligation / Prohibition)
* **Ambiguity Detection**

  * Example: “Amount not specified”, “No defined scope”

### 3. Risk Assessment Engine

* Overall **Risk Score (0–100)**
* Separate assessment for:

  * Legal Risk
  * Financial Risk
  * Compliance Risk
* Explicit detection of risk flags:

  * Penalty clauses
  * Unilateral termination
  * Missing liability caps
  * Indemnity clauses
  * Non-compete & IP transfer clauses
  * Auto-renewal risks

### 4. Compliance Checking (India-focused)

* Checks alignment with:

  * Indian Contract Act, 1872
  * Employment and labor regulations (where applicable)
* Highlights violations and compliance gaps
* Provides actionable recommendations

---

## 📊 SME-Focused Features

### SME-Friendly Contract Templates

* Downloadable templates:

  * Employment Agreement (SME)
  * NDA (SME)
* Designed to reflect balanced, low-risk clauses

### Renegotiation Suggestions

* Clause-level renegotiation hints for risky or ambiguous clauses
* Practical alternatives instead of legal jargon

---

## 💬 Interactive Contract Q&A

* Ask natural language questions such as:

  * “Who can terminate the contract?”
  * “Is there any non-compete clause?”
  * “What happens if payment is delayed?”
* Answers are generated **strictly based on the uploaded contract text**

---

## 📥 Export & Reporting

* Export full analysis as a **PDF report**
* Includes:

  * Contract overview
  * Risk scores
  * Clause analysis
  * Compliance findings

---

## 🖥️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **LLM:** Claude Opus 4.6 (via OpenRouter)
* **PDF Generation:** ReportLab
* **File Handling:** PDF / DOCX / TXT
* **Design:** Custom CSS for professional legal UI

---

## 📁 Project Structure (Simplified)

```
app/
├── main.py                     # Streamlit UI
├── services/
│   ├── contract_analyzer.py    # Clause & contract analysis
│   ├── risk_scorer.py          # Risk assessment logic
│   └── compliance_checker.py   # Legal compliance checks
├── utils/
│   ├── file_handler.py         # File text extraction
│   ├── pdf_exporter.py         # PDF report generation
│   └── json_utils.py
├── templates/
│   ├── employment_sme.docx
│   └── nda_sme.docx
```

---

## 🧪 Supported File Formats

* PDF (`.pdf`)
* Word (`.docx`)
* Text (`.txt`)
* Max file size: **200MB**

---

## 🔒 Data & Privacy

* Uploaded contracts are processed in-session
* No permanent storage of documents
* API keys managed via environment variables

---

## 🎯 Intended Users

* SME founders & managers
* Startup legal teams
* Business analysts
* Legal-tech researchers
* Academic or applied NLP projects in law

---

## 📌 Disclaimer

CARA Bot is an **assistive legal analysis tool** and does not replace professional legal advice. Users should consult a qualified lawyer for final decisions.

---

If you want, I can also provide:

* 📄 **Academic-style README**
* 🧪 **Testing & evaluation section**
* 🧠 **Architecture diagram explanation**
* 🎓 **Resume / project description version**

Just tell me.
