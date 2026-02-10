from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build_executive_pdf(company_name: str, filename: str, summary: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="VisionPilot AI Executive Report")
    styles = getSampleStyleSheet()

    kpi_rows = [["KPI", "Status"], ["Revenue Growth", "On Track"], ["Churn Risk", "Moderate"], ["Operational Risk", "Monitored"]]
    table = Table(kpi_rows, colWidths=[200, 200])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E2A78")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#7C8BFF")),
            ]
        )
    )

    content = [
        Paragraph(f"VisionPilot AI | Board Executive Report - {company_name}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Source dataset: {filename}", styles["Heading2"]),
        Spacer(1, 8),
        Paragraph("AI Insights & KPI Summary", styles["Heading2"]),
        Spacer(1, 8),
        table,
        Spacer(1, 12),
        Paragraph("Detailed Insights", styles["Heading2"]),
        Spacer(1, 6),
    ]

    for line in summary.split("\n"):
        content.append(Paragraph(line, styles["BodyText"]))
        content.append(Spacer(1, 4))

    content.extend(
        [
            Spacer(1, 8),
            Paragraph("Risk Alerts: monitor churn segments and supplier volatility.", styles["BodyText"]),
            Paragraph("Recommendation: execute scenario simulation before final budget approval.", styles["BodyText"]),
        ]
    )

    doc.build(content)
    buffer.seek(0)
    return buffer.read()
