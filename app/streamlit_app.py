import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import sys
from app.utils.pdf_exporter import export_pdf


# Load environment variables FIRST
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.contract_analyzer import ContractAnalyzer
from app.services.risk_scorer import RiskScorer
from app.services.compliance_checker import ComplianceChecker
from app.utils.file_handler import FileHandler

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="CARA Bot - Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS 
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .main > div {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] *,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] em,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stMarkdown *,
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown span,
    [data-testid="stSidebar"] .stMarkdown strong,
    [data-testid="stSidebar"] .stMarkdown em,
    [data-testid="stSidebar"] .stMarkdown li {
        color: white !important;
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] select {
        background-color:#4a5568 !important;
        color: white !important;
        border: 2px solid #667eea !important;
        border-radius: 5px !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        color: #f0f0f0 !important;
        background-color: #4a5568 !important;
    }
    [data-testid="stSidebar"] .stSelectbox option {
        background-color: white !important;
        color: #1e3a8a !important;
    }
    [data-testid="stSidebar"] .stSelectbox [role="button"] {
        color: #1e3a8a !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }
    [data-testid="stSidebar"] input[type="radio"] {
        width: 18px !important;
        height: 18px !important;
        accent-color: #667eea !important;
        cursor: pointer !important;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: white !important;
        font-size: 15px !important;
    }
    [data-testid="stSidebar"] a {
        color: #4facfe !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] {
        background-color: #e5e7eb !important;
        border: 2px dashed #667eea !important;
        border-radius: 10px !important;
        padding: 30px !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] p,
    .stFileUploader [data-testid="stFileUploaderDropzone"] span {
        color: white !important;
        font-size: 16px !important;
    }
    .stFileUploader [data-testid="stFileUploaderDropzone"] svg {
        fill: white !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: white !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] svg {
        fill: white !important;
    }
    a::before, a::after {
        content: none !important;
        display: none !important;
    }
    .stMarkdown a {
        text-decoration: none !important;
    }
    p, li, div, span {
        color: #1e3a8a !important;
    }
    .stMarkdown p {
        color: #1e3a8a !important;
        font-size: 16px;
    }
    .stMarkdown li {
        color: #1e3a8a !important;
        font-size: 16px;
    }
    .streamlit-expanderHeader {
        background-color: #f3f4f6;
        border-radius: 5px;
        font-weight: bold;
        font-size: 18px !important;
    }
    .streamlit-expanderContent {
        color: #1e3a8a !important;
        font-size: 16px !important;
    }
    .streamlit-expanderContent p {
        font-size: 16px !important;
    }
    h1 {
        color: #1e3a8a;
        font-family: 'Segoe UI', sans-serif;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    h2, h3 {
        color: #1e3a8a;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        text-align: center;
        min-height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card h3 {
        color: white !important;
        margin-bottom: 10px;
    }
    .metric-card p {
        color: white !important;
    }
    .risk-high { color: #dc2626; font-weight: bold; }
    .risk-medium { color: #f59e0b; font-weight: bold; }
    .risk-low { color: #10b981; font-weight: bold; }
    .stButton>button {
        background: #e5e7eb !important;
        color: white !important;
        border: none;
        padding: 10px 30px;
        border-radius: 5px;
        font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    [data-testid="stBottomBlockContainer"],
    [data-testid="stBottom"],
    .element-container:empty {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
    }
    [data-testid="stMarkdown"] a::before,
    [data-testid="stMarkdown"] a::after,
    a::before, a::after {
        content: none !important;
        display: none !important;
    }
    /* Download button text WHITE */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #5a6fd6 0%, #6a4292 100%) !important;
        color: white !important;
    }
    .stDownloadButton > button p,
    .stDownloadButton > button span,
    .stDownloadButton > button div {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# TRANSLATIONS
# ============================================
TRANSLATIONS = {
    "English": {
        "title": "⚖️ CARA Bot - AI Legal Assistant for Indian SMEs",
        "subtitle": "Contract Analysis • Risk Assessment • Compliance Checking",
        "upload": "📄 Upload Contract Document",
        "analyze": "🔍 Analyze Contract",
        "language": "🌐 Language",
        "contract_type": "Contract Type",
        "parties": "Parties Involved",
        "dates": "Key Dates",
        "financial": "Financial Terms",
        "risk_score": "Risk Score",
        "clauses": "Clause Analysis",
        "compliance": "Compliance Status",
        "get_details": "Get Detailed Analysis",
        "detailed_explanation": "📖 Detailed Explanation",
        "potential_issues": "⚠️ Potential Issues",
        "recommendations": "✅ Recommendations",
        "applicable_laws": "📚 Relevant Indian Laws",
        "ask_question": "💬 Ask About This Contract"
    },
    "हिंदी (Hindi)": {
        "title": "⚖️ CARA Bot - AI कानूनी सहायक भारतीय SME के लिए",
        "subtitle": "अनुबंध विश्लेषण • जोखिम मूल्यांकन • अनुपालन जांच",
        "upload": "📄 अनुबंध दस्तावेज़ अपलोड करें",
        "analyze": "🔍 अनुबंध का विश्लेषण करें",
        "language": "🌐 भाषा",
        "contract_type": "अनुबंध प्रकार",
        "parties": "पक्षकार",
        "dates": "महत्वपूर्ण तिथियां",
        "financial": "वित्तीय शर्तें",
        "risk_score": "जोखिम स्कोर",
        "clauses": "खंड विश्लेषण",
        "compliance": "अनुपालन स्थिति",
        "get_details": "विस्तृत विश्लेषण प्राप्त करें",
        "detailed_explanation": "📖 विस्तृत व्याख्या",
        "potential_issues": "⚠️ संभावित समस्याएं",
        "recommendations": "✅ सिफारिशें",
        "applicable_laws": "📚 प्रासंगिक भारतीय कानून",
        "ask_question": "💬 इस अनुबंध के बारे में पूछें"
    }
}

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding:10px;'>
        <span style='font-size: 60px;'>⚖️</span>
        <h3 style='color: white; margin-top: 8px;'>CARA Bot</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <style>
        div[data-testid="stSidebar"] input[type="radio"] {
            width: 20px !important; height: 20px !important;
            min-width: 20px !important; min-height: 20px !important;
            accent-color: #667eea !important; cursor: pointer !important;
            opacity: 1 !important; visibility: visible !important;
            display: inline-block !important;
        }
        div[data-testid="stSidebar"] .stRadio label { color: white !important; cursor: pointer !important; }
        div[data-testid="stSidebar"] .stRadio label span { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📋 Select Analysis Type")
    analysis_type = st.selectbox(
        "", ["📄 Full Contract Analysis", "⚠️ Risk Assessment Only", "📋 Compliance Check Only"],
        index=0, label_visibility="collapsed", key="analysis_selector"
    )

    st.markdown("---")

    st.markdown("""
    <style>
        div[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] { background-color: #f0f0f0 !important; }
        div[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div { color: #1e3a8a !important; background-color: #4a5568 !important; }
        div[data-testid="stSidebar"] .stSelectbox [role="button"] { color: #1e3a8a !important; background-color: #4a5568 !important; }
        div[data-testid="stSidebar"] .stSelectbox [role="button"] span { color: #1e3a8a !important; }
        div[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] [role="button"] > div { color: #1e3a8a !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### 🌐 Language / भाषा")
    language = st.selectbox("", ["English", "हिंदी (Hindi)"], index=0, label_visibility="collapsed")
    t = TRANSLATIONS[language]

    st.markdown("---")

    st.markdown("### 📖 About CARA Bot")
    st.markdown("""
    CARA (Contract Analysis & Risk Assessment) Bot is an AI-powered legal assistant specifically designed for Indian Small and Medium Enterprises (SMEs).

    **What Makes CARA Special:**

    📚 **Indian Law Focused**

    💡 **Smart Analysis**

    🗣️ **Bilingual Support**

    ⚡ **AI Model- Claude Opus 4.6**

    🔒 **Your Data is Safe**
    """)

    st.markdown("---")

    st.markdown("### 📁 Supported Formats")
    st.markdown("""
    ✅ PDF (.pdf)

    ✅ Word (.docx)

    ✅ Text (.txt)

    Max File Size: 200MB
    """)

    st.markdown("---")

    st.markdown("""
    <div style='text-align: center; padding: 20px 0; border-top: 1px solid rgba(255,255,255,0.2);'>
        <p style='font-size: 12px;'>Powered by: Claude Opus 4.6 AI</p>
        <p style='font-size: 12px;'>© 2026 CARA Bot</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN CONTENT
# ============================================
st.markdown("""
<h1 style='text-align: center; color: #1e3a8a; font-size: 2.5rem; margin-bottom: 5px; border: none;'>
    ⚖️ CARA Bot
</h1>
<p style='text-align: center; color: #1e3a8a; font-size: 1.2rem; margin-top: 5px; margin-bottom: 5px;'>
    AI Legal Assistant for Indian SMEs
</p>
<p style='text-align: center; color: #667eea; font-size: 1rem; margin-top: 5px;'>
    Contract Analysis • Risk Assessment • Compliance Checking
</p>
""", unsafe_allow_html=True)

st.markdown("---")

uploaded_file = st.file_uploader(
    "", type=['pdf', 'docx', 'txt'],
    help="Upload your contract in PDF, DOCX, or TXT format",
    label_visibility="collapsed"
)

if uploaded_file:
    st.success(f"📁 File uploaded: {uploaded_file.name}")

    if st.button(t["analyze"], type="primary"):
        st.session_state["run_analysis"] = True

    # ─── RUN ANALYSIS ───
    if st.session_state.get("run_analysis"):
        with st.spinner("🔄 Analyzing contract..."):
            try:
                file_handler = FileHandler()
                contract_text = file_handler.extract_text(uploaded_file)

                if not contract_text:
                    st.error("❌ Could not extract text from file")
                    st.stop()

                st.session_state['contract_text'] = contract_text

                analyzer = ContractAnalyzer()
                risk_scorer = RiskScorer()
                compliance_checker = ComplianceChecker()

                st.info(f"🔄 Running: **{analysis_type}** in **{language}**")

                analysis = None
                risk_assessment = None
                compliance = None

                if analysis_type == "📄 Full Contract Analysis":
                    analysis = analyzer.analyze(contract_text, language=language)
                    risk_assessment = risk_scorer.assess(contract_text, language=language)
                    compliance = compliance_checker.check(contract_text, language=language)
                elif analysis_type == "⚠️ Risk Assessment Only":
                    analysis = analyzer.analyze(contract_text, language=language)
                    risk_assessment = risk_scorer.assess(contract_text, language=language)
                elif analysis_type == "📋 Compliance Check Only":
                    analysis = analyzer.analyze(contract_text, language=language)
                    compliance = compliance_checker.check(contract_text, language=language)

                st.session_state['analysis'] = analysis
                st.session_state['risk_assessment'] = risk_assessment
                st.session_state['compliance'] = compliance
                st.session_state['analyzer'] = analyzer

            except Exception as e:
                st.error(f"❌ Analysis failed: {e}")
                import traceback
                with st.expander("Technical Details"):
                    st.code(traceback.format_exc())

    # ═══════════════════════════════════════════
    # DISPLAY RESULTS (all inside uploaded_file block)
    # ═══════════════════════════════════════════
    if st.session_state.get('analysis'):
        analysis = st.session_state['analysis']
        risk_assessment = st.session_state.get('risk_assessment')
        compliance = st.session_state.get('compliance')
        contract_text = st.session_state.get('contract_text', '')

        # ─── SME TEMPLATES ───
        st.markdown("## 📄 SME-Friendly Contract Templates")
        try:
            st.download_button(
                "Download Employment Agreement (SME)",
                open("app/templates/employment_sme.docx", "rb"),
                file_name="Employment_Agreement_SME.docx"
            )
            st.download_button(
                "Download NDA (SME)",
                open("app/templates/nda_sme.docx", "rb"),
                file_name="NDA_SME.docx"
            )
        except FileNotFoundError:
            st.caption("Template files not found in app/templates/")

        # ─── DASHBOARD METRICS ───
        st.markdown("## 📊 Contract Overview")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📄 {t['contract_type']}</h3>
                <p style="font-size: 18px;">{analysis.get('contract_type', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            risk_score = risk_assessment.get('overall_score', 50) if risk_assessment else 0
            risk_display = f"{risk_score}/100" if risk_assessment else "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <h3>⚠️ {t['risk_score']}</h3>
                <p style="font-size: 32px; color: white;">{risk_display}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            is_compliant = compliance.get('is_compliant', False) if compliance else True
            compliance_text = "✅ Compliant" if is_compliant else "⚠️ Issues"
            if not compliance:
                compliance_text = "N/A"
            st.markdown(f"""
            <div class="metric-card">
                <h3>📋 {t['compliance']}</h3>
                <p style="font-size: 18px;">{compliance_text}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # ─── PARTIES, DATES, FINANCIAL TERMS ───
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"### 👥 {t['parties']}")
            st.caption("The individuals, companies, or entities named in this contract and their roles.")
            parties = analysis.get('parties', [])
            if parties and len(parties) > 0:
                for party in parties:
                    party_str = str(party).strip()
                    if ':' in party_str:
                        role_part, name_part = party_str.split(':', 1)
                        st.markdown(f"**{role_part.strip()}:** {name_part.strip()}")
                    else:
                        st.markdown(f"• {party_str}")
            else:
                st.info("No parties identified")

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"### 📅 {t['dates']}")
            st.caption("Important dates such as start date, end date, renewal, and deadline milestones.")
            dates = analysis.get('dates', [])
            if dates and len(dates) > 0:
                for date in dates:
                    st.markdown(f"• {date}")
            else:
                st.info("No dates found")

        with col_right:
            st.markdown(f"### 💰 {t['financial']}")
            st.caption("Monetary values, payment schedules, penalties, fees, and compensation terms found in the contract.")
            amounts = analysis.get('amounts', [])
            if amounts and len(amounts) > 0:
                for amount in amounts:
                    st.markdown(f"• {amount}")
            else:
                st.info("No financial terms found")

        st.markdown("---")

        # ─── CLAUSE ANALYSIS ───
        st.markdown(f"## 🔍 {t['clauses']}")
        st.caption("Each clause is analyzed for risk level (🟢 Low, 🟡 Medium, 🔴 High). Click any clause to expand, then use 'Get Detailed Analysis' for a deep-dive with issues, recommendations, and applicable Indian laws.")

        clauses = analysis.get('clauses', [])

        # FALLBACK 1: NLP extraction
        if not clauses or len(clauses) == 0:
            analyzer_obj = st.session_state.get('analyzer')
            if analyzer_obj and hasattr(analyzer_obj, 'extract_clauses'):
                clauses = analyzer_obj.extract_clauses(contract_text)

        # FALLBACK 2: Generic clauses
        if not clauses or len(clauses) == 0:
            clauses = [
                {"type": "General Terms & Conditions", "risk_level": "Medium",
                 "explanation": "Standard contractual terms detected. Review recommended to ensure fairness."},
                {"type": "Obligations & Liabilities", "risk_level": "Medium",
                 "explanation": "Contract contains obligations for one or more parties. Verify balance."},
                {"type": "Termination Provisions", "risk_level": "Medium",
                 "explanation": "Review termination terms for adequate notice periods and fair exit conditions."}
            ]

        for idx, clause in enumerate(clauses):
            risk_level = clause.get('risk_level', 'Unknown')
            risk_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(risk_level, "⚪")
            clause_type = clause.get('type', 'Unknown Clause')
            explanation = clause.get('explanation', 'No explanation')

            with st.expander(f"{risk_emoji} **{clause_type}** - {risk_level} Risk"):
                st.markdown(f"**Summary:** {explanation}")
                st.markdown("<br>", unsafe_allow_html=True)

                button_key = f"detail_btn_{idx}"
                if st.button(f"🔍 {t['get_details']}", key=button_key):
                    st.session_state[f'show_details_{idx}'] = True

                if st.session_state.get(f'show_details_{idx}', False):
                    with st.spinner("Loading detailed analysis..."):
                        analyzer_obj = st.session_state.get('analyzer')
                        if analyzer_obj:
                            detailed = analyzer_obj.get_detailed_analysis(clause, contract_text, language)
                        else:
                            detailed = {
                                'explanation': 'Analyzer not available. Please re-run analysis.',
                                'issues': 'N/A', 'recommendations': 'N/A', 'applicable_laws': 'N/A'
                            }

                        st.markdown("---")
                        st.markdown(f"#### {t['detailed_explanation']}")
                        st.write(detailed.get('explanation', 'N/A'))

                        st.markdown(f"#### {t['potential_issues']}")
                        st.warning(detailed.get('issues', 'N/A'))

                        st.markdown(f"#### {t['recommendations']}")
                        st.success(detailed.get('recommendations', 'N/A'))

                        st.markdown(f"#### {t['applicable_laws']}")
                        st.info(detailed.get('applicable_laws', 'N/A'))

        st.markdown("---")

        # ─── RISK ASSESSMENT ───
        if analysis_type in ["📄 Full Contract Analysis", "⚠️ Risk Assessment Only"] and risk_assessment:
            st.markdown("## ⚠️ Risk Assessment")

            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("⚖️ Legal Risk", risk_assessment.get('legal_risk', 'Medium'))
            with rc2:
                st.metric("💰 Financial Risk", risk_assessment.get('financial_risk', 'Medium'))
            with rc3:
                st.metric("📋 Compliance Risk", risk_assessment.get('compliance_risk', 'Medium'))

            st.markdown(f"#### Overall Risk Score: **{risk_score}%**")

            detailed_risks = risk_assessment.get('detailed_risks', [])
            if detailed_risks and len(detailed_risks) > 0:
                st.markdown("### 📋 Risk Breakdown")
                for risk in detailed_risks:
                    category = risk.get('category', 'Risk Category')
                    description = risk.get('description', 'No description available')
                    st.warning(f"**{category}:** {description}")
            else:
                st.markdown("### 📋 Risk Breakdown")
                legal = risk_assessment.get('legal_risk', 'Medium')
                financial = risk_assessment.get('financial_risk', 'Medium')
                compliance_r = risk_assessment.get('compliance_risk', 'Medium')
                st.warning(f"**Legal Risk ({legal}):** Review contract for enforceability under Indian law.")
                st.warning(f"**Financial Risk ({financial}):** Examine payment terms, penalties, and liability caps.")
                st.warning(f"**Compliance Risk ({compliance_r}):** Verify compliance with Indian Contract Act 1872.")

            st.markdown("---")

        # ─── COMPLIANCE CHECK ───
        if analysis_type in ["📄 Full Contract Analysis", "📋 Compliance Check Only"] and compliance:
            st.markdown("## 📋 Compliance Check")

            is_compliant = compliance.get('is_compliant', False)

            if not is_compliant:
                violations = compliance.get('violations', [])
                if violations:
                    st.error("⚠️ **Issues Found:**")
                    for v in violations:
                        st.markdown(f"• **{v.get('law', 'Unknown')}:** {v.get('issue', 'N/A')}")
            else:
                st.success("✅ **No major issues**")

            recommendations = compliance.get('recommendations', [])
            if recommendations:
                st.markdown("### 💡 Recommendations")
                for i, rec in enumerate(recommendations, 1):
                    st.info(f"{i}. {rec}")

            st.markdown("---")

        # ─── Q&A FEATURE ───
        st.markdown(f"## {t['ask_question']}")

        user_question = st.text_input(
            "Ask me anything about this contract:",
            key="chat_input",
            placeholder="e.g. What is the termination notice period? / Are there any penalty clauses? / Who bears the liability?"
        )

        if st.button("Ask"):
            if user_question.strip():
                with st.spinner("🤔 Thinking..."):
                    try:
                        from openai import OpenAI
                        import os

                        client = OpenAI(
                            base_url="https://openrouter.ai/api/v1",
                            api_key=os.getenv("OPENROUTER_API_KEY")
                        )

                        response = client.chat.completions.create(
                            model="anthropic/claude-opus-4.6",
                            messages=[{
                                "role": "user",
                                "content": f"""Based on this contract, answer the question:

CONTRACT:
{contract_text[:4000]}

QUESTION: {user_question}

Provide a clear, concise answer with relevant contract clauses."""
                            }],
                            max_tokens=1000
                        )

                        st.success(f"**Answer:** {response.choices[0].message.content}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        with st.expander("Technical Details"):
                            import traceback
                            st.code(traceback.format_exc())

        # ─── DOWNLOAD ANALYSIS REPORT ───
        st.markdown("---")
        st.markdown("## 📥 Download Analysis Report")
        st.caption("Download the complete contract analysis as a professionally formatted PDF document.")

        try:
            pdf_bytes = export_pdf(
                analysis=analysis,
                risk_assessment=risk_assessment,
                compliance=compliance
            )
            file_label = uploaded_file.name.rsplit('.', 1)[0] if uploaded_file else "contract"
            st.download_button(
                label="📄 Download Full Analysis (PDF)",
                data=pdf_bytes,
                file_name=f"CARA_Analysis_{file_label}.pdf",
                mime="application/pdf",
                key="download_pdf_btn"
            )
        except Exception as e:
            st.error(f"❌ Could not generate PDF: {e}")
            with st.expander("Technical Details"):
                import traceback
                st.code(traceback.format_exc())

else:
    # ═══════════════════════════════════════════
    # WELCOME SCREEN
    # ═══════════════════════════════════════════
    st.info("👆 Upload a contract to begin")

    st.markdown("---")
    st.markdown("<h2 style='color: #1e3a8a; text-align: center;'>✨ What CARA Bot Can Do</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px; border-radius: 10px; color: white; text-align: center; min-height: 220px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='color: white; font-size: 48px;'>📄</h2>
            <h3 style='color: white; margin-bottom: 15px;'>Contract Analysis</h3>
            <p style='color: white;'>Extract parties, dates, financial terms</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    padding: 30px; border-radius: 10px; color: white; text-align: center; min-height: 220px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='color: white; font-size: 48px;'>⚠️</h2>
            <h3 style='color: white; margin-bottom: 15px;'>Risk Assessment</h3>
            <p style='color: white;'>Identify legal & financial risks</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                    padding: 30px; border-radius: 10px; color: white; text-align: center; min-height: 220px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
            <h2 style='color: white; font-size: 48px;'>📋</h2>
            <h3 style='color: white; margin-bottom: 15px;'>Compliance Check</h3>
            <p style='color: white;'>Verify Indian law compliance</p>
        </div>
        """, unsafe_allow_html=True)