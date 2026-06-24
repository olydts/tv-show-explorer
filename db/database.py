"""
Module de gestion de la base de données SQLite.
Utilise la POO : classe DatabaseManager encapsule toutes les opérations DB.
"""

import sqlite3
import os
from abc import ABCMeta, abstractmethod



# Classe abstraite (contrat pour tout gestionnaire de données)

class AbstractDataManager(metaclass=ABCMeta):
    """Interface définissant les opérations obligatoires sur les données."""

    @abstractmethod
    def insert(self, data: dict) -> None:
        pass

    @abstractmethod
    def fetch_all(self) -> list:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    @abstractmethod
    def count(self) -> int:
        pass



# Implémentation concrète SQLite

class DatabaseManager(AbstractDataManager):
    """Gère la persistance des séries TV dans SQLite."""

    DB_PATH = os.path.join(os.path.dirname(__file__), "tv_shows.db")

    def __init__(self):
        self._connection = None
        self._init_db()

    #  Connexion
    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.DB_PATH)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def _init_db(self) -> None:
        """Crée la table si elle n'existe pas."""
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shows (
                id          INTEGER PRIMARY KEY,
                name        TEXT NOT NULL,
                status      TEXT,
                rating      REAL,
                language    TEXT,
                genres      TEXT,
                premiered   TEXT,
                network     TEXT,
                summary     TEXT,
                image_url   TEXT
            )
        """)
        conn.commit()

    #  Opérations CRUD 
    def insert(self, data: dict) -> None:
        """Insère une série. Ignore si l'ID existe déjà."""
        conn = self._get_connection()
        conn.execute("""
            INSERT OR IGNORE INTO shows
            (id, name, status, rating, language, genres, premiered, network, summary, image_url)
            VALUES (:id, :name, :status, :rating, :language, :genres, :premiered, :network, :summary, :image_url)
        """, data)
        conn.commit()

    def fetch_all(self) -> list:
        """Retourne toutes les séries sous forme de liste de dict."""
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM shows ORDER BY rating DESC").fetchall()
        return [dict(row) for row in rows]

    def clear(self) -> None:
        """Supprime toutes les données."""
        conn = self._get_connection()
        conn.execute("DELETE FROM shows")
        conn.commit()

    def count(self) -> int:
        """Nombre de séries en base."""
        conn = self._get_connection()
        return conn.execute("SELECT COUNT(*) FROM shows").fetchone()[0]

    #  Agrégations SQL 
    def average_rating(self) -> float:
        """Moyenne des notes (requête SQL)."""
        conn = self._get_connection()
        result = conn.execute(
            "SELECT AVG(rating) FROM shows WHERE rating IS NOT NULL AND rating > 0"
        ).fetchone()[0]
        return round(result, 2) if result else 0.0

    def top_rated(self, n: int = 5) -> list:
        """Top N séries par note."""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT name, rating FROM shows WHERE rating > 0 ORDER BY rating DESC LIMIT ?", (n,)
        ).fetchall()
        return [dict(row) for row in rows]

    def count_by_status(self) -> list:
        """Nombre de séries par statut."""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT status, COUNT(*) as total FROM shows GROUP BY status ORDER BY total DESC"
        ).fetchall()
        return [dict(row) for row in rows]

    def count_by_language(self) -> list:
        """Nombre de séries par langue."""
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT language, COUNT(*) as total FROM shows WHERE language IS NOT NULL "
            "GROUP BY language ORDER BY total DESC LIMIT 8"
        ).fetchall()
        return [dict(row) for row in rows]

    def genres_distribution(self) -> dict:
        """Distribution des genres (parsing du champ genres)."""
        conn = self._get_connection()
        rows = conn.execute("SELECT genres FROM shows WHERE genres IS NOT NULL").fetchall()
        genre_count = {}
        for row in rows:
            for genre in row["genres"].split(","):
                g = genre.strip()
                if g:
                    genre_count[g] = genre_count.get(g, 0) + 1
        return dict(sorted(genre_count.items(), key=lambda x: x[1], reverse=True))

    def close(self) -> None:
        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self):
        self.close()
