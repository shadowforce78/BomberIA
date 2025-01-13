##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
import logging

# Configuration du logger
logging.basicConfig(filename='ia_bomber.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.debug(f"---" * 20)
        logging.debug("\nContenu du dictionnaire game_dict:")
        for key, value in game_dict.items():
            logging.debug(f"\nClé: {key}")

            # Afficher un exemple de la valeur selon son type
            if isinstance(value, list):
                logging.debug(f"Type: Liste de longueur {len(value)}")
                if value:
                    for item in value:
                        logging.debug(f"Valeur: {item}")
            else:
                logging.debug(f"Valeur: {value}")
        logging.debug(f"---" * 20)

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

    def get_direction_to_target(self, current_pos: tuple[int, int], target_pos: tuple[int, int]) -> str:
        """Détermine la direction à prendre pour aller vers la cible"""
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        if abs(dx) > abs(dy):
            return "D" if dx > 0 else "G"
        else:
            return "B" if dy > 0 else "H"

    def is_safe_position(self, pos: tuple[int, int], bombes: list[dict]) -> bool:
        """Vérifie si une position est sûre par rapport aux bombes"""
        for bombe in bombes:
            bombe_pos = bombe["position"]
            portee = bombe["portée"]
            
            # Si même ligne ou même colonne que la bombe
            if pos[0] == bombe_pos[0] or pos[1] == bombe_pos[1]:
                distance = abs(pos[0] - bombe_pos[0]) + abs(pos[1] - bombe_pos[1])
                if distance <= portee:
                    return False
        return True

    def get_safe_distance(self, bomb_pos: tuple[int, int], current_pos: tuple[int, int], portee: int = 2) -> bool:
        """Vérifie si la position actuelle est à une distance sûre de la bombe"""
        if current_pos[0] == bomb_pos[0] or current_pos[1] == bomb_pos[1]:
            distance = abs(current_pos[0] - bomb_pos[0]) + abs(current_pos[1] - bomb_pos[1])
            return distance > portee + 1
        return True

    def count_adjacent_minerals(self, pos: tuple[int, int], game_dict: dict) -> int:
        """Compte le nombre de minerais adjacents à une position"""
        count = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = pos[0] + dx, pos[1] + dy
            if 0 <= y < len(game_dict["map"]) and 0 <= x < len(game_dict["map"][0]):
                if game_dict["map"][y][x] == "M":
                    count += 1
        return count

    def should_place_bomb(self, pos: tuple[int, int], minerai: tuple[int, int]) -> bool:
        """Détermine s'il faut poser une bombe basé sur la position du minerai"""
        if pos[0] == minerai[0]:  # Même colonne
            return abs(pos[1] - minerai[1]) <= 2
        if pos[1] == minerai[1]:  # Même ligne
            return abs(pos[0] - minerai[0]) <= 2
        return False

    def get_best_minerai(self, minerais_proches: list, game_dict: dict) -> tuple[tuple[int, int], int]:
        """Choisit le meilleur minerai à cibler en fonction du nombre de minerais adjacents"""
        best_score = -1
        best_minerai = None
        
        for minerai, distance in minerais_proches:
            score = 0
            # Compte les minerais adjacents
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                x, y = minerai[0] + dx, minerai[1] + dy
                if 0 <= y < len(game_dict["map"]) and 0 <= x < len(game_dict["map"][0]):
                    if game_dict["map"][y][x] == "M":
                        score += 1
            
            # Pénalise la distance
            score = score - (distance * 0.1)
            
            if score > best_score:
                best_score = score
                best_minerai = minerai
                
        return best_minerai, best_score

    def action(self, game_dict: dict) -> str:
        """Décide de l'action à faire"""
        minerais_proches = self.flood_fill(game_dict)
        logging.debug(f"Minerais les plus proches: {minerais_proches}")
        
        # Récupérer la position actuelle du bomber
        bomber_pos = None
        for bomber in game_dict["bombers"]:
            if bomber["num_joueur"] == self.num_joueur:
                bomber_pos = bomber["position"]
                break
                
        if not bomber_pos or not minerais_proches:
            return "N"
            
        # État du bomber
        self.derniere_action = getattr(self, 'derniere_action', None)
        self.compte_recul = getattr(self, 'compte_recul', 0)
        self.direction_recul = getattr(self, 'direction_recul', None)
        self.derniere_bombe = getattr(self, 'derniere_bombe', None)
        
        # Réinitialisation des états après explosion de bombe
        if self.derniere_bombe:
            bombe_existe = False
            for bombe in game_dict["bombes"]:
                if bombe["position"] == self.derniere_bombe:
                    bombe_existe = True
                    break
            if not bombe_existe:  # La bombe a explosé
                self.derniere_bombe = None
                self.compte_recul = 0
                self.direction_recul = None
        
        # Si on est en train de reculer après avoir posé une bombe
        if self.compte_recul > 0:
            self.compte_recul -= 1
            return self.direction_recul
            
        # Vérifier les bombes actives
        if self.derniere_bombe and not self.get_safe_distance(self.derniere_bombe, bomber_pos):
            return self.direction_recul

        # Position du minerai le plus proche
        minerai_proche = minerais_proches[0][0]
        
        # Compter le nombre de minerais qu'on peut toucher avec une bombe
        nb_minerais_adjacents = self.count_adjacent_minerals(bomber_pos, game_dict)
        
        # Si on peut toucher plusieurs minerais d'un coup, on pose la bombe
        if nb_minerais_adjacents > 1:
            self.derniere_bombe = bomber_pos
            self.compte_recul = 5
            return "X"
        
        # Si on est adjacent au minerai
        if abs(bomber_pos[0] - minerai_proche[0]) <= 1 and abs(bomber_pos[1] - minerai_proche[1]) <= 1:
            # Déterminer la direction de recul la plus sûre (opposée au minerai)
            if bomber_pos[0] < minerai_proche[0]:
                self.direction_recul = "G"
            elif bomber_pos[0] > minerai_proche[0]:
                self.direction_recul = "D"
            elif bomber_pos[1] < minerai_proche[1]:
                self.direction_recul = "H"
            else:
                self.direction_recul = "B"
                
            # Poser la bombe et commencer le recul
            self.derniere_bombe = bomber_pos
            self.compte_recul = 3  # Augmenté à 5 pour plus de sécurité
            return "X"
            
        # Se déplacer vers le minerai seulement si on est en sécurité
        if not self.derniere_bombe or self.get_safe_distance(self.derniere_bombe, bomber_pos):
            direction = self.get_direction_to_target(bomber_pos, minerai_proche)
            self.derniere_action = direction
            return direction
            
        # Sinon continuer à reculer
        return self.direction_recul


# Les clés attendues dans game_dict sont:
# - 'map': la carte du jeu (liste de strings)
# - 'bombers': liste des informations des bombers
# - 'fantômes': liste des fantômes
# - 'bombes': liste des bombes
# - 'compteur_tour': numéro du tour actuel
# - 'scores': liste des scores des joueurs
