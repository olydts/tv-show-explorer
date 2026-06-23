"""
Application Desktop – Séries TV
Projet Python Avancé – Tkinter + SQLite + TVmaze API + Partie 2 (Peter Pan / Gutenberg)

Architecture OOP :
  - TVShowApp     : classe principale de l'application (fenêtre Tk)
  - SearchFrame   : frame de recherche (héritage de tk.Frame)
  - DataTableFrame: frame d'affichage des données (héritage de tk.Frame)
  - StatsFrame    : frame des agrégations SQL (héritage de tk.Frame)
  - ChartFrame    : frame d'affichage graphique (héritage de tk.Frame)
  - StatusBar     : barre d'état en bas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys

# Ajout du répertoire courant au path
sys.path.insert(0, os.path.dirname(__file__))

from db.database import DatabaseManager
from utils.api_fetcher import TVmazeFetcher
from utils.chart_generator import ChartFactory
from utils.book_analyzer import GutenbergAnalyzer
from utils.report_generator import WordReportGenerator

# ══════════════════════════════════════════════════════════════════
# Constantes de thème
# ══════════════════════════════════════════════════════════════════
BG_DARK   = "#1E1E2E"
BG_PANEL  = "#2A2A3E"
BG_CARD   = "#313145"
ACCENT    = "#6C63FF"
ACCENT2   = "#FF6584"
TEXT_MAIN = "#E0E0F0"
TEXT_DIM  = "#8888AA"
BTN_BG    = "#6C63FF"
BTN_FG    = "#FFFFFF"
BTN_HOV   = "#5A52E0"
SUCCESS   = "#4CAF50"
WARNING   = "#FFC857"
FONT_H1   = ("Segoe UI", 18, "bold")
FONT_H2   = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_CODE = ("Consolas", 9)


# ══════════════════════════════════════════════════════════════════
# Composants réutilisables
# ══════════════════════════════════════════════════════════════════

class RoundedButton(tk.Button):
    """Bouton stylisé (surcharge de tk.Button)."""

    def __init__(self, parent, text, command=None, bg=BTN_BG, fg=BTN_FG,
                 width=18, **kwargs):
        super().__init__(
            parent, text=text, command=command,
            bg=bg, fg=fg, relief="flat",
            activebackground=BTN_HOV, activeforeground=fg,
            cursor="hand2", font=("Segoe UI", 10, "bold"),
            width=width, pady=6, **kwargs
        )
        self.bind("<Enter>", lambda e: self.config(bg=BTN_HOV))
        self.bind("<Leave>", lambda e: self.config(bg=bg))


class StatusBar(tk.Frame):
    """Barre d'état en bas de la fenêtre."""

    def __init__(self, parent):
        super().__init__(parent, bg="#111122", height=28)
        self.pack(side="bottom", fill="x")
        self._label = tk.Label(
            self, text="✓ Application prête", bg="#111122",
            fg=TEXT_DIM, font=("Segoe UI", 9), anchor="w", padx=10
        )
        self._label.pack(side="left", fill="x")
        self._count_label = tk.Label(
            self, text="DB : 0 série", bg="#111122",
            fg=TEXT_DIM, font=("Segoe UI", 9), anchor="e", padx=10
        )
        self._count_label.pack(side="right")

    def set(self, msg: str, color: str = TEXT_DIM) -> None:
        self._label.config(text=f"  {msg}", fg=color)

    def set_count(self, n: int) -> None:
        self._count_label.config(text=f"DB : {n} série{'s' if n > 1 else ''}")


# ══════════════════════════════════════════════════════════════════
# Frames principales (héritage de tk.Frame)
# ══════════════════════════════════════════════════════════════════

class SearchFrame(tk.Frame):
    """Barre de recherche et menu actions."""

    def __init__(self, parent, on_search, on_popular, on_clear):
        super().__init__(parent, bg=BG_PANEL, pady=12, padx=14)

        tk.Label(self, text="🔍  Rechercher une série :", bg=BG_PANEL,
                 fg=TEXT_MAIN, font=FONT_H2).grid(row=0, column=0, padx=(0, 8), sticky="w")

        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self, textvariable=self._var, font=("Segoe UI", 12),
            bg=BG_CARD, fg=TEXT_MAIN, insertbackground=ACCENT,
            relief="flat", width=32
        )
        self._entry.grid(row=0, column=1, padx=6, ipady=6)
        self._entry.bind("<Return>", lambda e: on_search(self._var.get()))

        RoundedButton(self, "Rechercher", command=lambda: on_search(self._var.get()),
                      width=14).grid(row=0, column=2, padx=4)
        RoundedButton(self, "Séries populaires", command=on_popular,
                      bg="#43BFDB", width=16).grid(row=0, column=3, padx=4)
        RoundedButton(self, "Vider la base", command=on_clear,
                      bg=ACCENT2, width=14).grid(row=0, column=4, padx=4)

    def get_query(self) -> str:
        return self._var.get().strip()


