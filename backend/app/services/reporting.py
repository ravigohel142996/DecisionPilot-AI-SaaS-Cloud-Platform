from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def build_executive_pdf(company_name: str, filename: str, summary: str) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, title="DecisionPilot Executive Report")
    styles = getSampleStyleSheet()

    content = [
        Paragraph(f"DecisionPilot Executive Report - {company_name}", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Source dataset: {filename}", styles["Heading2"]),
        Spacer(1, 8),
    ]

    for line in summary.split("\n"):
        content.append(Paragraph(line, styles["BodyText"]))
        content.append(Spacer(1, 6))

    doc.build(content)
    buffer.seek(0)
    return buffer.read()
