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
- **Le Cahier Technique** : models, infra, agents
- **La Recherche** : papers et benchmarks
- **La Communauté** : ce qui agite Hugging Face, Reddit, X

Tout en français, ton journalistique, sources cliquables vers les annonces originales.

## 4 thèmes commutables

Un bouton en haut de page bascule entre 4 esthétiques broadsheet historiques :

- **Times Victorien** — 1850-1900 Times of London, monochrome ivoire strict, Bodoni Moda
- **Le Monde Classique** — 1960-1980 broadsheet français, EB Garamond, bleu de Prusse
- **Almanach Sépia** — 1900-1920 journal rural, IM Fell English, ornements floraux
- **Gazette du Soir** — 1930-1960 tabloïd, Abril Fatface, bandeau rouge sang

Préférence persistée dans le navigateur. Effet de flip 3D entre les pages (4 pages naviguables).

## Format

Static HTML servi via GitHub Pages, custom domain, HTTPS Let's Encrypt. Tout est versionné : `reports/YYYY-MM-DD.html` pour chaque édition, `reports/YYYY-MM-DD.json` pour les données structurées (parsing programmatique).

Self-contained : CSS inline, JS minimal (theme switcher + navigation), Google Fonts via CDN. Une édition fait ~60 KB. Fonctionne offline une fois ouverte. Archivable, partageable.

## Archives

Toutes les éditions passées sont indexées sur la [page d'accueil](https://neuron-times.com) et disponibles dans le dossier [`reports/`](./reports/) du repo.

## License

Le contenu des éditions est synthétisé depuis des sources publiques avec liens d'attribution. Le design (HTML, CSS, thèmes) est original.
