#!/usr/bin/env python3
"""
build_index.py — Regénère index.html à partir des editions/*.json

Lit tous les fichiers editions/*.json (sortie du générateur), trie par
date décroissante, génère une page d'index thématisée Times Victorien.

Multilingue (fr, en, de, it, rm) : si une édition est multilingual-v1
(schema), les fields headline/kicker/subdeck sont des dicts {fr,en,...}
et sont rendus en spans data-i18n. Sinon (mono FR), wrap en FR seul.
Le sélecteur en haut du masthead bascule la langue côté client via CSS.

Idempotent : peut être appelé à chaque push, ne fait rien si rien à changer.
"""

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
EDITIONS_DIR = ROOT / "editions"
INDEX_PATH = ROOT / "index.html"
LATEST_PATH = ROOT / "latest.html"

SUPPORTED_LANGS = ["fr", "en", "de", "it", "lmo"]

# Static UI strings translated across 5 languages
STATIC = {
    "daily_edition": {
        "fr": "Édition quotidienne",
        "en": "Daily Edition",
        "de": "Tägliche Ausgabe",
        "it": "Edizione quotidiana",
        "lmo": "Edizion de tüt i dì",
    },
    "archived_count": {
        # {n} placeholder
        "fr": "{n} éditions archivées",
        "en": "{n} archived editions",
        "de": "{n} archivierte Ausgaben",
        "it": "{n} edizioni archiviate",
        "lmo": "{n} edizion archiviaa",
    },
    "archived_count_one": {
        "fr": "1 édition publiée",
        "en": "1 edition published",
        "de": "1 Ausgabe veröffentlicht",
        "it": "1 edizione pubblicata",
        "lmo": "1 edizion publicaa",
    },
    "soon": {
        "fr": "Bientôt",
        "en": "Soon",
        "de": "Bald",
        "it": "Presto",
        "lmo": "Prest",
    },
    "intro": {
        "fr": "<strong>The Neuron Times</strong> publie chaque matin une synthèse des signaux notables de l'écosystème intelligence artificielle — modèles frontière, agents de codage, infrastructure, recherche, signaux communauté. Cliquez sur une édition pour la lire en intégralité.",
        "en": "<strong>The Neuron Times</strong> publishes every morning a synthesis of notable signals from the AI ecosystem — frontier models, coding agents, infrastructure, research, community signals. Click on an edition to read it in full.",
        "de": "<strong>The Neuron Times</strong> veröffentlicht jeden Morgen eine Synthese bemerkenswerter Signale aus dem KI-Ökosystem — Frontier-Modelle, Coding-Agenten, Infrastruktur, Forschung, Community-Signale. Klicken Sie auf eine Ausgabe, um sie vollständig zu lesen.",
        "it": "<strong>The Neuron Times</strong> pubblica ogni mattina una sintesi dei segnali notevoli dell'ecosistema AI — modelli di frontiera, agenti di codifica, infrastruttura, ricerca, segnali della comunità. Clicca su un'edizione per leggerla integralmente.",
        "lmo": "<strong>The Neuron Times</strong> el publica tüti i matin ona sintesi di signai notabei de l'ecosistem de l'intelligenza artificiala — modei de frontera, agent de codifica, infrastrutura, ricerca, signai de la comunità. Clicca su on'edizion per legela tüta intrega.",
    },
    "today_edition": {
        "fr": "Édition du jour",
        "en": "Today's edition",
        "de": "Heutige Ausgabe",
        "it": "Edizione di oggi",
        "lmo": "Edizion de incoeu",
    },
    "read_edition": {
        "fr": "Lire l'édition →",
        "en": "Read edition →",
        "de": "Ausgabe lesen →",
        "it": "Leggi l'edizione →",
        "lmo": "Legi l'edizion →",
    },
    "empty": {
        "fr": "Aucune édition publiée pour le moment. Revenez demain matin.",
        "en": "No edition published yet. Come back tomorrow morning.",
        "de": "Noch keine Ausgabe veröffentlicht. Kommen Sie morgen früh wieder.",
        "it": "Nessuna edizione pubblicata per ora. Torna domani mattina.",
        "lmo": "Ancamò nessuna edizion publicaa. Torna doman matina.",
    },
    "description_template": {
        # Used in <meta description>, can stay FR for simplicity (search engines)
        "fr": "Daily AI watch newspaper. {n} éditions publiées. Dernière : {last}.",
    },
}


