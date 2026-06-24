"""
Module de récupération des données TVmaze.
Héritage : BaseFetcher → TVmazeFetcher
"""

import urllib.request
import urllib.parse
import json
import re
from abc import ABCMeta, abstractmethod


class BaseFetcher(metaclass=ABCMeta):
    """Classe abstraite pour tout fetcher de données distantes."""

    BASE_URL: str = ""
    HEADERS: dict = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
    }

    @abstractmethod
    def fetch(self, query: str) -> list:
        pass

    def _get(self, url: str, timeout: int = 10) -> dict | list | None:
        """Requête HTTP GET générique avec gestion d'erreurs."""
        try:
            req = urllib.request.Request(url, headers=self.HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise ConnectionError(f"Erreur HTTP {e.code} : {e.reason}") from e
        except urllib.error.URLError as e:
            raise ConnectionError(f"Erreur réseau : {e.reason}") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"Réponse JSON invalide : {e}") from e
        except Exception as e:
            raise RuntimeError(f"Erreur inattendue : {e}") from e


class TVmazeFetcher(BaseFetcher):
    """Récupère et normalise les données de l'API TVmaze."""

    BASE_URL = "https://api.tvmaze.com"

    def fetch(self, query: str) -> list:
        """
        Recherche des séries par mot-clé.
        Retourne une liste de dicts normalisés prêts pour SQLite.
        """
        encoded = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/search/shows?q={encoded}"
        raw = self._get(url)
        return [self._normalize(item["show"]) for item in raw if "show" in item]

    def fetch_popular(self, pages: int = 4) -> list:
        all_shows = []
        for page in range(pages):
            try:
                url = f"{self.BASE_URL}/shows?page={page}"
                raw = self._get(url)
                all_shows.extend([self._normalize(show) for show in raw])
            except Exception:
                break  # Arrête si plus de pages disponibles
        return all_shows

    def _normalize(self, show: dict) -> dict:
        """Transforme une réponse TVmaze en dict plat pour la DB."""
        rating = show.get("rating", {}) or {}
        network = show.get("network", {}) or {}
        image = show.get("image", {}) or {}

        summary_raw = show.get("summary", "") or ""
        summary_clean = re.sub(r"<[^>]+>", "", summary_raw).strip()

        genres = show.get("genres", []) or []

        return {
            "id":        show.get("id", 0),
            "name":      show.get("name", "Inconnu"),
            "status":    show.get("status", "Unknown"),
            "rating":    rating.get("average") or 0.0,
            "language":  show.get("language", ""),
            "genres":    ", ".join(genres),
            "premiered": show.get("premiered", ""),
            "network":   network.get("name", ""),
            "summary":   summary_clean[:500],
            "image_url": image.get("medium", ""),
        }
