import tkinter as tk
from tkinter import ttk
import os
from BB_modele import Game, charger_scenario
import importlib
import sys


class SelectionWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configuration de la partie")
        self.root.geometry("400x500")

        # Variables
        self.mode_var = tk.StringVar(value="solo")
        self.ia_selections = []
        self.selected_map = tk.StringVar()

        # Liste des IAs disponibles
        self.available_ias = self._get_available_ias()
        self.create_widgets()

    def _get_available_ias(self):
        # Récupère la liste des fichiers IA dans le dossier IA
        ia_files = []
        ia_dir = "IA"
        for file in os.listdir(ia_dir):
            if file.endswith(".py") and not file.startswith("__"):
                ia_files.append(file[:-3])  # Enlever le .py
        return ia_files

    def create_widgets(self):
        # Mode de jeu
        tk.Label(self.root, text="Mode de jeu:").pack(pady=5)
        tk.Radiobutton(
            self.root,
            text="Solo",
            variable=self.mode_var,
            value="solo",
            command=self.update_ia_selectors,
        ).pack()
        tk.Radiobutton(
            self.root,
            text="4 Joueurs",
            variable=self.mode_var,
            value="quatre",
            command=self.update_ia_selectors,
        ).pack()

        # Frame pour les sélecteurs d'IA
        self.ia_frame = tk.Frame(self.root)
        self.ia_frame.pack(pady=10)

        # Sélection de la carte
        tk.Label(self.root, text="Sélection de la carte:").pack(pady=5)
        maps = [f for f in os.listdir("maps") if f.endswith(".txt")]
        ttk.Combobox(self.root, textvariable=self.selected_map, values=maps).pack()

        # Bouton de démarrage
        tk.Button(self.root, text="Démarrer la partie", command=self.start_game).pack(
            pady=20
        )

        self.update_ia_selectors()

    def update_ia_selectors(self):
        # Nettoyer les anciens sélecteurs
        for widget in self.ia_frame.winfo_children():
            widget.destroy()
        self.ia_selections.clear()

        # Créer les nouveaux sélecteurs
        num_players = 1 if self.mode_var.get() == "solo" else 4
        for i in range(num_players):
            tk.Label(self.ia_frame, text=f"Joueur {i+1}:").pack()
            ia_var = tk.StringVar(value=self.available_ias[0])
            self.ia_selections.append(ia_var)
            ttk.Combobox(
                self.ia_frame, textvariable=ia_var, values=self.available_ias
            ).pack()

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
        self.master.title("BomberBUT - Interface Tkinter")

        # Frame principale
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(padx=10, pady=10)

        # Canvas
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600, bg="white")
        self.canvas.pack()

        # Frame pour les informations
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(fill='x', pady=5)
        
        # Labels pour les scores
        self.score_labels = []
        for i in range(4):  # Maximum 4 joueurs
            label = tk.Label(self.info_frame, text="", font=("Arial", 12))
            label.grid(row=0, column=i, padx=10)
            self.score_labels.append(label)

        # Boutons de contrôle
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(pady=5)

        self.btn_tour = tk.Button(
            self.control_frame, text="Jouer un Tour", command=self.jouer_tour
        )
        self.btn_tour.grid(row=0, column=0, padx=5)

        self.btn_quit = tk.Button(
            self.control_frame, text="Quitter", command=master.quit
        )
        self.btn_quit.grid(row=0, column=1, padx=5)

        # Ajout d'une variable pour tracker l'état du défilement automatique
        self.auto_play = False
        self.auto_play_speed = 500  # 500ms = 2 tours par seconde
        
        # Ajout du bouton de défilement automatique dans control_frame
        self.btn_auto = tk.Button(
            self.control_frame, 
            text="Défilement Auto", 
            command=self.toggle_auto_play
        )
        self.btn_auto.grid(row=0, column=2, padx=5)

        # Chargement du jeu
        self.game = charger_scenario(scenario)
        self.selected_ias = selected_ias
        self.ias = self._charger_IAs()

        # Démarrage de l'affichage
        self.afficher_carte()

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
        taille_case = 30
        
        # Dessiner la grille de base
        for y, ligne in enumerate(self.game.carte):
            for x, case in enumerate(ligne):
                # Coordonnées de la case
                x1, y1 = x * taille_case, y * taille_case
                x2, y2 = (x + 1) * taille_case, (y + 1) * taille_case
                center_x = x1 + taille_case/2
                center_y = y1 + taille_case/2
                
                # Couleur de fond par défaut
                couleur = "white"
                if case == "C":  # Mur
                    couleur = "grey20"
                elif case == "M":  # Mine
                    couleur = "brown4"
                elif case == "E":  # Ethernet
                    couleur = "deep sky blue"
                
                # Dessiner le fond de la case
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=couleur, outline="black")
                
                # Dessiner les bombes
                for bombe in self.game.bombes:  # Correction ici: utiliser self.game.bombes
                    if bombe.position.x == x and bombe.position.y == y:
                        # Créer une bombe noire avec un cercle rouge au centre
                        self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="black")
                        self.canvas.create_oval(
                            center_x-5, center_y-5,
                            center_x+5, center_y+5,
                            fill="red", outline="red"
                        )
                
                # Dessiner les fantômes
                for fantome in self.game.fantômes:
                    if fantome.position.x == x and fantome.position.y == y:  # Correction ici aussi
                        # Dessiner un fantôme en forme de pacman inversé
                        self.canvas.create_arc(
                            x1+2, y1+2, x2-2, y2-2,
                            start=30, extent=300,
                            fill="lime green"
                        )
                
                # Dessiner les joueurs
                for i, bomber in enumerate(self.game.bombers):
                    if bomber.position.x == x and bomber.position.y == y and bomber.pv > 0:  # Correction ici aussi
                        # Couleurs différentes pour chaque joueur
                        player_colors = ["red", "blue", "green", "yellow"]
                        color = player_colors[i % len(player_colors)]
                        
                        # Dessiner le joueur comme un cercle
                        self.canvas.create_oval(
                            x1+3, y1+3, x2-3, y2-3,
                            fill=color, outline="black"
                        )
                        # Afficher les PV du joueur
                        self.canvas.create_text(
                            center_x, center_y,
                            text=str(bomber.pv),
                            fill="white", font=("Arial", 10, "bold")
                        )

        # Mettre à jour les labels de score au lieu de dessiner sur le canvas
        for i, bomber in enumerate(self.game.bombers):
            score_text = f"Joueur {i+1}: {self.game.scores[i]} pts (PV: {bomber.pv})"
            self.score_labels[i].config(
                text=score_text,
                fg=["red", "blue", "green", "yellow"][i % 4]
            )

        # Si game over, afficher au centre
        if self.game.is_game_over():
            self.canvas.create_text(
                400, 300,
                text="Partie Terminée",
                font=("Arial", 24),
                fill="red"
            )

    def jouer_tour(self):
        # Faire jouer chaque IA
        for j, ia in enumerate(self.ias):
            # Vérifier si le joueur est en vie avant de jouer
            if self.game.bombers[j].pv <= 0:
                self.game_over(j)
                return
                
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
            action = ia.action(self.game.to_dict())
            sys.stdout.close()
            sys.stdout = original_stdout
            self.game.résoudre_action(j, action)

            # Vérifier si le joueur est mort après son action
            if self.game.bombers[j].pv <= 0:
                self.game_over(j)
                return

        # Phase non-joueur
        self.game.phase_non_joueur()
        self.afficher_carte()

        if self.game.is_game_over():
            self.btn_tour["state"] = "disabled"
            self.canvas.create_text(
                400, 300, text="Partie Terminée", font=("Arial", 24), fill="red"
            )

    def game_over(self, player_index):
        """Affiche game over quand un joueur meurt"""
        self.auto_play = False
        self.btn_tour["state"] = "disabled"
        self.btn_auto["state"] = "disabled"
        self.canvas.create_text(
            400, 300,
            text=f"Game Over - Joueur {player_index + 1} est mort!",
            font=("Arial", 24),
            fill="red"
        )
        self.afficher_carte()

    def toggle_auto_play(self):
        """Active ou désactive le défilement automatique"""
        self.auto_play = not self.auto_play
        if self.auto_play:
            self.btn_auto.config(text="Arrêter Auto")
            self.jouer_tour_auto()
        else:
            self.btn_auto.config(text="Défilement Auto")

    def jouer_tour_auto(self):
        """Joue un tour automatiquement si auto_play est activé"""
        if self.auto_play and not self.game.is_game_over():
            self.jouer_tour()
            self.master.after(self.auto_play_speed, self.jouer_tour_auto)


if __name__ == "__main__":
    selection = SelectionWindow()
    selection.root.mainloop()