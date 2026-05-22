# The Neuron Times

> All the AI that's fit to print

Votre édition quotidienne de la veille IA, condensée dans un journal broadsheet old-school. Publiée tous les matins à 7h CET.

**→ [https://neuron-times.com](https://neuron-times.com)**

## L'idée

L'écosystème IA produit plus de signal en une semaine qu'un humain peut absorber en un mois. Twitter, arXiv, Hugging Face, blogs labos, GitHub releases : la veille devient un travail à temps plein.

Ce site lit pour vous. Chaque matin, une centaine de sources sont parcourues, classées, et synthétisées en une édition au format broadsheet. Les annonces majeures en Une, les signaux secondaires en sidebar, les analyses techniques en pages intérieures.

Objectif : 5 minutes de lecture le matin = veille IA à jour pour la journée.

## Ce que vous trouvez chaque jour

- **À la Une** : un papier long sur l'annonce du jour (release de modèle, M&A, breakthrough recherche)
- **From the Wires** : 4 signaux majeurs en bref
- **Modèles & Frontière** : annonces des labos frontière (Anthropic, OpenAI, Google/DeepMind, Meta, Mistral, DeepSeek, xAI)
- **Le Cahier Technique** : agents, CLI, inference engines, dev tools
- **La Recherche** : papers et benchmarks
- **Tour des labos** : signaux des labos non-frontière (Apple ML, HuggingFace, Microsoft Research, Cloudflare AI, Modal, Together, Nous Research, IBM Research, NVIDIA, etc.)
- **Écosystème & Édito** : signaux community + édito transversal

Ton journalistique, sources cliquables vers les annonces originales.

## Multilingue — 5 langues

Chaque édition est publiée simultanément dans **5 langues**, avec un sélecteur dans le masthead :

- **FR** — français (langue source)
- **EN** — anglais (international)
- **DE** — allemand (suisse standard)
- **IT** — italien (suisse standard)
- **LMO** — lombard (langue gallo-italique parlée au Tessin suisse et en Lombardie italienne)

La langue active est **auto-détectée** au premier load via `navigator.language` du navigateur. L'utilisateur peut la **changer** en cliquant sur un code dans le sélecteur ; la préférence est persistée en `localStorage` pour les visites suivantes. Switch instantané sans rechargement de page (cascade CSS sur `<html lang="...">`).

Tous les fichiers `editions/YYYY-MM-DD.json` ont un schéma `multilingual-v1` avec chaque champ texte exprimé en objet `{fr, en, de, it, lmo}`.

## Format

Static HTML servi via GitHub Pages, custom domain, HTTPS Let's Encrypt. Tout est versionné :

- `editions/YYYY-MM-DD.html` pour chaque édition (HTML self-contained, ~80-150 KB raw, ~30-40 KB gzippé)
- `editions/YYYY-MM-DD.json` pour les données structurées multilingues (parsing programmatique, RSS futur, etc.)
- `latest.html` : miroir de la dernière édition (URL stable)
- `index.html` : archives chronologiques, regénéré par GitHub Actions à chaque push

Self-contained : CSS inline, JS minimal (lang detection + sélecteur + thème), Google Fonts via CDN. Fonctionne offline une fois la page chargée.

## Archives

Toutes les éditions passées sont indexées sur la [page d'accueil](https://neuron-times.com) et disponibles dans le dossier [`editions/`](./editions/) du repo.

## Roadmap (non shipped)

- Thèmes commutables : 4 esthétiques broadsheet historiques (Times Victorien, Le Monde Classique, Almanach Sépia, Gazette du Soir) avec switcher persisté
- Effet de flip 3D entre les pages (multi-pages navigables)
- Flux RSS / Atom (`feed.xml`)
- OG meta tags pour partage LinkedIn / Twitter (image OG dynamique masthead + headline du jour)

## License

Le contenu des éditions est synthétisé depuis des sources publiques avec liens d'attribution. Le design (HTML, CSS) est original.
