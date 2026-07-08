from __future__ import annotations

import base64
import io
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


@dataclass
class ReportSection:
    title: str
    content: str = ""
    figures: list[plt.Figure] = field(default_factory=list)
    metrics: dict[str, str | float | int] = field(default_factory=dict)


class ReportBuilder:
    """Builds a self-contained dark-themed HTML report.

    Usage::

        rb = ReportBuilder("Credit Card Fraud — Model Report", subtitle="v0.1.0")
        rb.add_section(ReportSection(
            title="Model Performance",
            metrics={"F1": 0.94, "AUC-ROC": 0.98},
            figures=[roc_fig, cm_fig],
        ))
        rb.save("reports/model_report.html")
    """

    def __init__(self, title: str, subtitle: str = "") -> None:
        self.title = title
        self.subtitle = subtitle
        self._sections: list[ReportSection] = []

    def add_section(self, section: ReportSection) -> ReportBuilder:
        self._sections.append(section)
        return self

    @staticmethod
    def _fig_to_b64(fig: plt.Figure) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    def to_html(self) -> str:
        sections_html = ""
        for sec in self._sections:
            metrics_html = ""
            if sec.metrics:
                rows = "".join(
                    f"<tr><td>{k}</td><td><strong>{v}</strong></td></tr>"
                    for k, v in sec.metrics.items()
                )
                metrics_html = f"<table class='metrics'><tbody>{rows}</tbody></table>"

            figs_html = "".join(
                f"<img src='data:image/png;base64,{self._fig_to_b64(f)}' alt='figure' />"
                for f in sec.figures
            )
            body = ""
            if sec.content:
                body = f"<p>{sec.content}</p>"
            sections_html += f"""
        <section>
          <h2>{sec.title}</h2>
          {body}{metrics_html}{figs_html}
        </section>"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{self.title}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'DM Mono', 'Courier New', monospace;
      background: #0a0a0a; color: #e8e4dc;
      padding: 2rem; max-width: 960px; margin: 0 auto;
    }}
    h1 {{ color: #c8a96e; font-size: 2rem; letter-spacing: -0.02em; margin-bottom: 0.5rem; }}
    h2 {{
      color: #00e5cc; font-size: 0.8rem; letter-spacing: 0.12em;
      text-transform: uppercase; border-bottom: 1px solid #1e1e1e;
      padding-bottom: 0.5rem; margin: 2rem 0 1rem;
    }}
    p {{ color: #a09994; line-height: 1.7; margin-bottom: 1rem; }}
    .meta {{ color: #6b6460; font-size: 0.78rem; margin-top: 0.4rem; }}
    table.metrics {{ border-collapse: collapse; margin: 1rem 0; width: auto; }}
    table.metrics td {{ padding: 0.35rem 1rem; border: 1px solid #1e1e1e; font-size: 0.88rem; }}
    table.metrics td:first-child {{ color: #a09994; }}
    table.metrics td strong {{ color: #00e5cc; }}
    img {{ max-width: 100%; border: 1px solid #1e1e1e; border-radius: 4px; margin: 0.5rem 0; display: block; }}
    section {{ margin-bottom: 1.5rem; }}
  </style>
</head>
<body>
  <h1>{self.title}</h1>
  {f"<p>{self.subtitle}</p>" if self.subtitle else ""}
  <p class="meta">Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
  {sections_html}
</body>
</html>"""

    def save(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_html(), encoding="utf-8")
        return path
