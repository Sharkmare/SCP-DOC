from __future__ import annotations

import json
import html
import sys
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------
# Official SCP Wiki ACS icon base
# ---------------------------------------------------------------------

ACS_ICON_BASE = (
    "https://scp-wiki.wdfiles.com/local--files/"
    "component:anomaly-class-bar"
)

ACS_ICON_MAP = {
    # Containment
    "safe": "safe-icon.svg",
    "euclid": "euclid-icon.svg",
    "keter": "keter-icon.svg",
    "neutralized": "neutralized-icon.svg",
    "pending": "pending-icon.svg",
    "explained": "explained-icon.svg",
    "esoteric": "esoteric-icon.svg",

    # Secondary / Esoteric
    "thaumiel": "thaumiel-icon.svg",
    "apollyon": "apollyon-icon.svg",
    "archon": "archon-icon.svg",
    "cernunnos": "cernunnos-icon.svg",
    "decommissioned": "decommissioned-icon.svg",
    "hiemal": "hiemal-icon.svg",
    "tiamat": "tiamat-icon.svg",
    "ticonderoga": "ticonderoga-icon.svg",
    "uncontained": "uncontained-icon.svg",

    # Disruption
    "dark": "dark-icon.svg",
    "vlam": "vlam-icon.svg",
    "keneq": "keneq-icon.svg",
    "ekhi": "ekhi-icon.svg",
    "amida": "amida-icon.svg",

    # Risk
    "none": "notice-icon.svg",
    "notice": "notice-icon.svg",
    "caution": "caution-icon.svg",
    "warning": "warning-icon.svg",
    "danger": "danger-icon.svg",
    "critical": "critical-icon.svg",
}

def acs_icon_url(value: str) -> str | None:
    value = value.lower()
    filename = ACS_ICON_MAP.get(value)
    if not filename:
        return None
    return f"{ACS_ICON_BASE}/{filename}"

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def esc(s: Any) -> str:
    return html.escape(str(s), quote=True)

def to_paragraphs(body: Any) -> str:
    if body is None:
        return ""
    if isinstance(body, str):
        items = [body]
    elif isinstance(body, list):
        items = body
    else:
        items = [str(body)]

    return "\n".join(
        f"<p>{esc(p.strip())}</p>"
        for p in items
        if str(p).strip()
    )

# ---------------------------------------------------------------------
# Header renderers
# ---------------------------------------------------------------------

def render_classic_header(data: Dict[str, Any]) -> str:
    classic = data.get("classic", {})
    item_number = classic.get("item_number", data.get("title", "SCP-XXXX"))
    object_class = classic.get("object_class", "Euclid")

    return f"""
<section class="doc-header">
  <div class="doc-title">{esc(data.get("title", item_number))}</div>
  {"<div class='doc-subtitle'>" + esc(data["subtitle"]) + "</div>" if data.get("subtitle") else ""}
  <div class="meta-lines">
    <div><span class="meta-key">Item #:</span> {esc(item_number)}</div>
    <div><span class="meta-key">Object Class:</span> {esc(object_class)}</div>
  </div>
</section>
""".strip()

def acs_badge(label: str, value: str) -> str:
    icon = acs_icon_url(value)
    if not icon:
        return ""

    return f"""
<div class="badge badge--acs">
  <img
    src="{icon}"
    alt="{esc(label)}: {esc(value)}"
    class="badge__icon"
    loading="lazy"
    referrerpolicy="no-referrer"
  >
  <div class="badge__text">
    <div class="badge__label">{esc(label)}</div>
    <div class="badge__value">{esc(value)}</div>
  </div>
</div>
""".strip()

def render_acs_header(data: Dict[str, Any]) -> str:
    acs = data.get("acs", {})
    title = data.get("title", "SCP-XXXX")

    item_number = acs.get("item_number", title)
    clearance_level = acs.get("clearance_level", 2)
    clearance_label = acs.get("clearance_label", "")
    clearance = f"Level {clearance_level}" + (f": {clearance_label}" if clearance_label else "")

    containment = acs.get("containment_class", "euclid")
    secondary = acs.get("secondary_class", "none")
    disruption = acs.get("disruption_class", "none")
    risk = acs.get("risk_class", "notice")

    memo_url = acs.get("memo_url")

    return f"""
<section class="doc-header">
  <div class="doc-title">{esc(title)}</div>
  {"<div class='doc-subtitle'>" + esc(data["subtitle"]) + "</div>" if data.get("subtitle") else ""}
  <div class="acs-bar">
    <div class="acs-top">
      <div class="acs-item"><span class="acs-k">Item #</span>{esc(item_number)}</div>
      <div class="acs-item"><span class="acs-k">Clearance</span>{esc(clearance)}</div>
      <!-- {f"<a class='memo-link' href='{esc(memo_url)}'>Link to memo</a>" if memo_url else ""} -->
    </div>
    <div class="acs-badges">
      {acs_badge("Containment", containment)}
      {acs_badge("Secondary", secondary)}
      {acs_badge("Disruption", disruption)}
      {acs_badge("Risk", risk)}
    </div>
  </div>
</section>
""".strip()

# ---------------------------------------------------------------------
# Sections / Footer / HTML
# ---------------------------------------------------------------------

def render_sections(data: Dict[str, Any]) -> str:
    out: List[str] = []
    for sec in data.get("sections", []):
        cls = "section"
        if sec.get("kind") == "log":
            cls += " section--log"
        out.append(f"""
<section class="{cls}">
  <h2>{esc(sec.get("heading", "Section"))}</h2>
  {to_paragraphs(sec.get("body"))}
</section>
""".strip())
    return "\n".join(out)

def render_footer(data: Dict[str, Any]) -> str:
    foot = data.get("footer", {})
    return f"""
<footer class="doc-footer">
  <span>{esc(foot.get("left", "«"))}</span>
  <span>{esc(foot.get("center", data.get("title", "SCP")))}</span>
  <span>{esc(foot.get("right", "»"))}</span>
</footer>
""".strip()

def build_html(data: Dict[str, Any]) -> str:
    header = (
        render_acs_header(data)
        if data.get("header_mode") == "acs"
        else render_classic_header(data)
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(data.get("title", "SCP Document"))}</title>
<style>
body {{ background:#0c0d10; color:#e8e8ee; font:15px/1.5 system-ui,sans-serif; }}
.doc {{ max-width:960px; margin:40px auto; padding:24px; background:#121420; border-radius:16px; }}
.doc-title {{ font-size:26px; font-weight:800; }}
.meta-key {{ color:#b7b7c8; font-weight:700; }}
.acs-bar {{ margin-top:14px; padding:12px; border:1px solid rgba(255,255,255,.15); border-radius:12px; }}
.acs-badges {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }}
.badge--acs {{ display:flex; gap:10px; align-items:center; border:1px solid rgba(255,255,255,.15); padding:8px; border-radius:10px; }}
.badge__icon {{ width:28px; height:28px; }}
.section {{ margin-top:20px; }}
.section--log p {{ font-family:monospace; background:rgba(0,0,0,.25); padding:8px; border-radius:8px; }}
.doc-footer {{ display:flex; justify-content:space-between; margin-top:30px; color:#b7b7c8; font-size:12px; }}
</style>
</head>
<body>
<article class="doc">
{header}
{render_sections(data)}
{render_footer(data)}
</article>
</body>
</html>
"""

def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python scpdocgen.py SCPDOC.json output.html", file=sys.stderr)
        return 1

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    Path(sys.argv[2]).write_text(build_html(data), encoding="utf-8")
    print("HTML generated.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
