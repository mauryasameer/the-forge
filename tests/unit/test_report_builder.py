from pathlib import Path

from meerax.report.builder import ReportBuilder, ReportSection


def test_to_html_contains_title():
    rb = ReportBuilder("Test Report")
    html = rb.to_html()
    assert "Test Report" in html


def test_section_metrics_in_html():
    rb = ReportBuilder("Report")
    rb.add_section(ReportSection(title="Metrics", metrics={"F1": 0.95, "AUC": 0.98}))
    html = rb.to_html()
    assert "F1" in html
    assert "0.95" in html


def test_section_content_in_html():
    rb = ReportBuilder("Report")
    rb.add_section(ReportSection(title="Summary", content="Model trained on 10k samples."))
    html = rb.to_html()
    assert "Model trained on 10k samples." in html


def test_save_creates_file(tmp_path: Path):
    rb = ReportBuilder("Save Test")
    out = rb.save(tmp_path / "report.html")
    assert out.exists()
    assert out.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_chaining():
    rb = ReportBuilder("Chain")
    result = rb.add_section(ReportSection("S1")).add_section(ReportSection("S2"))
    assert result is rb
    assert len(rb._sections) == 2
