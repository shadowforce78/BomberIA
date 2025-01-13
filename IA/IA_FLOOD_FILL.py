##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random


class IA_Bomber:
    def __init__(
        self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int
    ) -> None:
        """génère l'objet de la classe IA_Bomber"""
        self.num_joueur = num_joueur
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme

        # Analyse initiale du dictionnaire
        self.analyze_game_dict(game_dic)

    def analyze_game_dict(self, game_dict: dict) -> None:
        """Analyse le contenu du dictionnaire du jeu"""
        print(f"---" * 20)
        print("\nContenu du dictionnaire game_dict:")
        for key, value in game_dict.items():
            print(f"\nClé: {key}")

            # Afficher un exemple de la valeur selon son type
            if isinstance(value, list):
                print(f"Type: Liste de longueur {len(value)}")
                if value:
                    for item in value:
                        print(f"Valeur: {item}")
            else:
                print(f"Valeur: {value}")
        print(f"---" * 20)

    def flood_fill(self, game_dict: dict) -> list[tuple[tuple[int, int], int]]:
        """Calcule la distance aux 10 minerais les plus proches en utilisant flood fill"""
        carte = game_dict["map"]
        height = len(carte)
        width = len(carte[0])

        # Position du bomber
        bomber_pos = None
        for bomber in game_dict["bombers"]:
            if bomber["num_joueur"] == self.num_joueur:
                bomber_pos = bomber["position"]
                break

        if not bomber_pos:
            return []

        # Initialisation de la matrice des distances
        distances = [[-1 for _ in range(width)] for _ in range(height)]
        distances[bomber_pos[1]][bomber_pos[0]] = 0

        # File pour le BFS
        queue = [(bomber_pos[0], bomber_pos[1])]
        minerais = []

        # Directions possibles
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        while queue:
            x, y = queue.pop(0)

            # Si c'est un minerai, on l'ajoute à la liste
            if carte[y][x] == "M":
                minerais.append(((x, y), distances[y][x]))
                if len(minerais) >= 10:  # On s'arrête après avoir trouvé 10 minerais
                    break

            # Pour chaque direction possible
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy

                # Vérification des limites et obstacles
                if (
                    0 <= new_x < width
                    and 0 <= new_y < height
                    and distances[new_y][new_x] == -1
                    and carte[new_y][new_x] != "C"
                ):  # On ne peut pas traverser les colonnes

                    distances[new_y][new_x] = distances[y][x] + 1
                    queue.append((new_x, new_y))

        # Trie les minerais par distance
        minerais.sort(key=lambda x: x[1])
        return minerais[:10]

    def action(self, game_dict: dict) -> str:
        """Décide de l'action à faire"""
        minerais_proches = self.flood_fill(game_dict)
        print(f"Minerais les plus proches: {minerais_proches}")
        
        #  H/B/G/D
        t = game_dict["compteur_tour"]
        # 15 fois droit, pose une bombe, 15 fois gauche
        suite = ["D"] * 15 + ["X"] + ["G"] * 15
        if t < len(suite):
            return suite[t]


# Les clés attendues dans game_dict sont:
# - 'map': la carte du jeu (liste de strings)
# - 'bombers': liste des informations des bombers
# - 'fantômes': liste des fantômes
# - 'bombes': liste des bombes
# - 'compteur_tour': numéro du tour actuel
# - 'scores': liste des scores des joueurs
