"""
Tests unitaires – Projet Python Avancé
Couvre : DatabaseManager, TVmazeFetcher (normalisation), GutenbergAnalyzer, ChartFactory
"""

import sys
import os
import unittest
import math
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import DatabaseManager
from utils.api_fetcher import TVmazeFetcher
from utils.book_analyzer import GutenbergAnalyzer
from utils.chart_generator import ChartFactory, ParagraphHistogram


# ══════════════════════════════════════════════════════════════════
# Fixtures communes
# ══════════════════════════════════════════════════════════════════

SAMPLE_SHOW = {
    "id": 1,
    "name": "Breaking Bad",
    "status": "Ended",
    "rating": 9.5,
    "language": "English",
    "genres": "Drama, Crime, Thriller",
    "premiered": "2008-01-20",
    "network": "AMC",
    "summary": "A chemistry teacher turns to drug manufacturing.",
    "image_url": "https://example.com/img.jpg",
}

SAMPLE_SHOW_2 = {
    "id": 2,
    "name": "Game of Thrones",
    "status": "Ended",
    "rating": 8.9,
    "language": "English",
    "genres": "Drama, Fantasy, Adventure",
    "premiered": "2011-04-17",
    "network": "HBO",
    "summary": "Noble families fight for the Iron Throne.",
    "image_url": "",
}

SAMPLE_SHOW_3 = {
    "id": 3,
    "name": "Lupin",
    "status": "Running",
    "rating": 7.5,
    "language": "French",
    "genres": "Crime, Drama",
    "premiered": "2021-01-08",
    "network": "Netflix",
    "summary": "Un gentleman cambrioleur.",
    "image_url": "",
}


# ══════════════════════════════════════════════════════════════════
# Tests Database
# ══════════════════════════════════════════════════════════════════

