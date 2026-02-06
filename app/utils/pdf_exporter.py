"""
PDF Exporter for CARA Bot
Generates a professional PDF report from contract analysis results.
Uses reportlab (available on most Python installations).
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def export_pdf(analysis, risk_assessment=None, compliance=None, filename=None):
    """
    Generate a PDF report from CARA Bot analysis results.

    Args:
        analysis: dict with contract_type, parties, dates, amounts, clauses
        risk_assessment: dict with overall_score, legal_risk, financial_risk, etc.
        compliance: dict with is_compliant, violations, recommendations
        filename: optional filename (not used — returns bytes)

    Returns:
        bytes: PDF file content as bytes (ready for st.download_button)
    """

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    # ── Styles ──
    styles = getSampleStyleSheet()

    style_title = ParagraphStyle(
        'CTitle', parent=styles['Title'],
        fontSize=22, textColor=HexColor('#1e3a8a'),
        spaceAfter=4, alignment=TA_CENTER,
    )
    style_subtitle = ParagraphStyle(
        'CSub', parent=styles['Normal'],
        fontSize=11, textColor=HexColor('#667eea'),
        alignment=TA_CENTER, spaceAfter=12,
    )
    style_h2 = ParagraphStyle(
        'CH2', parent=styles['Heading2'],
        fontSize=14, textColor=HexColor('#1e3a8a'),
        spaceBefore=14, spaceAfter=6,
        borderPadding=(0, 0, 2, 0),
    )
    style_h3 = ParagraphStyle(
        'CH3', parent=styles['Heading3'],
        fontSize=12, textColor=HexColor('#764ba2'),
        spaceBefore=10, spaceAfter=4,
    )
    style_body = ParagraphStyle(
        'CBody', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=HexColor('#1e293b'),
    )
    style_bullet = ParagraphStyle(
        'CBullet', parent=style_body,
        leftIndent=16, bulletIndent=6,
        spaceBefore=2, spaceAfter=2,
    )
    style_risk_high = ParagraphStyle('RHigh', parent=style_body, textColor=HexColor('#dc2626'))
    style_risk_med = ParagraphStyle('RMed', parent=style_body, textColor=HexColor('#d97706'))
    style_risk_low = ParagraphStyle('RLow', parent=style_body, textColor=HexColor('#059669'))
    style_footer = ParagraphStyle(
        'CFooter', parent=styles['Normal'],
        fontSize=8, textColor=HexColor('#94a3b8'),
        alignment=TA_CENTER,
    )

    elements = []

    # ── Header ──
    elements.append(Paragraph("⚖️  CARA Bot — Contract Analysis Report", style_title))
    elements.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        style_subtitle,
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=HexColor('#667eea'), spaceAfter=10))

    # ── Contract Overview ──
    contract_type = analysis.get('contract_type', 'Unknown')
    risk_score = risk_assessment.get('overall_score', 'N/A') if risk_assessment else 'N/A'
    compliant_str = 'N/A'
    if compliance:
        compliant_str = "✅ Compliant" if compliance.get('is_compliant', False) else "⚠️ Issues Found"

    overview_data = [
        ['Contract Type', 'Risk Score', 'Compliance Status'],
        [contract_type, f"{risk_score}/100" if risk_score != 'N/A' else 'N/A', compliant_str],
    ]
    overview_table = Table(overview_data, colWidths=[170, 170, 170])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 10))

    # ── Parties ──
    parties = analysis.get('parties', [])
    if parties:
        elements.append(Paragraph("👥 Parties Involved", style_h2))
        for p in parties:
            p_str = str(p).strip()
            if ':' in p_str:
                role, name = p_str.split(':', 1)
                elements.append(Paragraph(f"<b>{role.strip()}:</b> {name.strip()}", style_bullet))
            else:
                elements.append(Paragraph(f"• {p_str}", style_bullet))

    # ── Key Dates ──
    dates = analysis.get('dates', [])
    if dates:
        elements.append(Paragraph("📅 Key Dates", style_h2))
        for d in dates:
            elements.append(Paragraph(f"• {d}", style_bullet))

    # ── Financial Terms ──
    amounts = analysis.get('amounts', [])
    if amounts:
        elements.append(Paragraph("💰 Financial Terms", style_h2))
        for a in amounts:
            elements.append(Paragraph(f"• {a}", style_bullet))

    # ── Clause Analysis ──
    clauses = analysis.get('clauses', [])
    if clauses:
        elements.append(Paragraph("🔍 Clause Analysis", style_h2))
        for clause in clauses:
            risk = clause.get('risk_level', 'Unknown')
            ctype = clause.get('type', 'Clause')
            explanation = clause.get('explanation', '')
            indicator = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(risk, '⚪')
            risk_style = {'High': style_risk_high, 'Medium': style_risk_med, 'Low': style_risk_low}.get(risk, style_body)

            block = []
            block.append(Paragraph(f"<b>{indicator} {ctype}</b>  —  {risk} Risk", risk_style))
            if explanation:
                block.append(Paragraph(explanation, style_bullet))
            block.append(Spacer(1, 4))
            elements.append(KeepTogether(block))

    # ── Risk Assessment ──
    if risk_assessment:
        elements.append(Paragraph("⚠️ Risk Assessment", style_h2))
        risk_data = [
            ['Legal Risk', 'Financial Risk', 'Compliance Risk', 'Overall Score'],
            [
                risk_assessment.get('legal_risk', 'N/A'),
                risk_assessment.get('financial_risk', 'N/A'),
                risk_assessment.get('compliance_risk', 'N/A'),
                f"{risk_assessment.get('overall_score', 'N/A')}%",
            ],
        ]
        risk_table = Table(risk_data, colWidths=[127, 127, 127, 127])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f59e0b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#fffbeb')]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(risk_table)

        detailed_risks = risk_assessment.get('detailed_risks', [])
        if detailed_risks:
            elements.append(Paragraph("Risk Breakdown", style_h3))
            for r in detailed_risks:
                cat = r.get('category', 'Risk')
                desc = r.get('description', '')
                elements.append(Paragraph(f"<b>{cat}:</b> {desc}", style_bullet))

    # ── Compliance Check ──
    if compliance:
        elements.append(Paragraph("📋 Compliance Check", style_h2))
        is_ok = compliance.get('is_compliant', False)
        if is_ok:
            elements.append(Paragraph("✅ No major compliance issues found.", style_body))
        else:
            violations = compliance.get('violations', [])
            if violations:
                elements.append(Paragraph("<b>Issues Found:</b>", style_body))
                for v in violations:
                    law = v.get('law', 'Unknown')
                    issue = v.get('issue', 'N/A')
                    elements.append(Paragraph(f"<b>{law}:</b> {issue}", style_bullet))

        recs = compliance.get('recommendations', [])
        if recs:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("💡 Recommendations", style_h3))
            for i, rec in enumerate(recs, 1):
                elements.append(Paragraph(f"{i}. {rec}", style_bullet))

    # ── Footer ──
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#cbd5e1'), spaceAfter=6))
    elements.append(Paragraph(
        "Generated by CARA Bot — AI Legal Assistant for Indian SMEs  |  Powered by Claude Opus 4.6  |  © 2026",
        style_footer,
    ))
    elements.append(Paragraph(
        "⚠️ This report is AI-generated and should not be treated as legal advice. Please consult a qualified legal professional.",
        style_footer,
    ))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()