def ml(field, key_for_static: str = None) -> str:
    """
    Render a multilingual field as N spans with data-i18n + lang attrs.
    - field : either a dict {fr, en, de, it, rm}, or a plain string (assumed FR), or None
    - key_for_static : if provided, look up STATIC[key_for_static] instead (for UI strings)

    IMPORTANT : if the field has only 1 language (mono FR fallback), we render
    a single span WITHOUT data-i18n attribute so the CSS cascade does NOT hide
    it when the active language is not FR. The user sees FR content as a
    graceful fallback rather than an empty page.
    """
    if key_for_static and key_for_static in STATIC:
        trans = STATIC[key_for_static]
        return "".join(
            f'<span data-i18n lang="{lg}">{trans[lg]}</span>'
            for lg in SUPPORTED_LANGS
            if lg in trans
        )

    if isinstance(field, dict):
        present_langs = [lg for lg in SUPPORTED_LANGS if lg in field and field[lg] is not None]
        if len(present_langs) >= 2:
            # truly multilingual : render data-i18n spans, CSS shows active lang only
            return "".join(
                f'<span data-i18n lang="{lg}">{escape(field[lg])}</span>'
                for lg in present_langs
            )
        elif len(present_langs) == 1:
            # mono dict : render ONE span without data-i18n → visible in any lang
            return f'<span>{escape(field[present_langs[0]])}</span>'
        else:
            return ""
    elif field is None:
        return ""
    else:
        # Plain string : visible in any lang (no data-i18n)
        return f'<span>{escape(str(field))}</span>'


def load_editions():
    """Charge tous les editions/*.json en liste de dicts.
    Preserve les fields tel quel (dict si multilingual, string si mono).
    """
    editions = []
    for json_path in sorted(EDITIONS_DIR.glob("*.json")):
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            edition = data.get("edition", {})
            date_iso = edition.get("date_iso") or json_path.stem
            lead = data.get("lead", {})
            editions.append({
                "date_iso": date_iso,
                "date_long": edition.get("date_long", date_iso),  # may be dict or str
                "num": edition.get("num", ""),
                "headline": lead.get("headline", ""),  # may be dict or str
                "kicker": lead.get("kicker", ""),
                "subdeck": lead.get("subdeck", ""),
                "json_filename": json_path.name,
                "html_filename": json_path.stem + ".html",
            })
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[warn] skipping {json_path.name}: {e}", file=sys.stderr)
            continue
    editions.sort(key=lambda r: r["date_iso"], reverse=True)
    return editions


