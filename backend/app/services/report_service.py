import io
import html
import logging
from typing import List
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from ..models.schemas import AnalysisResponse, TestStatus

logger = logging.getLogger(__name__)


class ReportService:
    def generate_csv_bytes(self, analysis: AnalysisResponse) -> bytes:
        """
        Generate CSV export of the analyzed blood report.
        """
        rows = []
        for param in analysis.parameters:
            if param.ref_range_text:
                ref_str = param.ref_range_text
            elif param.ref_min is not None and param.ref_max is not None:
                ref_str = f"≥ {param.ref_min}" if param.ref_max >= 99999 else f"{param.ref_min} - {param.ref_max}"
            else:
                ref_str = "N/A"

            rows.append({
                "Test Name": param.test_name,
                "Category": param.category or "General",
                "Observed Result": param.value if param.value is not None else param.raw_value,
                "Unit": param.unit or "",
                "Reference Range": ref_str,
                "Status": param.status.value,
                "Correlated Symptoms": "; ".join(param.symptoms) if param.symptoms else "",
                "Explanation": param.explanation or "",
            })
        df = pd.DataFrame(rows)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        return csv_buffer.getvalue().encode("utf-8")

    def generate_pdf_bytes(self, analysis: AnalysisResponse) -> bytes:
        """
        Generate professional PDF summary report using ReportLab.
        """
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        styles = getSampleStyleSheet()

        # Custom styles
        primary_teal = colors.HexColor("#0F766E")
        navy_dark = colors.HexColor("#0F172A")
        slate_gray = colors.HexColor("#475569")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=primary_teal,
            spaceAfter=6,
        )

        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=slate_gray,
            spaceAfter=12,
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=navy_dark,
            spaceBefore=12,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=navy_dark,
        )

        cell_header_style = ParagraphStyle(
            "CellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=11,
            textColor=colors.white,
        )

        cell_body_style = ParagraphStyle(
            "CellBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10.5,
            textColor=navy_dark,
        )

        cell_bold_style = ParagraphStyle(
            "CellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10.5,
            textColor=navy_dark,
        )

        small_disclaimer = ParagraphStyle(
            "Disclaimer",
            parent=styles["Italic"],
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#64748B"),
        )

        # Header Title
        elements.append(Paragraph("<b>HemoInsight AI — Smart Blood Report Analysis</b>", title_style))
        elements.append(Paragraph(
            f"Report File: <b>{html.escape(analysis.metadata.filename)}</b> | Date: {html.escape(analysis.metadata.collection_date or 'Recent')} | Patient: {html.escape(analysis.metadata.patient_name or 'Not specified')}",
            subtitle_style
        ))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=primary_teal, spaceAfter=14))

        # Overall Outcome Box
        outcome_color = primary_teal
        if analysis.summary.overall_outcome.value == "SOME_NEED_ATTENTION":
            outcome_color = colors.HexColor("#D97706")
        elif analysis.summary.overall_outcome.value == "INSUFFICIENT_DATA":
            outcome_color = colors.HexColor("#DC2626")

        outcome_text = f"<b>{html.escape(analysis.summary.overall_title)}</b><br/>{html.escape(analysis.summary.overall_message)}"
        summary_table_data = [
            [Paragraph(outcome_text, ParagraphStyle("OutcomeBox", parent=styles["Normal"], textColor=colors.white, fontSize=10, leading=14))]
        ]
        outcome_table = Table(summary_table_data, colWidths=[540])
        outcome_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), outcome_color),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        elements.append(outcome_table)
        elements.append(Spacer(1, 12))

        # Summary Metrics
        metrics_data = [
            ["Total Analyzed", "Within Range", "Low Results", "High Results", "Needs Review"],
            [
                str(analysis.summary.total_parameters),
                str(analysis.summary.within_range_count),
                str(analysis.summary.low_count),
                str(analysis.summary.high_count),
                str(analysis.summary.needs_review_count),
            ]
        ]
        metrics_table = Table(metrics_data, colWidths=[108, 108, 108, 108, 108])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('TEXTCOLOR', (0, 0), (-1, -1), navy_dark),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 14))

        # Parameter Table
        elements.append(Paragraph("<b>Detailed Parameter Findings</b>", section_heading))
        table_data = [
            [
                Paragraph("<b>Test Parameter</b>", cell_header_style),
                Paragraph("<b>Result</b>", cell_header_style),
                Paragraph("<b>Unit</b>", cell_header_style),
                Paragraph("<b>Reference Interval</b>", cell_header_style),
                Paragraph("<b>Status</b>", cell_header_style)
            ]
        ]

        for p in analysis.parameters:
            if p.ref_range_text:
                ref_txt = p.ref_range_text
            elif p.ref_min is not None and p.ref_max is not None:
                ref_txt = f"≥ {p.ref_min}" if p.ref_max >= 99999 else f"{p.ref_min} - {p.ref_max}"
            else:
                ref_txt = "N/A"

            val_txt = str(p.value) if p.value is not None else (p.raw_value or "-")
            status_txt = p.status.value.replace("_", " ").title()

            status_color = "#0F766E"
            if p.status == TestStatus.LOW:
                status_color = "#1D4ED8"
            elif p.status == TestStatus.HIGH:
                status_color = "#B45309"
            elif p.status == TestStatus.NEEDS_REVIEW:
                status_color = "#DC2626"

            status_cell = Paragraph(f'<font color="{status_color}"><b>{html.escape(status_txt)}</b></font>', cell_body_style)

            table_data.append([
                Paragraph(html.escape(p.test_name), cell_bold_style),
                Paragraph(html.escape(val_txt), cell_body_style),
                Paragraph(html.escape(p.unit or ""), cell_body_style),
                Paragraph(html.escape(ref_txt), cell_body_style),
                status_cell
            ])

        param_table = Table(table_data, colWidths=[160, 75, 75, 120, 110])
        param_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F766E")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(param_table)
        elements.append(Spacer(1, 14))

        # Flagged Findings Explanations (Abnormal or Needing Verification)
        flagged_items = [p for p in analysis.parameters if p.status in [TestStatus.LOW, TestStatus.HIGH, TestStatus.NEEDS_REVIEW]]
        if flagged_items:
            elements.append(Paragraph("<b>Explanations of Flagged Results</b>", section_heading))
            for item in flagged_items:
                safe_name = html.escape(item.test_name)
                safe_status = html.escape(item.status.value.replace('_', ' ').title())
                safe_exp = html.escape(item.explanation or 'Evaluated against laboratory reference interval.')
                elements.append(Paragraph(f"• <b>{safe_name} ({safe_status}):</b> {safe_exp}", body_style))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 10))

        # Correlated Symptoms Checklist for the Patient to Discuss with Doctor
        if analysis.summary.patient_symptoms and len(analysis.summary.patient_symptoms) > 0:
            elements.append(Paragraph("<b>Physical Symptoms Checklist for Doctor Consultation</b>", section_heading))
            elements.append(Paragraph(
                "The following physical symptoms are clinically correlated with the out-of-range findings detected in this report. "
                "Check any symptoms you have been experiencing to share with your physician during consultation:",
                body_style
            ))
            elements.append(Spacer(1, 6))

            symptom_rows = []
            symps = analysis.summary.patient_symptoms[:12]  # Keep concise for clean PDF layout
            for i in range(0, len(symps), 2):
                col1 = f"[  ]  {html.escape(symps[i])}"
                col2 = f"[  ]  {html.escape(symps[i+1])}" if i + 1 < len(symps) else ""
                symptom_rows.append([
                    Paragraph(col1, body_style),
                    Paragraph(col2, body_style) if col2 else ""
                ])

            symptom_table = Table(symptom_rows, colWidths=[270, 270])
            symptom_table.setStyle(TableStyle([
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#F59E0B")),
            ]))
            elements.append(symptom_table)
            elements.append(Spacer(1, 12))

        # Potential Clinical Conditions Correlated for Physician Review
        if analysis.summary.associated_conditions and len(analysis.summary.associated_conditions) > 0:
            elements.append(Paragraph("<b>Potential Clinical Condition Associations (For Doctor Consultation)</b>", section_heading))
            elements.append(Paragraph(
                "Based on the pattern of out-of-range biomarkers, the following differentials and confirmatory tests are suggested to discuss with your healthcare professional:",
                body_style
            ))
            elements.append(Spacer(1, 4))
            for cond in analysis.summary.associated_conditions[:3]:
                safe_cond = html.escape(cond.condition_name)
                safe_level = html.escape(cond.match_level)
                safe_overview = html.escape(cond.overview)
                tests_str = ", ".join([html.escape(t) for t in cond.suggested_follow_up_tests[:3]])
                elements.append(Paragraph(f"• <b>{safe_cond}</b> ({safe_level} - {cond.match_score}%): {safe_overview}", body_style))
                if tests_str:
                    elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Suggested Doctor Follow-up Tests:</i> {tests_str}", body_style))
                elements.append(Spacer(1, 4))
            elements.append(Spacer(1, 10))

        # Medical Disclaimer
        elements.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#CBD5E1"), spaceAfter=8))
        elements.append(Paragraph(
            f"<b>Medical & Educational Safety Notice:</b> {html.escape(analysis.disclaimer)}",
            small_disclaimer
        ))

        doc.build(elements)
        return pdf_buffer.getvalue()
