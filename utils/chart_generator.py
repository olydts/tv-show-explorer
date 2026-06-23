"""
Module de génération de graphiques matplotlib.
Héritage : BaseChart → BarChart, PieChart, HistogramChart
Polymorphisme : chaque sous-classe implémente render() différemment.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Backend sans affichage (pour sauvegarde fichier)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from abc import ABCMeta, abstractmethod

CHARTS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
os.makedirs(CHARTS_DIR, exist_ok=True)

PALETTE = ["#6C63FF", "#FF6584", "#43BFDB", "#FFC857", "#4CAF50", "#FF7043", "#AB47BC", "#26A69A"]


class BaseChart(metaclass=ABCMeta):
    """Classe abstraite : contrat pour tous les graphiques."""

    def __init__(self, title: str, filename: str):
        self.title = title
        self.filepath = os.path.join(CHARTS_DIR, filename)
        self._fig = None
        self._ax = None

    @abstractmethod
    def render(self, data: dict | list) -> str:
        """Génère le graphique et retourne le chemin du fichier sauvegardé."""
        pass

    def _setup(self, figsize=(10, 6)) -> None:
        """Initialise la figure avec style commun."""
        plt.style.use("seaborn-v0_8-darkgrid")
        self._fig, self._ax = plt.subplots(figsize=figsize)
        self._fig.patch.set_facecolor("#1E1E2E")
        self._ax.set_facecolor("#2A2A3E")
        self._ax.tick_params(colors="white")
        self._ax.xaxis.label.set_color("white")
        self._ax.yaxis.label.set_color("white")
        self._ax.title.set_color("white")
        for spine in self._ax.spines.values():
            spine.set_edgecolor("#444466")

    def _save(self) -> str:
        """Sauvegarde et ferme la figure."""
        self._fig.tight_layout()
        self._fig.savefig(self.filepath, dpi=120, bbox_inches="tight",
                          facecolor=self._fig.get_facecolor())
        plt.close(self._fig)
        return self.filepath


class RatingBarChart(BaseChart):
    """Graphique barres : top séries par note."""

    def __init__(self):
        super().__init__("Top Séries par Note", "chart_ratings.png")

    def render(self, data: list) -> str:
        """data = [{'name': str, 'rating': float}, ...]"""
        self._setup(figsize=(10, 6))

        names = [d["name"][:20] for d in data]
        ratings = [d["rating"] for d in data]
        colors = PALETTE[:len(names)]

        bars = self._ax.barh(names, ratings, color=colors, edgecolor="#444466", height=0.6)
        self._ax.set_xlim(0, 10.5)
        self._ax.set_xlabel("Note moyenne", color="white", fontsize=11)
        self._ax.set_title(self.title, color="white", fontsize=14, fontweight="bold", pad=15)

        for bar, rating in zip(bars, ratings):
            self._ax.text(
                bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{rating:.1f}", va="center", color="white", fontsize=10, fontweight="bold"
            )
        self._ax.invert_yaxis()
        return self._save()


class StatusPieChart(BaseChart):
    """Graphique camembert : répartition des statuts."""

    def __init__(self):
        super().__init__("Répartition par Statut", "chart_status.png")

    def render(self, data: list) -> str:
        """data = [{'status': str, 'total': int}, ...]"""
        self._setup(figsize=(8, 8))

        labels = [d["status"] for d in data]
        values = [d["total"] for d in data]
        colors = PALETTE[:len(labels)]

        wedges, texts, autotexts = self._ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct="%1.1f%%",
            startangle=140,
            pctdistance=0.82,
            wedgeprops={"linewidth": 2, "edgecolor": "#1E1E2E"}
        )
        for text in texts + autotexts:
            text.set_color("white")
            text.set_fontsize(11)

        self._ax.set_title(self.title, color="white", fontsize=14, fontweight="bold", pad=20)
        return self._save()


class LanguageBarChart(BaseChart):
    """Graphique barres verticales : séries par langue."""

    def __init__(self):
        super().__init__("Séries par Langue", "chart_languages.png")

    def render(self, data: list) -> str:
        """data = [{'language': str, 'total': int}, ...]"""
        self._setup(figsize=(10, 6))

        langs = [d["language"] for d in data]
        totals = [d["total"] for d in data]
        x = range(len(langs))
        colors = PALETTE[:len(langs)]

        bars = self._ax.bar(x, totals, color=colors, edgecolor="#444466", width=0.6)
        self._ax.set_xticks(list(x))
        self._ax.set_xticklabels(langs, rotation=30, ha="right", color="white")
        self._ax.set_ylabel("Nombre de séries", color="white", fontsize=11)
        self._ax.set_title(self.title, color="white", fontsize=14, fontweight="bold", pad=15)

        for bar, total in zip(bars, totals):
            self._ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(total), ha="center", color="white", fontsize=10, fontweight="bold"
            )
        return self._save()


class GenreBarChart(BaseChart):
    """Graphique genres disponibles dans la DB."""

    def __init__(self):
        super().__init__("Distribution des Genres", "chart_genres.png")

    def render(self, data: dict) -> str:
        """data = {'Genre': count, ...}"""
        self._setup(figsize=(11, 6))

        items = list(data.items())[:10]
        genres = [g for g, _ in items]
        counts = [c for _, c in items]
        colors = PALETTE[:len(genres)]

        bars = self._ax.barh(genres, counts, color=colors, edgecolor="#444466", height=0.6)
        self._ax.set_xlabel("Nombre de séries", color="white", fontsize=11)
        self._ax.set_title(self.title, color="white", fontsize=14, fontweight="bold", pad=15)

        for bar, count in zip(bars, counts):
            self._ax.text(
                bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", color="white", fontsize=10
            )
        self._ax.invert_yaxis()
        return self._save()


class ParagraphHistogram(BaseChart):
    """Histogramme distribution longueurs paragraphes (Partie 2)."""

    def __init__(self):
        super().__init__("Distribution des longueurs de paragraphes – Chapitre I", "chart_paragraphs.png")

    def render(self, data: dict) -> str:
        """data = {nb_mots_arrondi: nb_paragraphes, ...}"""
        self._setup(figsize=(12, 6))

        x_vals = sorted(data.keys())
        y_vals = [data[k] for k in x_vals]
        colors = [PALETTE[i % len(PALETTE)] for i in range(len(x_vals))]

        bars = self._ax.bar(
            [str(v) for v in x_vals], y_vals,
            color=colors, edgecolor="#444466", width=0.7
        )
        self._ax.set_xlabel("Nombre de mots (arrondi à la dizaine)", color="white", fontsize=11)
        self._ax.set_ylabel("Nombre de paragraphes", color="white", fontsize=11)
        self._ax.set_title(self.title, color="white", fontsize=13, fontweight="bold", pad=15)
        plt.xticks(rotation=45, ha="right")

        for bar, count in zip(bars, y_vals):
            self._ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.05,
                str(count), ha="center", color="white", fontsize=9
            )
        return self._save()


# ── Factory : renvoie le bon graphique selon le type demandé ──
class ChartFactory:
    """Polymorphisme via factory : sélectionne et exécute le bon graphique."""

    _registry = {
        "ratings":    RatingBarChart,
        "status":     StatusPieChart,
        "languages":  LanguageBarChart,
        "genres":     GenreBarChart,
        "paragraphs": ParagraphHistogram,
    }

    @classmethod
    def create(cls, chart_type: str) -> BaseChart:
        klass = cls._registry.get(chart_type)
        if klass is None:
            raise ValueError(f"Type de graphique inconnu : '{chart_type}'")
        return klass()

    @classmethod
    def generate(cls, chart_type: str, data) -> str:
        """Crée et rend directement un graphique."""
        chart = cls.create(chart_type)
        return chart.render(data)
