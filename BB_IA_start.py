import BB_modele
from typing import Literal
import importlib
import os
import sys
import tkinter as tk
from tkinter import Canvas


def charger_IAs(noms_des_joueurs: list[str], game: BB_modele.Game):
    """Charge les objets IA contenus dans les fichiers (noms des joueurs) donnés

    Args:
        player_names ([str]): noms des joueurs
    Returns:
        list : liste des objet IAs par chaque indice de joueur
    """

    list_ia = []

    for i in range(len(noms_des_joueurs)):
        imp = importlib.import_module("IA." + noms_des_joueurs[i])
        list_ia.append(
            imp.IA_Bomber(i, game.to_dict(), game.timerglobal, game.timerfantôme)
        )

    return list_ia


class GameView:
    def __init__(self, game):
        self.root = tk.Tk()
        self.root.title("BomberIA Viewer")

        # Frame principale
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill="both")

        # Délai fixe entre les frames (200ms = 5 FPS)
        self.frame_delay = 200

        # Calcul de la taille de la fenêtre en fonction de la carte
        game_dict = game.to_dict()
        terrain = game_dict["map"]
        self.rows = len(terrain)
        self.cols = len(terrain[0])

        # Taille maximale de la fenêtre (80% de la taille de l'écran)
        screen_width = self.root.winfo_screenwidth() * 0.8
        screen_height = self.root.winfo_screenheight() * 0.8

        # Calcul de la taille des cellules
        self.cell_size = min(screen_width // self.cols, screen_height // self.rows)

        # Taille finale du canvas
        canvas_width = self.cell_size * self.cols
        canvas_height = self.cell_size * self.rows

        self.canvas = Canvas(main_frame, width=canvas_width, height=canvas_height)
        self.canvas.pack()

        # Couleurs du jeu améliorées
        self.colors = {
            "wall": "#404040",  # Murs (gris foncé)
            "minerai": "#8B4513",  # Minerai (marron foncé)
            "bomber": "#1E90FF",  # Bomber (bleu vif)
            "bomber_outline": "#104E8B",  # Contour bomber (bleu foncé)
            "ghost": "#FF4500",  # Fantôme (rouge-orange)
            "ghost_outline": "#8B2500",  # Contour fantôme (rouge foncé)
            "update": "#32CD32",  # Update (vert lime)
            "ethernet": "#9370DB",  # Ethernet (violet)
            "background": "#E8E8E8",  # Fond (gris très clair)
            "grid": "#D3D3D3",  # Grille (gris clair)
            'bomb': '#000000',          # Bombe (noir)
            'bomb_outline': '#FF0000',  # Contour bombe (rouge)
            'explosion': '#FFD700',     # Explosion (jaune doré)
            'explosion_center': '#FF4500'  # Centre explosion (orange-rouge)
        }

        self.game = game
        self.draw_game()

    def draw_game(self):
        self.canvas.delete("all")
        game_dict = self.game.to_dict()
        terrain = game_dict["map"]

        # Dessiner le terrain avec grille
        for i in range(len(terrain)):
            for j in range(len(terrain[0])):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size

                # Fond avec grille
                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.colors["background"],
                    outline=self.colors["grid"],
                    width=1,
                )

                # Éléments du terrain
                if terrain[i][j] == "C":  # Changé de '#' à 'C' pour les murs
                    # Mur avec effet 3D
                    self.canvas.create_rectangle(
                        x1 + 2,
                        y1 + 2,
                        x2 - 2,
                        y2 - 2,
                        fill=self.colors["wall"],
                        outline="#303030",
                        width=2,
                    )
                elif terrain[i][j] == "M":
                    # Minerai avec texture
                    self.canvas.create_rectangle(
                        x1 + 4,
                        y1 + 4,
                        x2 - 4,
                        y2 - 4,
                        fill=self.colors["minerai"],
                        outline="#654321",
                        width=2,
                    )
                elif terrain[i][j] == "U":
                    # Update avec effet brillant
                    self.canvas.create_oval(
                        x1 + 4,
                        y1 + 4,
                        x2 - 4,
                        y2 - 4,
                        fill=self.colors["update"],
                        outline="#228B22",
                        width=2,
                    )
                elif terrain[i][j] == "E":
                    # Ethernet avec symbole
                    self.canvas.create_rectangle(
                        x1 + 4,
                        y1 + 4,
                        x2 - 4,
                        y2 - 4,
                        fill=self.colors["ethernet"],
                        outline="#483D8B",
                        width=2,
                    )
                    # Ajout d'un symbole "E"
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="E",
                        fill="white",
                        font=("Arial", int(self.cell_size / 2)),
                    )

        # Dessiner les explosions (avant les bombes pour qu'elles apparaissent en dessous)
        for bombe in game_dict['bombes']:
            if bombe['timer'] <= 1:  # La bombe est en train d'exploser
                x = bombe['position'][1] * self.cell_size + self.cell_size/2
                y = bombe['position'][0] * self.cell_size + self.cell_size/2
                
                # Centre de l'explosion
                radius = self.cell_size * 0.4
                self.canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    fill=self.colors['explosion_center'],
                    outline='',
                )
                
                # Rayons d'explosion
                portée = bombe['portée']
                directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # Haut, Bas, Gauche, Droite
                
                for dx, dy in directions:
                    for distance in range(1, portée + 1):
                        ex = x + (dx * self.cell_size * distance)
                        ey = y + (dy * self.cell_size * distance)
                        
                        # Dessiner le rayon d'explosion
                        self.canvas.create_rectangle(
                            ex - self.cell_size/2, ey - self.cell_size/2,
                            ex + self.cell_size/2, ey + self.cell_size/2,
                            fill=self.colors['explosion'],
                            outline='',
                            stipple='gray50'  # Effet de transparence
                        )

        # Dessiner les bombes
        for bombe in game_dict['bombes']:
            if bombe['timer'] > 1:  # Ne pas dessiner la bombe si elle explose
                x = bombe['position'][1] * self.cell_size + self.cell_size/2
                y = bombe['position'][0] * self.cell_size + self.cell_size/2
                radius = self.cell_size * 0.3
                
                # Corps de la bombe
                self.canvas.create_oval(
                    x - radius, y - radius,
                    x + radius, y + radius,
                    fill=self.colors['bomb'],
                    outline=self.colors['bomb_outline'],
                    width=2
                )
                
                # Timer de la bombe
                self.canvas.create_text(
                    x, y,
                    text=str(bombe['timer']),
                    fill='white',
                    font=('Arial bold', int(self.cell_size/3))
                )

        # Dessiner les bombers avec plus de détails
        for bomber in game_dict["bombers"]:
            # Modification ici: vérifier si le bomber existe toujours dans le jeu
            if bomber is not None and bomber.get("pv", 0) >= 0:  # Changé > 0 à >= 0
                x = bomber["position"][1] * self.cell_size + self.cell_size / 2
                y = bomber["position"][0] * self.cell_size + self.cell_size / 2
                radius = self.cell_size * 0.35

                # Corps du bomber
                self.canvas.create_oval(
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius,
                    fill=self.colors["bomber"],
                    outline=self.colors["bomber_outline"],
                    width=2,
                )

                # Numéro du joueur avec outline pour meilleure visibilité
                self.canvas.create_text(
                    x,
                    y,
                    text=str(bomber["num_joueur"]),
                    fill="white",
                    font=("Arial bold", int(self.cell_size / 3)),
                )

                # Indicateur de PV plus visible
                pv_text = "♥" * bomber["pv"]
                if bomber["pv"] > 0:  # N'afficher les PV que si le bomber est vivant
                    self.canvas.create_text(
                        x,
                        y - radius - 5,
                        text=pv_text,
                        fill="red",
                        font=("Arial", int(self.cell_size / 4)),
                    )

        # Dessiner les fantômes avec effet fantomatique
        for fantome in game_dict["fantômes"]:
            x = fantome["position"][1] * self.cell_size + self.cell_size / 2
            y = fantome["position"][0] * self.cell_size + self.cell_size / 2
            radius = self.cell_size * 0.3

            # Corps du fantôme avec ondulations
            points = [
                x,
                y - radius,  # sommet
                x + radius,
                y,  # droite
                x + radius * 0.8,
                y + radius,  # bas droite
                x,
                y + radius * 0.8,  # bas milieu
                x - radius * 0.8,
                y + radius,  # bas gauche
                x - radius,
                y,  # gauche
            ]
            # Effet de transparence avec couches superposées
            self.canvas.create_polygon(
                points,
                fill=self.colors["ghost"],
                outline=self.colors["ghost_outline"],
                width=2,
                smooth=True,
            )

        self.root.update()  # Force la mise à jour de l'interface
        if not self.game.is_game_over():
            self.root.after(self.frame_delay, self.draw_next_frame)

    def draw_next_frame(self):
        try:
            if not self.game.is_game_over():
                self.game_step()
                self.draw_game()
        except tk.TclError:
            # Gestion propre de la fermeture de la fenêtre
            pass

    def game_step(self):
        """Exécute une étape de simulation"""
        # Cette méthode sera définie depuis l'extérieur
        pass