class DataTableFrame(tk.Frame):
    """Affichage des séries sous forme de tableau."""

    COLS = ("Titre", "Statut", "Note", "Langue", "Genres", "Réseau", "Année")

    def __init__(self, parent):
        super().__init__(parent, bg=BG_DARK)

        # Header
        tk.Label(self, text="📺  Séries en base de données", bg=BG_DARK,
                 fg=TEXT_MAIN, font=FONT_H2).pack(anchor="w", padx=12, pady=(10, 4))

        # Treeview
        frame_tree = tk.Frame(self, bg=BG_DARK)
        frame_tree.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.Treeview",
                         background=BG_CARD, foreground=TEXT_MAIN,
                         fieldbackground=BG_CARD, rowheight=26,
                         font=("Segoe UI", 9))
        style.configure("Dark.Treeview.Heading",
                         background=BG_PANEL, foreground=ACCENT,
                         font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "#FFFFFF")])

        self._tree = ttk.Treeview(
            frame_tree, columns=self.COLS, show="headings",
            style="Dark.Treeview", selectmode="browse"
        )
        col_widths = [200, 90, 60, 80, 180, 120, 70]
        for col, w in zip(self.COLS, col_widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center")
        self._tree.column("Titre", anchor="w")

        scrollbar = ttk.Scrollbar(frame_tree, orient="vertical",
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def load(self, rows: list) -> None:
        """Recharge le tableau avec de nouvelles données."""
        self._tree.delete(*self._tree.get_children())
        for row in rows:
            premiered = (row.get("premiered") or "")[:4]
            rating    = f"{row['rating']:.1f}" if row.get("rating") else "—"
            self._tree.insert("", "end", values=(
                row.get("name", ""),
                row.get("status", ""),
                rating,
                row.get("language", ""),
                row.get("genres", ""),
                row.get("network", ""),
                premiered,
            ))


class StatsFrame(tk.Frame):
    """Affichage des agrégations SQL."""

    def __init__(self, parent, on_show_chart, on_gen_report):
        super().__init__(parent, bg=BG_PANEL, pady=10, padx=14)

        tk.Label(self, text="📊  Agrégations SQL", bg=BG_PANEL,
                 fg=TEXT_MAIN, font=FONT_H2).grid(row=0, column=0, columnspan=2,
                                                    sticky="w", pady=(0, 8))

        # Labels des stats
        self._avg_var   = tk.StringVar(value="—")
        self._count_var = tk.StringVar(value="—")
        self._top_var   = tk.StringVar(value="—")

        stats = [
            ("Note moyenne (SQL AVG) :", self._avg_var),
            ("Séries enregistrées (SQL COUNT) :", self._count_var),
            ("Meilleure série :", self._top_var),
        ]
        for i, (label, var) in enumerate(stats):
            tk.Label(self, text=label, bg=BG_PANEL, fg=TEXT_DIM,
                     font=FONT_BODY).grid(row=i+1, column=0, sticky="w", pady=2)
            tk.Label(self, textvariable=var, bg=BG_PANEL, fg=WARNING,
                     font=("Segoe UI", 10, "bold")).grid(row=i+1, column=1, sticky="w", padx=8)

        # Boutons graphiques
        btn_frame = tk.Frame(self, bg=BG_PANEL)
        btn_frame.grid(row=5, column=0, columnspan=4, pady=(12, 0), sticky="w")

        charts = [
            ("📈 Notes (barres)", "ratings"),
            ("🥧 Statuts (camembert)", "status"),
            ("🌍 Langues", "languages"),
            ("🎭 Genres", "genres"),
        ]
        for i, (label, ctype) in enumerate(charts):
            RoundedButton(btn_frame, label, width=20,
                          command=lambda t=ctype: on_show_chart(t),
                          bg=BG_CARD).grid(row=0, column=i, padx=4)

        tk.Frame(self, bg=BG_PANEL).grid(row=5, column=4, padx=20)
        RoundedButton(self, "📄 Générer le rapport Word (Partie 2)",
                      command=on_gen_report, width=36,
                      bg=SUCCESS).grid(row=6, column=0, columnspan=4,
                                       pady=(10, 0), sticky="w")

    def update_stats(self, avg: float, count: int, top: str) -> None:
        self._avg_var.set(f"{avg:.2f} / 10" if avg else "—")
        self._count_var.set(str(count))
        self._top_var.set(top or "—")


# ══════════════════════════════════════════════════════════════════
# Application principale
# ══════════════════════════════════════════════════════════════════

class TVShowApp(tk.Tk):
    """
    Fenêtre principale de l'application.
    Coordonne tous les modules : DB, API, graphiques, rapport.
    """

    def __init__(self):
        super().__init__()
        self.title("📺  TV Show Explorer – Python Avancé")
        self.geometry("1100x750")
        self.minsize(900, 600)
        self.configure(bg=BG_DARK)

        # Modules métier
        self._db      = DatabaseManager()
        self._fetcher = TVmazeFetcher()

        self._build_ui()
        self._refresh_table()
        self._refresh_stats()

    # ── Construction UI ──────────────────────────
    def _build_ui(self) -> None:
        # Titre
        header = tk.Frame(self, bg=ACCENT, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📺  TV Show Explorer",
                 bg=ACCENT, fg="white", font=FONT_H1).pack(side="left", padx=18, pady=8)
        tk.Label(header, text="Projet Python Avancé · TVmaze API · SQLite",
                 bg=ACCENT, fg="#DDDDFF", font=("Segoe UI", 9, "italic")).pack(
                     side="right", padx=18)

        # Barre de recherche
        self._search_frame = SearchFrame(
            self,
            on_search=self._on_search,
            on_popular=self._on_popular,
            on_clear=self._on_clear,
        )
        self._search_frame.pack(fill="x", padx=10, pady=6)

        # Panneau central : table + stats
        center = tk.Frame(self, bg=BG_DARK)
        center.pack(fill="both", expand=True, padx=10, pady=4)

        # Table (70% de la hauteur)
        self._table_frame = DataTableFrame(center)
        self._table_frame.pack(fill="both", expand=True)

        # Stats (partie basse)
        self._stats_frame = StatsFrame(
            center,
            on_show_chart=self._on_show_chart,
            on_gen_report=self._on_gen_report,
        )
        self._stats_frame.pack(fill="x", pady=6)

        # Barre d'état
        self._status = StatusBar(self)

    # ── Actions utilisateur ──────────────────────
    def _on_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            messagebox.showwarning("Saisie vide", "Entrez un titre de série à rechercher.")
            return
        self._run_in_thread(
            task=lambda: self._fetch_and_store(query),
            status_msg=f"🔄 Recherche : {query}…",
        )

    def _on_popular(self) -> None:
        self._run_in_thread(
            task=lambda: self._fetch_popular(),
            status_msg="🔄 Chargement des séries populaires…",
        )

    def _on_clear(self) -> None:
        if not messagebox.askyesno("Confirmer", "Vider toute la base de données ?"):
            return
        self._db.clear()
        self._refresh_table()
        self._refresh_stats()
        self._status.set("🗑️  Base de données vidée.", color=ACCENT2)

    def _on_show_chart(self, chart_type: str) -> None:
        """Génère et ouvre un graphique dans une nouvelle fenêtre."""
        try:
            data = self._get_chart_data(chart_type)
            if not data:
                messagebox.showinfo("Données manquantes",
                                    "Téléchargez d'abord des séries.")
                return
            path = ChartFactory.generate(chart_type, data)
            self._show_chart_window(path, chart_type)
            self._status.set(f"✅ Graphique '{chart_type}' généré.", color=SUCCESS)
        except Exception as e:
            messagebox.showerror("Erreur graphique", str(e))

    def _on_gen_report(self) -> None:
        """Lance la génération du rapport Word (Partie 2)."""
        self._run_in_thread(
            task=self._generate_word_report,
            status_msg="📄 Génération du rapport Word (Peter Pan)…",
        )

    # ── Logique métier ───────────────────────────
    def _fetch_and_store(self, query: str) -> None:
        """Télécharge depuis TVmaze et stocke en DB (thread secondaire)."""
        shows = self._fetcher.fetch(query)
        if not shows:
            self.after(0, lambda: self._status.set(
                f"⚠️  Aucun résultat pour '{query}'.", color=WARNING))
            return
        # Détection DB non vide
        if self._db.count() > 0:
            answer = self._ask_main_thread(
                "Base non vide",
                f"La base contient déjà {self._db.count()} série(s).\n"
                "Voulez-vous ajouter les nouveaux résultats ?"
            )
            if not answer:
                return
        for show in shows:
            self._db.insert(show)
        self.after(0, self._refresh_table)
        self.after(0, self._refresh_stats)
        self.after(0, lambda: self._status.set(
            f"✅ {len(shows)} série(s) ajoutée(s) pour '{query}'.", color=SUCCESS))

    def _fetch_popular(self) -> None:
        shows = self._fetcher.fetch_popular()
        if self._db.count() > 0:
            answer = self._ask_main_thread(
                "Base non vide",
                f"La base contient déjà {self._db.count()} série(s).\n"
                "Ajouter les séries populaires ?"
            )
            if not answer:
                return
        for show in shows:
            self._db.insert(show)
        self.after(0, self._refresh_table)
        self.after(0, self._refresh_stats)
        self.after(0, lambda: self._status.set(
            f"✅ {len(shows)} séries populaires chargées.", color=SUCCESS))

    def _generate_word_report(self) -> None:
        """Partie 2 : analyse Peter Pan + génération rapport Word."""
        try:
            self.after(0, lambda: self._status.set(
                "📥 Téléchargement de Peter Pan (Gutenberg)…", color=WARNING))

            analyzer = GutenbergAnalyzer()
            analyzer.load()
            metadata  = analyzer.extract_metadata()
            _         = analyzer.get_first_chapter()
            analysis  = analyzer.analyze_paragraphs()

            # Graphique paragraphes
            self.after(0, lambda: self._status.set(
                "📊 Génération du graphique…", color=WARNING))
            chart_path = ChartFactory.generate("paragraphs", analysis["distribution"])

            # Image Peter Pan (illustration domaine public)
            assets_dir = os.path.join(os.path.dirname(__file__), "assets")
            os.makedirs(assets_dir, exist_ok=True)
            img_path  = os.path.join(assets_dir, "peter_pan_cover.jpg")
            logo_path = os.path.join(assets_dir, "logo_bw.png")

            IMAGE_URL = (
                "https://upload.wikimedia.org/wikipedia/commons/thumb/"
                "3/3d/Peter_Pan_1915_poster.jpg/440px-Peter_Pan_1915_poster.jpg"
            )
            try:
                analyzer.download_image(IMAGE_URL, img_path)
                # Recadrage + rotation logo avec Pillow
                self._process_images(img_path, logo_path)
            except Exception:
                img_path  = None
                logo_path = None

            # Génération rapport Word
            self.after(0, lambda: self._status.set(
                "📝 Génération du document Word…", color=WARNING))
            report = WordReportGenerator()
            out_path = os.path.join(assets_dir, "rapport_peter_pan.docx")
            report.generate(
                metadata=metadata,
                analysis=analysis,
                chart_path=chart_path,
                image_path=img_path,
                logo_path=logo_path,
                output_path=out_path,
            )

            self.after(0, lambda: self._status.set(
                f"✅ Rapport généré : {out_path}", color=SUCCESS))
            self.after(0, lambda: messagebox.showinfo(
                "Rapport Word généré",
                f"✅ Rapport sauvegardé :\n{out_path}\n\n"
                f"Paragraphes analysés : {analysis['total_paras']}\n"
                f"Mots totaux : {analysis['total_words']}\n"
                f"Moyenne : {analysis['avg_words']} mots/§"
            ))

        except ConnectionError as e:
            self.after(0, lambda: messagebox.showerror(
                "Erreur réseau", f"Impossible de télécharger le livre :\n{e}"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Erreur", f"Erreur lors de la génération :\n{e}"))

    def _process_images(self, img_path: str, logo_path: str) -> None:
        """Recadrage de l'image + création d'un logo en N&B pivoté (Pillow)."""
        from PIL import Image
        # Image #1 : recadrage et redimensionnement
        if img_path and os.path.exists(img_path):
            with Image.open(img_path) as img:
                w, h = img.size
                # Recadrage : supprime 10% en haut et en bas
                cropped = img.crop((0, int(h * 0.10), w, int(h * 0.90)))
                resized = cropped.resize((400, 500), Image.LANCZOS)
                resized.save(img_path, quality=90)

        # Image #2 : logo N&B pivoté, collé sur l'image #1
        try:
            logo_url = (
                "https://upload.wikimedia.org/wikipedia/commons/thumb/"
                "a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg"
            )
            # Crée un logo N&B simple si pas de logo réel
            logo = Image.new("L", (100, 40), color=0)
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(logo)
            draw.text((5, 10), "YNOV", fill=255)
            logo_rotated = logo.rotate(15, expand=True)

            if img_path and os.path.exists(img_path):
                with Image.open(img_path) as base:
                    base = base.convert("RGBA")
                    logo_rgba = logo_rotated.convert("RGBA")
                    base.paste(logo_rgba, (10, 10), logo_rgba)
                    base.convert("RGB").save(img_path, quality=90)
        except Exception:
            pass  # Logo optionnel

    # ── Helpers UI ───────────────────────────────
    def _refresh_table(self) -> None:
        rows = self._db.fetch_all()
        self._table_frame.load(rows)
        self._status.set_count(len(rows))

    def _refresh_stats(self) -> None:
        avg   = self._db.average_rating()
        count = self._db.count()
        top   = self._db.top_rated(1)
        top_name = top[0]["name"] if top else "—"
        self._stats_frame.update_stats(avg, count, top_name)

    def _get_chart_data(self, chart_type: str):
        mapping = {
            "ratings":   lambda: self._db.top_rated(10),
            "status":    lambda: self._db.count_by_status(),
            "languages": lambda: self._db.count_by_language(),
            "genres":    lambda: self._db.genres_distribution(),
        }
        fn = mapping.get(chart_type)
        return fn() if fn else None

    def _show_chart_window(self, path: str, title: str) -> None:
        """Ouvre le graphique dans une fenêtre Toplevel."""
        try:
            from PIL import Image, ImageTk
            win = tk.Toplevel(self)
            win.title(f"📊  Graphique – {title}")
            win.configure(bg=BG_DARK)
            img = Image.open(path)
            img.thumbnail((900, 600))
            photo = ImageTk.PhotoImage(img)
            label = tk.Label(win, image=photo, bg=BG_DARK)
            label.image = photo  # Garde une référence
            label.pack(padx=10, pady=10)
            RoundedButton(win, "💾 Enregistrer sous…",
                          command=lambda: self._save_image(path)).pack(pady=(0, 10))
        except ImportError:
            messagebox.showinfo("Graphique", f"Graphique sauvegardé :\n{path}")

    def _save_image(self, src: str) -> None:
        dest = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("Tous", "*.*")],
            initialfile=os.path.basename(src)
        )
        if dest:
            import shutil
            shutil.copy(src, dest)
            self._status.set(f"✅ Image sauvegardée : {dest}", color=SUCCESS)

    def _ask_main_thread(self, title: str, msg: str) -> bool:
        """Pose une question depuis un thread secondaire (thread-safe)."""
        result = [False]
        event  = threading.Event()

        def _ask():
            result[0] = messagebox.askyesno(title, msg)
            event.set()

        self.after(0, _ask)
        event.wait()
        return result[0]

    def _run_in_thread(self, task, status_msg: str) -> None:
        """Lance une tâche lourde dans un thread secondaire."""
        self._status.set(status_msg, color=WARNING)

        def _wrapper():
            try:
                task()
            except ConnectionError as e:
                self.after(0, lambda: messagebox.showerror(
                    "Erreur réseau", f"Vérifiez votre connexion :\n{e}"))
                self.after(0, lambda: self._status.set(
                    "❌ Erreur réseau.", color=ACCENT2))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror(
                    "Erreur inattendue", str(e)))
                self.after(0, lambda: self._status.set(
                    f"❌ Erreur : {e}", color=ACCENT2))

        t = threading.Thread(target=_wrapper, daemon=True)
        t.start()

    def on_closing(self) -> None:
        self._db.close()
        self.destroy()


# ══════════════════════════════════════════════════════════════════
# Point d'entrée
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = TVShowApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
