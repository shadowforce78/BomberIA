import tkinter as tk
from tkinter import ttk
import os
from BB_modele import Game, charger_scenario
import importlib
import sys

# Configuration du thème
COLORS = {
    "primary": "#2c3e50",
    "secondary": "#34495e",
    "accent": "#3498db",
    "success": "#2ecc71",
    "warning": "#f1c40f",
    "danger": "#e74c3c",
    "light": "#ecf0f1",
    "dark": "#2c3e50",
    "text": "#2c3e50",
    "text_light": "#ffffff",
}


class ModernButton(tk.Button):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            bg=COLORS["accent"],
            fg=COLORS["text_light"],
            font=("Helvetica", 10),
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
        )
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self["background"] = "#2980b9"

    def on_leave(self, e):
        self["background"] = COLORS["accent"]


class SelectionWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BomberBUT - Configuration")
        self.root.geometry("500x700")
        self.root.configure(bg=COLORS["light"])

        # Style configuration
        style = ttk.Style()
        style.configure(
            "Modern.TCombobox",
            fieldbackground=COLORS["light"],
            background=COLORS["accent"],
        )
        style.configure(
            "Modern.TRadiobutton", background=COLORS["light"], foreground=COLORS["text"]
        )

        # Variables
        self.mode_var = tk.StringVar(value="solo")
        self.ia_selections = []
        self.selected_map = tk.StringVar()

        self.available_ias = self._get_available_ias()
        self.create_modern_widgets()

    def _get_available_ias(self):
        # Récupère la liste des fichiers IA dans le dossier IA
        ia_files = []
        ia_dir = "IA"
        for file in os.listdir(ia_dir):
            if file.endswith(".py") and not file.startswith("__"):
                ia_files.append(file[:-3])  # Enlever le .py
        return ia_files

    def create_modern_widgets(self):
        # Titre principal
        title_frame = tk.Frame(self.root, bg=COLORS["light"])
        title_frame.pack(pady=20)
        tk.Label(
            title_frame,
            text="Configuration de la partie",
            font=("Helvetica", 18, "bold"),
            bg=COLORS["light"],
            fg=COLORS["text"],
        ).pack()

        # Container principal
        main_container = tk.Frame(self.root, bg=COLORS["light"])
        main_container.pack(padx=40, pady=20, fill="both", expand=True)

        # Mode de jeu
        game_mode_frame = tk.LabelFrame(
            main_container,
            text="Mode de jeu",
            font=("Helvetica", 12),
            bg=COLORS["light"],
            fg=COLORS["text"],
        )
        game_mode_frame.pack(fill="x", pady=10)

        ttk.Radiobutton(
            game_mode_frame,
            text="Solo",
            variable=self.mode_var,
            value="solo",
            command=self.update_ia_selectors,
            style="Modern.TRadiobutton",
        ).pack(padx=20, pady=5)
        ttk.Radiobutton(
            game_mode_frame,
            text="4 Joueurs",
            variable=self.mode_var,
            value="quatre",
            command=self.update_ia_selectors,
            style="Modern.TRadiobutton",
        ).pack(padx=20, pady=5)

        # Frame pour les sélecteurs d'IA
        self.ia_frame = tk.LabelFrame(
            main_container,
            text="Sélection des IAs",
            font=("Helvetica", 12),
            bg=COLORS["light"],
            fg=COLORS["text"],
        )
        self.ia_frame.pack(fill="x", pady=10)

        # Sélection de la carte
        map_frame = tk.LabelFrame(
            main_container,
            text="Sélection de la carte",
            font=("Helvetica", 12),
            bg=COLORS["light"],
            fg=COLORS["text"],
        )
        map_frame.pack(fill="x", pady=10)

        maps = [f for f in os.listdir("maps") if f.endswith(".txt")]
        map_combo = ttk.Combobox(
            map_frame,
            textvariable=self.selected_map,
            values=maps,
            style="Modern.TCombobox",
        )
        map_combo.pack(padx=20, pady=10, fill="x")

        # Bouton de démarrage
        self.start_button = ModernButton(
            main_container, text="Démarrer la partie", command=self.start_game
        )
        self.start_button.pack(pady=20)

        self.update_ia_selectors()

    def update_ia_selectors(self):
        for widget in self.ia_frame.winfo_children():
            widget.destroy()
        self.ia_selections.clear()

        num_players = 1 if self.mode_var.get() == "solo" else 4
        for i in range(num_players):
            player_frame = tk.Frame(self.ia_frame, bg=COLORS["light"])
            player_frame.pack(fill="x", padx=20, pady=5)

            tk.Label(
                player_frame,
                text=f"Joueur {i+1}",
                font=("Helvetica", 10),
                bg=COLORS["light"],
                fg=COLORS["text"],
            ).pack(side="left")

            ia_var = tk.StringVar(value=self.available_ias[0])
            self.ia_selections.append(ia_var)
            combo = ttk.Combobox(
                player_frame,
                textvariable=ia_var,
                values=self.available_ias,
                style="Modern.TCombobox",
            )
            combo.pack(side="right", fill="x", expand=True, padx=10)

    def start_game(self):
        selected_ias = [var.get() for var in self.ia_selections]
        map_name = self.selected_map.get()
        self.root.destroy()
        root = tk.Tk()
        app = JeuBomberTK(root, f"maps/{map_name}", selected_ias)
        root.mainloop()


