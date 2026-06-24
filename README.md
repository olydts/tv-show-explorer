# 📺 TV Show Explorer – Projet Python Avancé

Application desktop Python complète : séries TV via l'API TVmaze, stockage SQLite,
visualisations matplotlib et génération de rapport Word (Peter Pan – Gutenberg).

---

## 🗂️ Structure du projet

```
tv_project/
├── app.py                     # Point d'entrée – Application Tkinter
├── requirements.txt
├── README.md
│
├── db/
│   └── database.py            # DatabaseManager (SQLite) – classe abstraite + implémentation
│
├── utils/
│   ├── api_fetcher.py         # BaseFetcher → TVmazeFetcher (héritage, abstraction)
│   ├── chart_generator.py     # BaseChart → 5 types de graphiques (polymorphisme + factory)
│   ├── book_analyzer.py       # BaseTextAnalyzer → GutenbergAnalyzer (Partie 2)
│   └── report_generator.py    # WordReportGenerator – surcharge de méthodes
│
├── tests/
│   └── test_all.py            # 29 tests unitaires (unittest)
│
└── assets/                    # Graphiques générés + rapport Word (créé à l'exécution)
    ├── logo_bw.png            # Logo noir et blanc (à placer ici manuellement)
    └── ...
```

---

## ⚡ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/TON_USERNAME/tv-show-explorer.git
cd tv-show-explorer

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python app.py
```

---

## 🖼️ Image logo (Partie 2)

Le rapport Word utilise un logo noir et blanc (`assets/logo_bw.png`).
Place ton image dans le dossier `assets/` avant de générer le rapport.
Si aucune image n'est présente, un logo YNOV est généré automatiquement.

---

## 🎯 Fonctionnalités

### Partie 1 – Application Desktop (Tkinter)

| Bouton | Description |
|---|---|
| **Rechercher** | Recherche une série par nom via TVmaze API et la stocke en SQLite |
| **Séries populaires** | Charge ~485 séries populaires depuis TVmaze (2 pages × ~250) |
| **Vider la base** | Supprime toutes les données SQLite avec confirmation |
| **📈 Notes (barres)** | Graphique top 10 séries par note moyenne |
| **🥧 Statuts (camembert)** | Répartition Running / Ended / To Be Determined |
| **🌍 Langues** | Distribution des séries par langue |
| **🎭 Genres** | Distribution des genres en base |
| **💾 Enregistrer** | Export PNG du graphique affiché |

**Agrégations SQL affichées en temps réel :**
- `AVG(rating)` – note moyenne
- `COUNT(*)` – nombre de séries
- `TOP 1` – meilleure série

### Partie 2 – Rapport Word (Peter Pan – Gutenberg)

| Étape | Description |
|---|---|
| **Téléchargement** | Livre Peter Pan depuis Project Gutenberg (automatique) |
| **Extraction** | Titre, auteur, Chapitre I (ignore la table des matières) |
| **Analyse paragraphes** | Compte mots par §, arrondit à la dizaine, trie |
| **Graphique** | Histogramme distribution longueurs paragraphes |
| **Image #1** | Affiche Peter Pan téléchargée, recadrée et redimensionnée |
| **Image #2 (logo)** | Logo  pivoté 15°, collé sur l'image #1 |
| **Rapport Word** | Page titre + page graphique + page extrait + statistiques |

---

## 🏗️ Architecture POO

### Concepts utilisés (cours POO)

**Héritage :**
- `AbstractDataManager` → `DatabaseManager`
- `BaseFetcher` → `TVmazeFetcher`
- `BaseTextAnalyzer` → `GutenbergAnalyzer`
- `BaseChart` → `RatingBarChart`, `StatusPieChart`, `LanguageBarChart`, `GenreBarChart`, `ParagraphHistogram`
- `tk.Frame` → `SearchFrame`, `DataTableFrame`, `StatsFrame`, `StatusBar`
- `tk.Button` → `RoundedButton`
- `tk.Tk` → `TVShowApp`

**Classes abstraites (ABCMeta) :**
- `AbstractDataManager` : contrat CRUD pour la DB
- `BaseFetcher` : contrat fetch() pour toute API
- `BaseTextAnalyzer` : contrat load/metadata/chapter
- `BaseChart` : contrat render() pour tout graphique

**Surcharge de méthodes :**
- `WordReportGenerator._add_heading(level=1/2/3)` : comportement différent selon le niveau

**Polymorphisme :**
- `ChartFactory.generate(chart_type, data)` : appelle `render()` sur n'importe quel `BaseChart`

---

## 🧪 Tests unitaires

```bash
python -m unittest tests.test_all -v
```

**29 tests couvrant :**
- `TestDatabaseManager` (10 tests) : insert, count, clear, avg, top, status, langue, genres
- `TestTVmazeFetcher` (5 tests) : normalisation JSON → dict plat
- `TestGutenbergAnalyzer` (9 tests) : extraction métadonnées, chapitre, arrondi paragraphes
- `TestChartFactory` (5 tests) : factory pattern, rendu PNG, formule arrondi

---

## 📊 API utilisée

- **TVmaze** : `https://api.tvmaze.com` , sans clé requise
  - `/search/shows?q={query}` : recherche par nom
  - `/shows?page={n}` : séries populaires par page (~250 par page)

---

## 📄 Source littéraire

- **Peter Pan** (J. M. Barrie, 1911)
- Téléchargé automatiquement depuis [Project Gutenberg #16](https://www.gutenberg.org/ebooks/16)
- Extraction automatique du Chapitre I 

---

## 🎁 Bonus implémentés

- [x] Barre d'état en bas de la fenêtre (opérations en temps réel)
- [x] Threads pour ne pas bloquer l'UI pendant les requêtes réseau
- [x] Gestion complète des exceptions (réseau, JSON, Pillow, docx)
- [x] `check_same_thread=False` pour SQLite multi-thread
- [x] `INSERT OR IGNORE` pour éviter les doublons en base

---

## 👤 Auteur

DOTSU Olympe – Python Avancé – YNOV Campus Paris
