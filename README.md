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
```

---

## ⚡ Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/VOTRE_USER/tv-show-explorer.git
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

## 🎯 Fonctionnalités

### Partie 1 – Application Desktop (Tkinter)

| Fonctionnalité | Description |
|---|---|
| **Recherche** | Recherche de séries par nom via l'API TVmaze (JSON) |
| **Séries populaires** | Chargement de la page 0 de l'API (250+ séries) |
| **Stockage SQLite** | Persistance locale avec détection DB non vide |
| **Vider la base** | Suppression avec confirmation utilisateur |
| **Tableau de données** | Affichage trié par note, scrollable |
| **Agrégations SQL** | AVG(rating), COUNT(*), TOP 1 calculés en SQL |
| **4 graphiques** | Barres (notes), Camembert (statuts), Langues, Genres |
| **Sauvegarde graphiques** | Export PNG via boîte de dialogue |
| **Barre d'état** | Informations temps réel sur les opérations |
| **Threads** | Appels réseau non bloquants (threading.Thread) |

### Partie 2 – Rapport Word (Peter Pan – Gutenberg)

| Étape | Description |
|---|---|
| **Téléchargement** | Livre Peter Pan depuis Project Gutenberg |
| **Extraction** | Titre, auteur, Chapitre I |
| **Analyse paragraphes** | Compte mots, arrondit à la dizaine, trie |
| **Graphique** | Distribution des longueurs (histogramme) |
| **Image #1** | Affiche Peter Pan téléchargée + recadrée/redimensionnée |
| **Image #2 (logo)** | Logo N&B généré, pivoté, collé sur l'image |
| **Rapport Word** | Page titre + page graphique + page description + stats |

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

- **TVmaze** : `https://api.tvmaze.com` – Gratuite, pas de clé requise
  - `/search/shows?q={query}` : recherche
  - `/shows?page={n}` : séries populaires

---

## 📄 Source littéraire

- **Peter Pan** (J. M. Barrie, 1911)
- Source : [Project Gutenberg #16](https://www.gutenberg.org/ebooks/16)

---

## 🎁 Bonus implémentés

- [x] Barre d'état (`StatusBar`) en bas de la fenêtre
- [x] Threads pour ne pas bloquer l'UI pendant les requêtes réseau
- [x] Gestion complète des exceptions (réseau, JSON, pillow, docx)
- [x] GitHub : publier ce dépôt pour le bonus ±1 point

---

## 👤 Auteur

Étudiant(e) – Python Avancé – YNOV Campus Paris
