from app.services.analysis import summarize_csv
from app.services.reporting import build_executive_pdf


def test_summarize_csv():
    csv_data = b"revenue,cost,region\n100,60,US\n120,70,EU\n"
    _, summary, metadata = summarize_csv(csv_data, "metrics.csv")
    assert "Rows: 2" in summary
    assert "Columns: 5" in summary  # includes engineered features
    assert "revenue" in summary
    assert "numeric_features" in metadata


def test_build_executive_pdf():
    pdf_bytes = build_executive_pdf("Acme", "metrics.csv", "Rows: 2")
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500