class JeuBomberTK:
    def __init__(self, master, scenario, selected_ias):
        self.master = master
        self.master.title("BomberBUT")
        self.master.configure(bg=COLORS["light"])

        # Récupérer la taille de l'écran
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight() 

        # Initialisation du jeu avant la création du canvas
        self.game = charger_scenario(scenario)
        self.selected_ias = selected_ias
        self.ias = self._charger_IAs()

        # Calcul de la taille optimale du canvas en fonction de la map et de l'écran
        game_width = len(self.game.carte[0])
        game_height = len(self.game.carte)

        # Taille maximale des cases en fonction de l'écran (80% de la plus petite dimension)
        max_cell_width = int((screen_width * 0.8) / game_width)
        max_cell_height = int((screen_height * 0.8) / game_height)
        self.taille_case = min(max_cell_width, max_cell_height, 50)  # Maximum 50 pixels

        # Dimensions finales du canvas
        canvas_width = game_width * self.taille_case
        canvas_height = game_height * self.taille_case

        # Frame principale avec padding
        self.main_frame = tk.Frame(master, bg=COLORS["light"])
        self.main_frame.pack(padx=20, pady=20)

        # Canvas avec bordure moderne et taille adaptée
        self.canvas = tk.Canvas(
            self.main_frame,
            width=canvas_width,
            height=canvas_height,
            bg=COLORS["light"],
            highlightthickness=1,
            highlightbackground=COLORS["accent"],
        )
        self.canvas.pack()

        # Frame pour les informations
        self.info_frame = tk.Frame(self.main_frame, bg=COLORS["light"])
        self.info_frame.pack(fill="x", pady=5)

        # Labels pour les scores
        self.score_labels = []
        for i in range(4):  # Maximum 4 joueurs
            label = tk.Label(self.info_frame, text="", font=("Arial", 12))
            label.grid(row=0, column=i, padx=10)
            self.score_labels.append(label)

        # Frame pour les contrôles avec style moderne
        self.control_frame = tk.Frame(self.main_frame, bg=COLORS["light"])
        self.control_frame.pack(pady=20)

        # Boutons modernes
        self.btn_tour = ModernButton(
            self.control_frame, text="▶ Tour suivant", command=self.jouer_tour
        )
        self.btn_tour.grid(row=0, column=0, padx=10)

        self.btn_auto = ModernButton(
            self.control_frame, text="⟳ Défilement Auto", command=self.toggle_auto_play
        )
        self.btn_auto.grid(row=0, column=1, padx=10)

        # Slider moderne pour la vitesse
        self.speed_frame = tk.Frame(self.control_frame, bg=COLORS["light"])
        self.speed_frame.grid(row=0, column=2, padx=20)

        tk.Label(
            self.speed_frame,
            text="Vitesse",
            font=("Helvetica", 10),
            bg=COLORS["light"],
            fg=COLORS["text"],
        ).pack()

        self.speed_scale = tk.Scale(
            self.speed_frame,
            from_=200,
            to=2000,
            orient="horizontal",
            length=150,
            bg=COLORS["light"],
            highlightthickness=0,
            command=self.update_speed,
        )
        self.speed_scale.set(1000)
        self.speed_scale.pack()

        # Frame pour les scores avec style moderne
        self.score_frame = tk.Frame(self.main_frame, bg=COLORS["light"])
        self.score_frame.pack(fill="x", pady=10)

        self.score_labels = []
        score_colors = [
            COLORS["accent"],
            COLORS["success"],
            COLORS["warning"],
            COLORS["danger"],
        ]

        for i in range(len(selected_ias)):
            label = tk.Label(
                self.score_frame,
                text=f"Joueur {i+1}: 0 pts",
                font=("Helvetica", 12),
                fg=score_colors[i % len(score_colors)],
                bg=COLORS["light"],
            )
            label.grid(row=0, column=i, padx=20)
            self.score_labels.append(label)

        # Centrer la fenêtre
        window_width = canvas_width + 40  # +40 pour le padding
        window_height = canvas_height + 200  # +200 pour les contrôles et scores
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Initialisation du jeu
        self.game = charger_scenario(scenario)
        self.selected_ias = selected_ias
        self.ias = self._charger_IAs()
        self.auto_play = False
        self.auto_play_speed = 500

        # Initialisation des variables de timing
        self.auto_play = False
        self.auto_play_speed = 1000  # Valeur par défaut en millisecondes
        self.last_auto_time = 0  # Pour tracker le dernier tour auto
        self.auto_play_after_id = None  # Pour stocker l'id du dernier after()

        # Premier affichage
        self.afficher_carte()
        self.game_over_happened = False  # Nouvelle variable pour tracker le game over

    def _charger_IAs(self):
        list_ia = []
        for i, ia_name in enumerate(self.selected_ias):
            imp = importlib.import_module("IA." + ia_name)
            list_ia.append(
                imp.IA_Bomber(
                    i,
                    self.game.to_dict(),
                    self.game.timerglobal,
                    self.game.timerfantôme,
                )
            )
        return list_ia

    def afficher_carte(self):
        self.canvas.delete("all")

        # Utiliser la taille de case calculée
        for y, ligne in enumerate(self.game.carte):
            for x, case in enumerate(ligne):
                # Coordonnées de la case
                x1, y1 = x * self.taille_case, y * self.taille_case
                x2, y2 = (x + 1) * self.taille_case, (y + 1) * self.taille_case
                center_x = x1 + self.taille_case / 2
                center_y = y1 + self.taille_case / 2

                # Couleur de fond par défaut
                couleur = "white"
                if case == "C":  # Mur
                    couleur = "grey20"
                elif case == "M":  # Mine
                    couleur = "brown4"
                elif case == "E":  # Ethernet
                    couleur = "deep sky blue"

                # Dessiner le fond de la case
                self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=couleur, outline="black"
                )

                # Dessiner les bombes
                for (
                    bombe
                ) in self.game.bombes:  # Correction ici: utiliser self.game.bombes
                    if bombe.position.x == x and bombe.position.y == y:
                        # Créer une bombe noire avec un cercle rouge au centre
                        self.canvas.create_oval(
                            x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black"
                        )
                        self.canvas.create_oval(
                            center_x - 5,
                            center_y - 5,
                            center_x + 5,
                            center_y + 5,
                            fill="red",
                            outline="red",
                        )

                # Dessiner les fantômes
                for fantome in self.game.fantômes:
                    if (
                        fantome.position.x == x and fantome.position.y == y
                    ):  # Correction ici aussi
                        # Dessiner un fantôme en forme de pacman inversé
                        self.canvas.create_arc(
                            x1 + 2,
                            y1 + 2,
                            x2 - 2,
                            y2 - 2,
                            start=30,
                            extent=300,
                            fill="lime green",
                        )

                # Dessiner les joueurs
                for i, bomber in enumerate(self.game.bombers):
                    if (
                        bomber.position.x == x
                        and bomber.position.y == y
                        and bomber.pv > 0
                    ):  # Correction ici aussi
                        # Couleurs différentes pour chaque joueur
                        player_colors = ["red", "blue", "green", "yellow"]
                        color = player_colors[i % len(player_colors)]

                        # Dessiner le joueur comme un cercle
                        self.canvas.create_oval(
                            x1 + 3, y1 + 3, x2 - 3, y2 - 3, fill=color, outline="black"
                        )
                        # Afficher les PV du joueur
                        self.canvas.create_text(
                            center_x,
                            center_y,
                            text=str(bomber.pv),
                            fill="white",
                            font=("Arial", 10, "bold"),
                        )

        # Mettre à jour les labels de score au lieu de dessiner sur le canvas
        for i, bomber in enumerate(self.game.bombers):
            score_text = f"Joueur {i+1}: {self.game.scores[i]} pts (PV: {bomber.pv})"
            self.score_labels[i].config(
                text=score_text, fg=["red", "blue", "green", "yellow"][i % 4]
            )

        # Si game over, afficher au centre
        if self.game.is_game_over():
            self.canvas.create_text(
                400, 300, text="Partie Terminée", font=("Arial", 24), fill="red"
            )

        # Mise à jour des scores de manière sécurisée
        for i in range(len(self.score_labels)):
            if i < len(self.game.bombers):
                bomber = self.game.bombers[i]
                score_text = (
                    f"Joueur {i+1}: {self.game.scores[i]} pts (PV: {bomber.pv})"
                )
                self.score_labels[i].config(text=score_text)
            else:
                self.score_labels[i].config(text=f"Joueur {i+1}: Éliminé")

    def jouer_tour(self):
        # Vérifier si le jeu n'est pas déjà terminé
        if self.game.is_game_over():
            self.finir_partie()
            return

        # Faire jouer chaque IA
        for j, ia in enumerate(self.ias):
            if j < len(self.game.bombers) and self.game.bombers[j].pv > 0:
                action = None
                try:
                    original_stdout = sys.stdout
                    sys.stdout = open(os.devnull, "w")
                    action = ia.action(self.game.to_dict())
                    sys.stdout.close()
                    sys.stdout = original_stdout

                    if action:
                        self.game.résoudre_action(j, action)
                        # Vérifier si le bomber est mort après l'action
                        if self.game.bombers[j].pv == 0:
                            self.game_over(j)
                            return
                except Exception as e:
                    print(f"Erreur pour le joueur {j}: {str(e)}")
                    continue

        # Phase non-joueur  
        try:
            self.game.phase_non_joueur()
            # Vérifier si un bomber est mort pendant la phase non-joueur
            all_dead = True
            for j, bomber in enumerate(self.game.bombers):
                if bomber.pv > 0:
                    all_dead = False
                    break
            
            if all_dead:
                self.finir_partie()
                return

        except Exception as e:
            print(f"Erreur dans la phase non-joueur: {str(e)}")

        # Mise à jour de l'affichage
        self.afficher_carte()

        # Vérifie les conditions de fin de partie uniquement en mode multijoueur
        if len(self.ias) > 1:  # Si plus d'un joueur
            alive_players = sum(1 for bomber in self.game.bombers if bomber.pv > 0)
            if alive_players == 0:  # La partie se termine uniquement quand tous les joueurs sont morts
                self.finir_partie()
                return

    def game_over(self, player_index):
        """Affiche game over quand un joueur meurt"""
        self.game_over_happened = True  # Marque que le game over a eu lieu
        self.auto_play = False
        self.btn_tour["state"] = "disabled"
        self.btn_auto["state"] = "disabled"
        
        # Affichage du message game over
        self.canvas.create_text(
            400, 300,
            text=f"Game Over - Joueur {player_index + 1} est mort!",
            font=("Arial", 24),
            fill=COLORS["danger"]
        )
        
        # Afficher le score final
        score_text = f"Score final: {self.game.scores[player_index]} points"
        self.canvas.create_text(
            400, 350,
            text=score_text,
            font=("Arial", 18),
            fill=COLORS["text"]
        )
        
        self.afficher_carte()

    def toggle_auto_play(self):
        """Active ou désactive le défilement automatique"""
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.btn_auto.config(text="Arrêter Auto")
            # Démarrer le défilement automatique
            self.last_auto_time = self.master.after_idle(self.jouer_tour_auto)
        else:
            self.btn_auto.config(text="Défilement Auto")
            # Annuler le prochain tour auto s'il existe
            if self.auto_play_after_id:
                self.master.after_cancel(self.auto_play_after_id)
                self.auto_play_after_id = None

    def jouer_tour_auto(self):
        """Joue un tour automatiquement avec une vitesse constante"""
        if self.auto_play and not self.game.is_game_over():
            self.jouer_tour()
            # Planifier le prochain tour avec un délai constant
            self.auto_play_after_id = self.master.after(
                self.auto_play_speed, 
                self.jouer_tour_auto
            )

    def finir_partie(self):
        """Gestion de la fin de partie"""
        self.auto_play = False
        self.btn_tour["state"] = "disabled"
        self.btn_auto["state"] = "disabled"

        # Trouver le gagnant
        max_score = -1
        winner = -1
        for i, score in enumerate(self.game.scores):
            if score > max_score:
                max_score = score
                winner = i

        if winner >= 0:
            self.canvas.create_text(
                400,
                300,
                text=f"Partie Terminée - Joueur {winner + 1} gagne avec {max_score} points!",
                font=("Arial", 24, "bold"),
                fill="red",
            )
        else:
            self.canvas.create_text(
                400,
                300,
                text="Partie Terminée - Égalité!",
                font=("Arial", 24, "bold"),
                fill="red",
            )

    def update_speed(self, value):
        """Met à jour la vitesse de défilement automatique"""
        self.auto_play_speed = int(value)
        # Redémarrer le défilement si actif pour appliquer la nouvelle vitesse
        if self.auto_play:
            if self.auto_play_after_id:
                self.master.after_cancel(self.auto_play_after_id)
            self.auto_play_after_id = self.master.after(
                self.auto_play_speed,
                self.jouer_tour_auto
            )


if __name__ == "__main__":
    selection = SelectionWindow()
    selection.root.mainloop()
