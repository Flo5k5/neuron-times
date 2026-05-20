#!/usr/bin/env python3
"""
build_index.py — Regénère index.html à partir des reports/*.json

Lit tous les fichiers reports/*.json (sortie du générateur engine), trie par
date décroissante, génère une page d'index thématisée Times Victorien (le
thème par défaut) avec une grille de cards chronologiques.

Idempotent : peut être appelé à chaque push, ne fait rien si rien à changer.

Convention : reports/YYYY-MM-DD.json contient au minimum :
    {
      "edition": {"date_long": "Mercredi 20 mai 2026", "date_iso": "2026-05-20", "vol": "I", "num": "1"},
      "lead": {"kicker": "...", "headline": "...", "subdeck": "..."}
    }
"""

import json
import sys
from datetime import datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
REPORTS_DIR = ROOT / "reports"
INDEX_PATH = ROOT / "index.html"
LATEST_PATH = ROOT / "latest.html"


def load_reports():
    """Charge tous les reports/*.json en liste de dicts avec date_iso accessible."""
    reports = []
    for json_path in sorted(REPORTS_DIR.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            edition = data.get("edition", {})
            date_iso = edition.get("date_iso") or json_path.stem
            reports.append({
                "date_iso": date_iso,
                "date_long": edition.get("date_long", date_iso),
                "vol": edition.get("vol", ""),
                "num": edition.get("num", ""),
                "headline": data.get("lead", {}).get("headline", "Rapport veille"),
                "kicker": data.get("lead", {}).get("kicker", ""),
                "subdeck": data.get("lead", {}).get("subdeck", ""),
                "json_filename": json_path.name,
                "html_filename": json_path.stem + ".html",
            })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[warn] skipping {json_path.name}: {e}", file=sys.stderr)
            continue
    # Tri DESC par date
    reports.sort(key=lambda r: r["date_iso"], reverse=True)
    return reports


def update_latest(reports):
    """Copie le report HTML le plus récent vers latest.html."""
    if not reports:
        return
    latest_html = REPORTS_DIR / reports[0]["html_filename"]
    if latest_html.exists():
        LATEST_PATH.write_text(latest_html.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[ok] latest.html updated → {reports[0]['html_filename']}")
    else:
        print(f"[warn] {latest_html} not found, latest.html not updated", file=sys.stderr)


def render_card(report):
    """Génère une <article class='card'> pour un report donné."""
    return f"""
    <article class="card">
      <a href="reports/{escape(report['html_filename'])}" class="card-link">
        <div class="card-meta">
          <span class="card-date">{escape(report['date_long'])}</span>
          {f'<span class="card-vol">Vol. {escape(report["vol"])} · N° {escape(report["num"])}</span>' if report['vol'] else ''}
        </div>
        <div class="card-kicker">{escape(report['kicker'])}</div>
        <h2 class="card-headline">{escape(report['headline'])}</h2>
        {f'<p class="card-subdeck">{escape(report["subdeck"])}</p>' if report['subdeck'] else ''}
        <div class="card-cta">Lire l'édition →</div>
      </a>
    </article>"""


def render_index(reports):
    """Génère le HTML complet de index.html (thématisé Times Victorien)."""
    cards_html = "\n".join(render_card(r) for r in reports) if reports else """
    <p class="empty">Aucun rapport publié pour le moment. Reviens demain matin.</p>"""

    total = len(reports)
    latest_date = reports[0]["date_long"] if reports else ""
    build_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Neuron Times — Archive</title>
<meta name="description" content="Daily AI watch newspaper. {total} éditions publiées. Dernière : {escape(latest_date)}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@0,400;0,700;0,900;1,400&family=Cinzel:wght@400;600;800&family=Old+Standard+TT:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ font-size: 16px; }}
  body {{
    font-family: 'Old Standard TT', 'Times New Roman', serif;
    background: #ede4cf;
    color: #0c0c0c;
    line-height: 1.55;
    min-height: 100vh;
    background-image: radial-gradient(ellipse at center, transparent 40%, rgba(0,0,0,0.03) 100%);
  }}
  .paper {{
    max-width: 1100px;
    margin: 2rem auto;
    padding: 3rem 3.5rem;
    background: #f4ecdc;
    border: 1px solid #b8af96;
    box-shadow: 0 2px 30px rgba(0,0,0,0.15);
  }}
  .masthead {{
    text-align: center;
    border-top: 8px solid #0c0c0c;
    border-bottom: 1px solid #0c0c0c;
    padding: 1.2rem 0 0.8rem;
    margin-bottom: 1.5rem;
    position: relative;
  }}
  .masthead::after {{ content: ''; display: block; border-top: 1px solid #0c0c0c; margin-top: 4px; }}
  .masthead .above {{
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 5px;
    color: #4a4a4a;
    margin-bottom: 0.6rem;
    font-style: italic;
  }}
  .masthead h1 {{
    font-family: 'Bodoni Moda', serif;
    font-size: 5rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: -2px;
    line-height: 1;
    margin: 0.3rem 0;
  }}
  .masthead .motto {{
    font-family: 'Old Standard TT', serif;
    font-style: italic;
    font-size: 1rem;
    color: #4a4a4a;
    margin-bottom: 0.6rem;
  }}
  .masthead .dateline {{
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-top: 2px solid #0c0c0c;
    border-bottom: 2px solid #0c0c0c;
    margin-top: 1rem;
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
  }}
  .archive-intro {{
    font-family: 'Old Standard TT', serif;
    font-style: italic;
    font-size: 1.15rem;
    color: #2a2a2a;
    text-align: center;
    max-width: 720px;
    margin: 1.5rem auto 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 4px double #0c0c0c;
    line-height: 1.5;
  }}
  .archive-intro strong {{ font-weight: 700; color: #0c0c0c; }}
  .archive-intro a {{ color: #6b0f0f; text-decoration: none; border-bottom: 1px solid currentColor; }}
  .archive-intro a:hover {{ color: #0c0c0c; }}
  .archive-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }}
  .card {{
    border: 1px solid #b8af96;
    background: #faf6ea;
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 18px rgba(0,0,0,0.12);
  }}
  .card-link {{
    display: block;
    padding: 1.2rem 1.4rem;
    color: inherit;
    text-decoration: none;
    height: 100%;
  }}
  .card-meta {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-family: 'Cinzel', serif;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b6b6b;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #0c0c0c;
  }}
  .card-kicker {{
    font-family: 'Cinzel', serif;
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b0f0f;
    font-weight: 600;
    margin-bottom: 0.3rem;
  }}
  .card-headline {{
    font-family: 'Bodoni Moda', serif;
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1.15;
    margin-bottom: 0.6rem;
  }}
  .card-subdeck {{
    font-family: 'Old Standard TT', serif;
    font-style: italic;
    font-size: 0.95rem;
    color: #444;
    line-height: 1.35;
    margin-bottom: 0.8rem;
  }}
  .card-cta {{
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #6b0f0f;
    font-weight: 600;
    text-align: right;
  }}
  .empty {{
    font-family: 'Old Standard TT', serif;
    font-style: italic;
    text-align: center;
    color: #6b6b6b;
    padding: 3rem 0;
    font-size: 1.1rem;
  }}
  .ours {{
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 6px solid #0c0c0c;
    text-align: center;
    font-family: 'Cinzel', serif;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a4a4a;
  }}
  .ours .motto {{
    font-family: 'Bodoni Moda', serif;
    font-style: italic;
    font-size: 1rem;
    color: #0c0c0c;
    text-transform: none;
    letter-spacing: 0;
    margin-top: 0.8rem;
  }}
  .ours .build-time {{ font-size: 0.6rem; color: #888; margin-top: 0.4rem; }}
  @media (max-width: 720px) {{
    html {{ font-size: 14px; }}
    .paper {{ padding: 1.5rem; margin: 0; }}
    .masthead h1 {{ font-size: 2.8rem; }}
    .archive-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<div class="paper">

  <header class="masthead">
    <div class="above">Published at https://neuron-times.com</div>
    <h1>The Neuron Times</h1>
    <p class="motto">« All the AI that's fit to print »</p>
    <div class="dateline">
      <span>Daily Edition</span>
      <span>{escape(latest_date) if latest_date else "Bientôt"}</span>
      <span>{total} éditions archivées</span>
    </div>
  </header>

  <p class="archive-intro">
    <strong>The Neuron Times</strong> publie chaque matin une synthèse des signaux notables de l'écosystème
    intelligence artificielle — modèles frontière, agents de codage, infrastructure, recherche, signaux
    communauté. Cliquez sur une édition pour la lire en intégralité.
    {f'<br><br>Édition du jour : <a href="latest.html">{escape(latest_date)}</a>' if latest_date else ''}
  </p>

  <main class="archive-grid">
    {cards_html}
  </main>

  <footer class="ours">
    <div>★ ★ ★</div>
    <p style="margin-top: 0.8rem;">Édition quotidienne automatique · Hébergé sur GitHub Pages</p>
    <p class="motto">« All the AI that's fit to print »</p>
    <p class="build-time">Index regenerated {build_time} UTC</p>
  </footer>

</div>
</body>
</html>
"""


def main():
    if not REPORTS_DIR.exists():
        print(f"[err] reports/ directory not found at {REPORTS_DIR}", file=sys.stderr)
        sys.exit(1)

    reports = load_reports()
    print(f"[info] {len(reports)} reports found")

    # Génère index.html
    INDEX_PATH.write_text(render_index(reports), encoding="utf-8")
    print(f"[ok] index.html generated ({len(reports)} cards, {INDEX_PATH.stat().st_size} bytes)")

    # Update latest.html
    update_latest(reports)


if __name__ == "__main__":
    main()