def update_latest(editions):
    """Copie l'édition HTML la plus récente vers latest.html."""
    if not editions:
        return
    latest_html = EDITIONS_DIR / editions[0]["html_filename"]
    if latest_html.exists():
        LATEST_PATH.write_text(latest_html.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[ok] latest.html updated → {editions[0]['html_filename']}")
    else:
        print(f"[warn] {latest_html} not found, latest.html not updated", file=sys.stderr)


def t_fr(field) -> str:
    """Extract FR plain text (for <title> + <meta>)."""
    if isinstance(field, dict):
        return field.get("fr") or field.get("en") or next(iter(field.values()), "")
    return str(field) if field is not None else ""


def render_card(edition):
    """Génère une <article class='card'> pour une édition donnée."""
    num_span = f'<span class="card-num">N° {escape(str(edition["num"]))}</span>' if edition["num"] else ""

    # kicker can be a dict (multilingual) or string ; render as multilingual spans
    kicker_div = f'<div class="card-kicker">{ml(edition["kicker"])}</div>' if edition["kicker"] else ""
    subdeck_p = f'<p class="card-subdeck">{ml(edition["subdeck"])}</p>' if edition["subdeck"] else ""

    return f"""
    <article class="card">
      <a href="editions/{escape(edition['html_filename'])}" class="card-link">
        <div class="card-meta">
          <span class="card-date">{ml(edition['date_long'])}</span>
          {num_span}
        </div>
        {kicker_div}
        <h2 class="card-headline">{ml(edition['headline'])}</h2>
        {subdeck_p}
        <div class="card-cta">{ml(None, key_for_static='read_edition')}</div>
      </a>
    </article>"""


def render_index(editions):
    """Génère le HTML complet de index.html (multilingue, thème Times Victorien)."""
    cards_html = "\n".join(render_card(e) for e in editions) if editions else f"""
    <p class="empty">{ml(None, key_for_static='empty')}</p>"""

    total = len(editions)
    latest_date_field = editions[0]["date_long"] if editions else None
    latest_date_fr = t_fr(latest_date_field) if latest_date_field else ""

    # Archive count : pluralize per language
    if total == 1:
        archive_count_html = ml(None, key_for_static="archived_count_one")
    else:
        # We need to substitute {n} inline ; build the spans manually
        trans = STATIC["archived_count"]
        archive_count_html = "".join(
            f'<span data-i18n lang="{lg}">{trans[lg].format(n=total)}</span>'
            for lg in SUPPORTED_LANGS
        )

    # Latest date for dateline (multilingual or "Soon" if empty)
    if latest_date_field:
        latest_date_html = ml(latest_date_field)
    else:
        latest_date_html = ml(None, key_for_static="soon")

    # Intro paragraph + "today's edition" link
    if latest_date_field:
        today_link = f'<br><br>{ml(None, key_for_static="today_edition")} : <a href="latest.html">{ml(latest_date_field)}</a>'
    else:
        today_link = ""

    # Selector
    lang_selector = (
        '<nav class="lang-selector">'
        '<a href="#" data-lang="fr">FR</a><span class="sep"> · </span>'
        '<a href="#" data-lang="en">EN</a><span class="sep"> · </span>'
        '<a href="#" data-lang="de">DE</a><span class="sep"> · </span>'
        '<a href="#" data-lang="it">IT</a><span class="sep"> · </span>'
        '<a href="#" data-lang="lmo">LMO</a>'
        '</nav>'
    )

    # JS for lang detection + switch (same logic as edition HTML)
    lang_js = """
(function() {
  var SUPPORTED = ['fr', 'en', 'de', 'it', 'lmo'];
  var STORAGE_KEY = 'nt-lang';
  function detectLang() {
    var pref = null;
    try { pref = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    if (pref && SUPPORTED.indexOf(pref) !== -1) return pref;
    var nav = (navigator.language || navigator.userLanguage || 'fr').toLowerCase().split('-')[0];
    return SUPPORTED.indexOf(nav) !== -1 ? nav : 'fr';
  }
  function applyLang(lang) {
    document.documentElement.lang = lang;
    var links = document.querySelectorAll('.lang-selector a');
    for (var i = 0; i < links.length; i++) {
      links[i].classList.toggle('active', links[i].dataset.lang === lang);
    }
  }
  applyLang(detectLang());
  document.addEventListener('click', function(e) {
    var a = e.target.closest('.lang-selector a');
    if (!a) return;
    e.preventDefault();
    var lang = a.dataset.lang;
    if (SUPPORTED.indexOf(lang) === -1) return;
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    applyLang(lang);
  });
})();
"""

    description = STATIC["description_template"]["fr"].format(n=total, last=escape(latest_date_fr))

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Neuron Times — Archive</title>
<meta name="description" content="{description}">
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
    justify-content: flex-start;
    align-items: center;
    padding: 0.5rem 0;
    border-top: 2px solid #0c0c0c;
    border-bottom: 2px solid #0c0c0c;
    margin-top: 1rem;
    font-family: 'Cinzel', serif;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 600;
    flex-wrap: wrap;
    gap: 1rem;
  }}
  .masthead .dateline-item {{ white-space: nowrap; }}
  .masthead .dateline-sep {{ opacity: 0.5; font-weight: 400; }}
  .masthead .dateline .lang-selector {{ margin-left: auto; }}
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
    color: #4a4a4a;
  }}
  .ours .motto {{
    font-family: 'Bodoni Moda', serif;
    font-style: italic;
    font-size: 1rem;
    color: #0c0c0c;
  }}
  .lang-selector {{
    font-family: 'Courier New', monospace;
    font-size: 0.7rem;
    letter-spacing: 1px;
    color: #4a4a4a;
    margin-left: auto;
  }}
  .lang-selector a {{
    color: #4a4a4a;
    text-decoration: none;
    padding: 0 3px;
    opacity: 0.55;
    transition: opacity 0.15s;
  }}
  .lang-selector a:hover {{ opacity: 1; }}
  .lang-selector a.active {{
    opacity: 1;
    font-weight: 700;
    text-decoration: underline;
    text-underline-offset: 3px;
  }}
  .lang-selector .sep {{ opacity: 0.4; }}

  /* Multilingual cascade : show only matching lang */
  html[lang="fr"] [data-i18n][lang]:not([lang="fr"]) {{ display: none !important; }}
  html[lang="en"] [data-i18n][lang]:not([lang="en"]) {{ display: none !important; }}
  html[lang="de"] [data-i18n][lang]:not([lang="de"]) {{ display: none !important; }}
  html[lang="it"] [data-i18n][lang]:not([lang="it"]) {{ display: none !important; }}
  html[lang="lmo"] [data-i18n][lang]:not([lang="lmo"]) {{ display: none !important; }}

  @media (max-width: 720px) {{
    html {{ font-size: 14px; }}
    .paper {{ padding: 1.5rem; margin: 0; }}
    .masthead h1 {{ font-size: 2.8rem; }}
    .archive-grid {{ grid-template-columns: 1fr; }}
    .dateline {{ flex-direction: column; gap: 8px; }}
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
      <span class="dateline-item">{ml(None, key_for_static='daily_edition')}</span>
      <span class="dateline-sep">·</span>
      <span class="dateline-item">{latest_date_html}</span>
      <span class="dateline-sep">·</span>
      <span class="dateline-item">{archive_count_html}</span>
      {lang_selector}
    </div>
  </header>

  <p class="archive-intro">
    {ml(None, key_for_static='intro')}
    {today_link}
  </p>

  <main class="archive-grid">
    {cards_html}
  </main>

  <footer class="ours">
    <div>★ ★ ★</div>
    <p class="motto">« All the AI that's fit to print »</p>
  </footer>

</div>
<script>{lang_js}</script>
</body>
</html>
"""


def main():
    if not EDITIONS_DIR.exists():
        print(f"[err] editions/ directory not found at {EDITIONS_DIR}", file=sys.stderr)
        sys.exit(1)

    editions = load_editions()
    print(f"[info] {len(editions)} editions found")

    INDEX_PATH.write_text(render_index(editions), encoding="utf-8")
    print(f"[ok] index.html generated ({len(editions)} cards, {INDEX_PATH.stat().st_size} bytes)")

    update_latest(editions)


if __name__ == "__main__":
    main()
