# The Neuron Times

> All the AI that's fit to print

A daily AI watch newspaper, broadsheet old-school style with commutable themes.

**Live :** [https://neuron-times.com](https://neuron-times.com)
**Mirror redirect :** `the-ai-loop.com` → `neuron-times.com` (301)

## What is this

A daily-generated, static HTML report aggregating the most significant signals from the AI ecosystem — frontier models, coding agents, infrastructure, research papers, community signals. Inspired by traditional broadsheet newspapers (NYT, Le Monde, Guardian) with modern interactive enhancements (theme switcher, multi-page navigation, 3D page transitions).

## Repo structure

```
neuron-times/
├── reports/                    Daily reports (YYYY-MM-DD.html + .json + .md)
├── latest.html                 Mirror of the most recent report (stable URL)
├── index.html                  Archive index, auto-regenerated on push
├── CNAME                       Custom domain config for GitHub Pages
├── build_index.py              Script that regenerates index.html from reports/*.json
└── .github/workflows/
    └── regenerate-index.yml    Workflow rebuilding index on push to reports/
```

## Themes

Each report HTML embeds 4 commutable themes (top-bar switcher, persisted via localStorage) :

- **Times Victorien** — Bodoni Moda, monochrome strict ivoire (1850-1900 Times of London style)
- **Le Monde Classique** — EB Garamond + bleu de Prusse (1960-1980 broadsheet français)
- **Almanach Sépia** — IM Fell English + Pinyon Script + ornements floraux (1900-1920 journal rural)
- **Gazette du Soir** — Abril Fatface + bandeau rouge sang (1930-1960 tabloïd dramatique)

## Self-contained

Each HTML report is fully self-contained : CSS inline, Google Fonts via CDN, JS minimal (theme switcher + page navigation). Works offline once loaded, portable, archivable.

## License

The reports content is curated from publicly available sources with attribution links. The visual design (HTML template, CSS, themes) is original work.