class TestDatabaseManager(unittest.TestCase):
    """Tests de la couche base de données."""

    def setUp(self):
        # Base temporaire pour les tests
        self._tmp = tempfile.mkdtemp()
        DatabaseManager.DB_PATH = os.path.join(self._tmp, "test.db")
        self._db = DatabaseManager()

    def tearDown(self):
        self._db.close()
        shutil.rmtree(self._tmp, ignore_errors=True)

    def test_insert_and_count(self):
        self._db.insert(SAMPLE_SHOW)
        self.assertEqual(self._db.count(), 1)

    def test_insert_duplicate_ignored(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.insert(SAMPLE_SHOW)   # Doublon
        self.assertEqual(self._db.count(), 1)

    def test_fetch_all_returns_list(self):
        self._db.insert(SAMPLE_SHOW)
        rows = self._db.fetch_all()
        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Breaking Bad")

    def test_clear(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.clear()
        self.assertEqual(self._db.count(), 0)

    def test_average_rating(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.insert(SAMPLE_SHOW_2)
        avg = self._db.average_rating()
        expected = (9.5 + 8.9) / 2
        self.assertAlmostEqual(avg, expected, places=1)

    def test_average_rating_empty(self):
        avg = self._db.average_rating()
        self.assertEqual(avg, 0.0)

    def test_top_rated(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.insert(SAMPLE_SHOW_2)
        self._db.insert(SAMPLE_SHOW_3)
        top = self._db.top_rated(1)
        self.assertEqual(len(top), 1)
        self.assertEqual(top[0]["name"], "Breaking Bad")

    def test_count_by_status(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.insert(SAMPLE_SHOW_2)
        self._db.insert(SAMPLE_SHOW_3)
        result = self._db.count_by_status()
        statuses = {r["status"]: r["total"] for r in result}
        self.assertEqual(statuses.get("Ended"), 2)
        self.assertEqual(statuses.get("Running"), 1)

    def test_count_by_language(self):
        self._db.insert(SAMPLE_SHOW)
        self._db.insert(SAMPLE_SHOW_2)
        self._db.insert(SAMPLE_SHOW_3)
        result = self._db.count_by_language()
        langs = {r["language"]: r["total"] for r in result}
        self.assertEqual(langs.get("English"), 2)
        self.assertEqual(langs.get("French"), 1)

    def test_genres_distribution(self):
        self._db.insert(SAMPLE_SHOW)
        dist = self._db.genres_distribution()
        self.assertIn("Drama", dist)
        self.assertIn("Crime", dist)

    def test_fetch_all_sorted_by_rating(self):
        self._db.insert(SAMPLE_SHOW_3)  # 7.5
        self._db.insert(SAMPLE_SHOW)    # 9.5
        self._db.insert(SAMPLE_SHOW_2)  # 8.9
        rows = self._db.fetch_all()
        self.assertEqual(rows[0]["name"], "Breaking Bad")
        self.assertEqual(rows[1]["name"], "Game of Thrones")


# ══════════════════════════════════════════════════════════════════
# Tests API Fetcher (normalisation seulement, sans réseau)
# ══════════════════════════════════════════════════════════════════

class TestTVmazeFetcher(unittest.TestCase):
    """Tests de la normalisation des données TVmaze."""

    def setUp(self):
        self._fetcher = TVmazeFetcher()

    def test_normalize_complete_show(self):
        raw = {
            "id": 169,
            "name": "Breaking Bad",
            "status": "Ended",
            "rating": {"average": 9.5},
            "language": "English",
            "genres": ["Drama", "Crime"],
            "premiered": "2008-01-20",
            "network": {"name": "AMC"},
            "summary": "<p>A chemistry teacher turns to crime.</p>",
            "image": {"medium": "https://example.com/img.jpg"},
        }
        result = self._fetcher._normalize(raw)
        self.assertEqual(result["id"], 169)
        self.assertEqual(result["name"], "Breaking Bad")
        self.assertEqual(result["rating"], 9.5)
        self.assertEqual(result["genres"], "Drama, Crime")
        self.assertNotIn("<p>", result["summary"])  # HTML retiré
        self.assertEqual(result["network"], "AMC")

    def test_normalize_missing_rating(self):
        raw = {
            "id": 1, "name": "Test", "status": "Running",
            "rating": None, "language": "English",
            "genres": [], "premiered": "", "network": None,
            "summary": "", "image": None,
        }
        result = self._fetcher._normalize(raw)
        self.assertEqual(result["rating"], 0.0)

    def test_normalize_html_summary_stripped(self):
        raw = {
            "id": 2, "name": "X", "status": "Ended",
            "rating": {"average": 8.0}, "language": "English",
            "genres": [], "premiered": "",
            "network": {"name": "NBC"},
            "summary": "<p>Hello <b>World</b></p>",
            "image": {},
        }
        result = self._fetcher._normalize(raw)
        self.assertEqual(result["summary"], "Hello World")

    def test_normalize_summary_truncated(self):
        raw = {
            "id": 3, "name": "Y", "status": "Running",
            "rating": {"average": 7.0}, "language": "English",
            "genres": [], "premiered": "", "network": {},
            "summary": "A" * 600,
            "image": {},
        }
        result = self._fetcher._normalize(raw)
        self.assertLessEqual(len(result["summary"]), 500)

    def test_normalize_empty_genres(self):
        raw = {
            "id": 4, "name": "Z", "status": "Ended",
            "rating": {"average": 6.0}, "language": "French",
            "genres": [], "premiered": "",
            "network": {"name": "TF1"},
            "summary": "", "image": {},
        }
        result = self._fetcher._normalize(raw)
        self.assertEqual(result["genres"], "")


# ══════════════════════════════════════════════════════════════════
# Tests Book Analyzer (sans réseau)
# ══════════════════════════════════════════════════════════════════

class TestGutenbergAnalyzer(unittest.TestCase):
    """Tests de l'analyseur de texte (données simulées)."""

    FAKE_TEXT = """Title: Peter Pan
Author: J. M. Barrie

*** START OF THE PROJECT GUTENBERG EBOOK PETER PAN ***

CHAPTER I. Peter Breaks Through

All children, except one, grow up. They soon know that they will grow up,
and the way Wendy knew was this.

One day when she was two years old she was playing in a garden, and she plucked
another flower and ran with it to her mother. I suppose she must have looked
rather delightful, for Mrs. Darling put her hand to her heart and cried.

Wendy did not know this at the time. She was very young indeed when Mr. and Mrs.
Darling discovered that their children were different from other children.

Peter Pan was a special child. He could fly and he never grew up. He lived in
Neverland with the Lost Boys and Tinker Bell the fairy.

CHAPTER II. The Shadow

The shadow was caught by Mrs. Darling.
"""

    def setUp(self):
        self._analyzer = GutenbergAnalyzer()
        self._analyzer._raw_text = self.FAKE_TEXT

    def test_extract_metadata_title(self):
        meta = self._analyzer.extract_metadata()
        self.assertEqual(meta["title"], "Peter Pan")

    def test_extract_metadata_author(self):
        meta = self._analyzer.extract_metadata()
        self.assertEqual(meta["author"], "J. M. Barrie")

    def test_get_first_chapter_not_empty(self):
        chapter = self._analyzer.get_first_chapter()
        self.assertTrue(len(chapter) > 0)
        self.assertNotIn("CHAPTER II", chapter)

    def test_analyze_paragraphs_returns_dict(self):
        self._analyzer.get_first_chapter()
        result = self._analyzer.analyze_paragraphs()
        self.assertIn("distribution", result)
        self.assertIn("total_words", result)
        self.assertIn("total_paras", result)

    def test_analyze_paragraphs_rounding(self):
        """Vérifie que les mots sont arrondis à la dizaine inférieure."""
        self._analyzer.get_first_chapter()
        result = self._analyzer.analyze_paragraphs()
        dist = result["distribution"]
        for key in dist:
            self.assertEqual(key % 10, 0, f"{key} n'est pas un multiple de 10")

    def test_analyze_paragraphs_counts_positive(self):
        self._analyzer.get_first_chapter()
        result = self._analyzer.analyze_paragraphs()
        self.assertGreater(result["total_paras"], 0)
        self.assertGreater(result["total_words"], 0)

    def test_analyze_word_count_min_max(self):
        self._analyzer.get_first_chapter()
        result = self._analyzer.analyze_paragraphs()
        self.assertLessEqual(result["min_words"], result["max_words"])
        self.assertGreaterEqual(result["avg_words"], result["min_words"])

    def test_load_required_before_metadata(self):
        """Sans load(), extract_metadata doit lever RuntimeError."""
        analyzer = GutenbergAnalyzer()
        with self.assertRaises(RuntimeError):
            analyzer.extract_metadata()

    def test_load_required_before_chapter(self):
        analyzer = GutenbergAnalyzer()
        with self.assertRaises(RuntimeError):
            analyzer.get_first_chapter()


# ══════════════════════════════════════════════════════════════════
# Tests ChartFactory
# ══════════════════════════════════════════════════════════════════

class TestChartFactory(unittest.TestCase):

    def test_factory_ratings(self):
        from utils.chart_generator import RatingBarChart
        chart = ChartFactory.create("ratings")
        self.assertIsInstance(chart, RatingBarChart)

    def test_factory_unknown_raises(self):
        with self.assertRaises(ValueError):
            ChartFactory.create("unknown_type")

    def test_paragraph_chart_renders(self):
        """Test de rendu du graphique paragraphes (sans affichage)."""
        import tempfile, os
        dist = {10: 3, 20: 5, 30: 2, 40: 1, 50: 4}
        chart = ParagraphHistogram()
        # Redirige la sortie vers un fichier tmp
        chart.filepath = os.path.join(tempfile.mkdtemp(), "test_chart.png")
        path = chart.render(dist)
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 0)
        os.unlink(path)

    def test_rounding_formula(self):
        """Vérifie la formule d'arrondi à la dizaine inférieure."""
        cases = [(0, 0), (9, 0), (10, 10), (15, 10), (123, 120), (127, 120), (129, 120)]
        for raw, expected in cases:
            result = math.floor(raw / 10) * 10
            self.assertEqual(result, expected, f"floor({raw}/10)*10 should be {expected}")


# ══════════════════════════════════════════════════════════════════
# Runner
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTVmazeFetcher))
    suite.addTests(loader.loadTestsFromTestCase(TestGutenbergAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestChartFactory))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
