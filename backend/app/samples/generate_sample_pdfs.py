import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf(filename, title, patient, date, rows):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    styles = getSampleStyleSheet()
    elements = []

    primary_color = colors.HexColor("#0F766E")
    
    title_style = ParagraphStyle(
        "LabTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4,
    )

    info_style = ParagraphStyle(
        "LabInfo",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )

    elements.append(Paragraph("<b>Apex Clinical Diagnostic Laboratories</b>", title_style))
    elements.append(Paragraph(f"<b>Test Report:</b> {title}<br/><b>Patient Name:</b> {patient} | <b>Collection Date:</b> {date} | <b>Ref By:</b> Dr. S. Rao, MD", info_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=14))

    table_data = [["Test Parameter", "Observed Value", "Units", "Biological Reference Interval", "Flag"]]
    table_data.extend(rows)

    t = Table(table_data, colWidths=[180, 80, 70, 140, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Italic"],
        fontSize=8,
        textColor=colors.HexColor("#64748B"),
    )
    elements.append(Paragraph("This laboratory report is validated and digitally authorized by Apex Diagnostic Medical Director.", disclaimer_style))

    doc.build(elements)
    print(f"Generated {filename}")

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. CBC Anemia
    generate_pdf(
        os.path.join(out_dir, "sample_cbc_anemia.pdf"),
        "Complete Blood Count (CBC) with Automated Differential",
        "Jane Doe, 32 / Female",
        "14-Oct-2026",
        [
            ["Hemoglobin", "10.4", "g/dL", "12.0 - 16.0", "LOW"],
            ["Red Blood Cell Count", "3.75", "million/mcL", "4.0 - 5.4", "LOW"],
            ["Hematocrit", "32.5", "%", "36.0 - 48.0", "LOW"],
            ["Mean Corpuscular Volume", "75.2", "fL", "80.0 - 100.0", "LOW"],
            ["White Blood Cell Count", "6.8", "x10^3/mcL", "4.0 - 11.0", "NORMAL"],
            ["Platelets", "128.0", "x10^3/mcL", "150.0 - 450.0", "LOW"],
            ["Neutrophils", "58.0", "%", "40.0 - 75.0", "NORMAL"],
            ["Lymphocytes", "32.0", "%", "20.0 - 45.0", "NORMAL"],
        ]
    )

    # 2. Routine Normal Checkup
    generate_pdf(
        os.path.join(out_dir, "sample_routine_checkup.pdf"),
        "Comprehensive Annual Health Screening Panel",
        "John Smith, 45 / Male",
        "12-Oct-2026",
        [
            ["Hemoglobin", "14.8", "g/dL", "13.5 - 17.5", "NORMAL"],
            ["Fasting Glucose", "92.0", "mg/dL", "70.0 - 99.0", "NORMAL"],
            ["Serum Creatinine", "0.95", "mg/dL", "0.6 - 1.3", "NORMAL"],
            ["Total Cholesterol", "172.0", "mg/dL", "125.0 - 200.0", "NORMAL"],
            ["Alanine Aminotransferase (ALT)", "22.0", "U/L", "7.0 - 56.0", "NORMAL"],
            ["Serum Potassium", "4.4", "mEq/L", "3.5 - 5.2", "NORMAL"],
        ]
    )