def partie(noms_des_joueurs: list[str], scenario: str):
    """
    Simule une partie du jeu BomberBUT

    Args:
        joueurs ([str]) : liste contenant les noms des joueurs i.e. les noms des fichiers contenant les IA
            (on peut mettre plusieurs fois le même nom)
        scenario : nom du fichier contenant la map de départ
    Returns:
        historique (str) : historique complet de la partie
        scores (list) : liste des scores des joueurs en fin de partie
    """

    game = BB_modele.charger_scenario(scenario)
    nb_joueurs = len(noms_des_joueurs)
    assert nb_joueurs == len(game.bombers)

    IAs = charger_IAs(noms_des_joueurs, game)
    game_view = GameView(game)

    def step_simulation():
        """Fonction qui exécute une étape de la simulation"""
        game.log("début_tour " + str(game.compteur_tour))
        # phase joueurs
        for j in range(nb_joueurs):
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")
            action = IAs[j].action(game.to_dict())
            sys.stdout = original_stdout
            game.résoudre_action(j, action)

        # phase non joueur
        game.phase_non_joueur()

    # Connecter la fonction step à la vue
    game_view.game_step = step_simulation

    # Lancer la première frame
    game_view.draw_game()

    # Démarrer la boucle principale
    game_view.root.mainloop()

    # Retourner les résultats après la fermeture de la fenêtre
    total_score = 0
    if type(game.scores) == list:
        for i in range(len(game.scores)):
            total_score += game.scores[i]
        game.log(f"total_score {total_score}")
    game.log("game_over")
    game.log(f"scores {game.scores}")


if __name__ == "__main__":
    partie(["IA_FIRST_TEST"], "maps/training3.txt")
    # partie(['IA_FIRST_TEST','IA_FIRST_TEST','IA_FIRST_TEST','IA_FIRST_TEST'], "maps/battle0.txt")
