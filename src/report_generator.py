"""PDF report generator using ReportLab."""

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)


def generate_report(analysis_results: dict) -> bytes:
    """Generate a PDF analysis report.

    Args:
        analysis_results: Dict containing all analysis outputs:
            - semantic_score
            - skill_comparison
            - gap_analysis
            - recommendations
            - roasts (optional)

    Returns:
        PDF file as bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a2e'),
        spaceAfter=6,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#16213e'),
        spaceBefore=16,
        spaceAfter=8,
        borderWidth=0,
        borderPadding=0,
    )
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        leading=14,
        spaceAfter=6,
    )
    small_style = ParagraphStyle(
        'SmallText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#999999'),
        alignment=TA_RIGHT,
    )

    # --- Title Section ---
    elements.append(Paragraph('Resume Roast AI', title_style))
    elements.append(Paragraph('Resume Analysis Report', subtitle_style))
    elements.append(Paragraph(
        f'Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}',
        small_style
    ))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(
        width='100%', thickness=1,
        color=colors.HexColor('#e0e0e0'),
        spaceAfter=16,
    ))

    # --- Score Overview ---
    semantic = analysis_results.get('semantic_score', {})
    skill_comp = analysis_results.get('skill_comparison', {})

    elements.append(Paragraph('Score Overview', heading_style))

    score_data = [
        ['Metric', 'Score', 'Interpretation'],
        [
            'Semantic Match',
            f"{semantic.get('percentage', 0):.1f}%",
            semantic.get('interpretation', 'N/A')[:80],
        ],
        [
            'Skill Coverage',
            skill_comp.get('coverage_percentage', '0%'),
            f"{len(skill_comp.get('matched', set()))} of "
            f"{len(skill_comp.get('matched', set())) + len(skill_comp.get('missing', set()))} "
            f"required skills matched",
        ],
    ]

    score_table = Table(score_data, colWidths=[100, 80, 310])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [
            colors.white, colors.HexColor('#f8f9fa')
        ]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(score_table)
    elements.append(Spacer(1, 16))

    # --- Matched Skills ---
    matched_details = skill_comp.get('matched_details', [])
    if matched_details:
        elements.append(Paragraph('Matched Skills', heading_style))
        for d in matched_details:
            elements.append(Paragraph(
                f"\u2713 <b>{d['skill']}</b> ({d['category']})",
                body_style
            ))
        elements.append(Spacer(1, 8))

    # --- Missing Skills ---
    missing_details = skill_comp.get('missing_details', [])
    if missing_details:
        elements.append(Paragraph('Missing Skills', heading_style))
        for d in missing_details:
            elements.append(Paragraph(
                f"\u2717 <b>{d['skill']}</b> ({d['category']})",
                body_style
            ))
        elements.append(Spacer(1, 8))

    # --- Additional Resume Skills ---
    additional_details = skill_comp.get('additional_details', [])
    if additional_details:
        elements.append(Paragraph('Additional Resume Skills', heading_style))
        for d in additional_details:
            elements.append(Paragraph(
                f"\u25CB <b>{d['skill']}</b> ({d['category']})",
                body_style
            ))
        elements.append(Spacer(1, 8))

    # --- Strengths ---
    gap = analysis_results.get('gap_analysis', {})
    strengths = gap.get('strengths', [])
    if strengths:
        elements.append(Paragraph('Strengths', heading_style))
        for s in strengths:
            elements.append(Paragraph(
                f"<b>{s['title']}</b>", body_style
            ))
            elements.append(Paragraph(s['detail'], body_style))
            elements.append(Spacer(1, 4))

    # --- Weaknesses ---
    weaknesses = gap.get('weaknesses', [])
    if weaknesses:
        elements.append(Paragraph('Areas for Improvement', heading_style))
        for w in weaknesses:
            elements.append(Paragraph(
                f"<b>{w['title']}</b>", body_style
            ))
            elements.append(Paragraph(w['detail'], body_style))
            elements.append(Spacer(1, 4))

    # --- Recommendations ---
    recs = analysis_results.get('recommendations', [])
    if recs:
        elements.append(PageBreak())
        elements.append(Paragraph('Recommendations', heading_style))
        for i, rec in enumerate(recs, 1):
            elements.append(Paragraph(
                f"<b>{i}. {rec['title']}</b>", body_style
            ))
            elements.append(Paragraph(rec['explanation'], body_style))
            action_style = ParagraphStyle(
                f'Action{i}',
                parent=body_style,
                leftIndent=16,
                textColor=colors.HexColor('#16213e'),
            )
            elements.append(Paragraph(
                f"\u2192 {rec['action']}", action_style
            ))
            elements.append(Spacer(1, 8))

    # --- Roast Section ---
    roasts = analysis_results.get('roasts', [])
    if roasts:
        elements.append(Paragraph('Resume Roast', heading_style))
        for roast in roasts:
            elements.append(Paragraph(f"\u2022 {roast}", body_style))
        elements.append(Spacer(1, 8))

    # --- Disclaimer ---
    elements.append(Spacer(1, 24))
    elements.append(HRFlowable(
        width='100%', thickness=0.5,
        color=colors.HexColor('#cccccc'),
        spaceBefore=12,
        spaceAfter=8,
    ))
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontSize=7,
        textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
        leading=10,
    )
    elements.append(Paragraph(
        'This report was generated by Resume Roast AI using NLP techniques. '
        'The semantic similarity score measures textual alignment between your '
        'resume and the job description \u2014 it does not represent hiring '
        'probability. Skills extraction is based on keyword matching against '
        'a configurable taxonomy. Use these insights as a guide for improvement, '
        'not as a definitive assessment.',
        disclaimer_style
    ))
    elements.append(Paragraph(
        f'Resume Roast AI \u2014 {datetime.now().year}',
        disclaimer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
