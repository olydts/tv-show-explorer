"""
Module d'analyse de texte Gutenberg (Partie 2).
Héritage : BaseTextAnalyzer → GutenbergAnalyzer
"""

import urllib.request
import re
import math
from abc import ABCMeta, abstractmethod


class BaseTextAnalyzer(metaclass=ABCMeta):
    """Interface pour tout analyseur de texte."""

    @abstractmethod
    def load(self, source: str) -> str:
        pass

    @abstractmethod
    def extract_metadata(self) -> dict:
        pass

    @abstractmethod
    def get_first_chapter(self) -> str:
        pass


class GutenbergAnalyzer(BaseTextAnalyzer):
    """
    Télécharge et analyse un livre du Projet Gutenberg.
    Utilisé pour Peter Pan (ID 16).
    """

    GUTENBERG_URL = "https://www.gutenberg.org/files/16/16-0.txt"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(self):
        self._raw_text: str = ""
        self._metadata: dict = {}
        self._chapter: str = ""

    # ── Chargement ─────────────────────────────
    def load(self, source: str = None) -> str:
        """Télécharge le texte depuis Gutenberg."""
        url = source or self.GUTENBERG_URL
        try:
            req = urllib.request.Request(url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw_bytes = resp.read()
                # Gutenberg peut encoder en UTF-8 ou Latin-1
                try:
                    self._raw_text = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    self._raw_text = raw_bytes.decode("latin-1")
        except Exception as e:
            raise ConnectionError(f"Impossible de télécharger le livre : {e}") from e
        return self._raw_text

    # ── Métadonnées ────────────────────────────
    def extract_metadata(self) -> dict:
        """Extrait titre, auteur depuis l'en-tête Gutenberg."""
        if not self._raw_text:
            raise RuntimeError("Appelez load() avant extract_metadata().")

        title_match = re.search(r"Title:\s*(.+)", self._raw_text)
        author_match = re.search(r"Author:\s*(.+)", self._raw_text)

        self._metadata = {
            "title":  title_match.group(1).strip() if title_match else "Peter Pan",
            "author": author_match.group(1).strip() if author_match else "J. M. Barrie",
            "source": self.GUTENBERG_URL,
        }
        return self._metadata

    @property
    def metadata(self) -> dict:
        return self._metadata

    # ── Extraction du premier chapitre ─────────
    def get_first_chapter(self) -> str:
        """Extrait le texte du premier chapitre."""
        if not self._raw_text:
            raise RuntimeError("Appelez load() avant get_first_chapter().")

        # Cherche le début du premier chapitre
        patterns = [
            r"CHAPTER\s+I[\.\s]",
            r"Chapter\s+I[\.\s]",
            r"CHAPTER\s+1[\.\s]",
        ]
        start = -1
        for pattern in patterns:
            m = re.search(pattern, self._raw_text)
            if m:
                start = m.start()
                break

        if start == -1:
            # Fallback : prend les 5000 premiers chars après l'en-tête
            end_header = self._raw_text.find("*** START OF")
            start = end_header + 200 if end_header > 0 else 1000

        # Cherche le début du chapitre II pour délimiter
        patterns_ch2 = [
            r"CHAPTER\s+II[\.\s]",
            r"Chapter\s+II[\.\s]",
            r"CHAPTER\s+2[\.\s]",
        ]
        end = -1
        for pattern in patterns_ch2:
            m = re.search(pattern, self._raw_text[start + 10:])
            if m:
                end = start + 10 + m.start()
                break

        if end == -1:
            end = start + 8000  # Fallback : 8000 chars

        self._chapter = self._raw_text[start:end].strip()
        return self._chapter

    # ── Analyse des paragraphes ─────────────────
    def analyze_paragraphs(self) -> dict:
        """
        Compte les mots par paragraphe, arrondit à la dizaine,
        et retourne la distribution {mots_arrondis: nb_paragraphes}.
        """
        if not self._chapter:
            self.get_first_chapter()

        # Sépare les paragraphes (double saut de ligne)
        raw_paragraphs = re.split(r"\n\s*\n", self._chapter)
        paragraphs = [p.strip() for p in raw_paragraphs if len(p.strip()) > 20]

        word_counts = []
        for para in paragraphs:
            words = re.findall(r"\b\w+\b", para)
            if words:
                word_counts.append(len(words))

        # Arrondit à la dizaine inférieure
        rounded = [math.floor(c / 10) * 10 for c in word_counts]

        # Distribution triée
        distribution: dict[int, int] = {}
        for val in sorted(rounded):
            distribution[val] = distribution.get(val, 0) + 1

        return {
            "distribution":   distribution,
            "paragraphs":     paragraphs,
            "word_counts":    word_counts,
            "total_words":    sum(word_counts),
            "total_paras":    len(word_counts),
            "min_words":      min(word_counts) if word_counts else 0,
            "max_words":      max(word_counts) if word_counts else 0,
            "avg_words":      round(sum(word_counts) / len(word_counts), 1) if word_counts else 0,
        }

    # ── Image ──────────────────────────────────
    def download_image(self, url: str, dest_path: str) -> str:
        """Télécharge une image depuis une URL."""
        try:
            req = urllib.request.Request(url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(dest_path, "wb") as f:
                    f.write(resp.read())
            return dest_path
        except Exception as e:
            raise ConnectionError(f"Impossible de télécharger l'image : {e}") from e
