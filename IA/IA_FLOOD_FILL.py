##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
import logging

# Configuration du logger
logging.basicConfig(
    filename='ia_bomber.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
        logging.debug("------------------------------------------------------------")
        logging.debug("Analyzing game dictionary:")
        for key, value in game_dict.items():
            if isinstance(value, list):
                logging.debug(f"{key}: list[{len(value)}]")
                if value and key in ['map', 'scores']:  # Only log specific important lists
                    for item in value:
                        logging.debug(str(item))
            else:
                logging.debug(f"{key}: {value}")
        logging.debug("------------------------------------------------------------")

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

    def can_move_to(self, pos: tuple[int, int], direction: str, game_dict: dict) -> bool:
        """Vérifie si le déplacement dans la direction donnée est possible"""
        map_height = len(game_dict["map"])
        map_width = len(game_dict["map"][0])
        x, y = pos
        
        if direction == "H" and y > 0:
            return game_dict["map"][y-1][x] != "C"
        elif direction == "B" and y < map_height - 1:
            return game_dict["map"][y+1][x] != "C"
        elif direction == "G" and x > 0:
            return game_dict["map"][y][x-1] != "C"
        elif direction == "D" and x < map_width - 1:
            return game_dict["map"][y][x+1] != "C"
        return False

    def get_direction_to_target(self, current_pos: tuple[int, int], target_pos: tuple[int, int], game_dict: dict) -> str:
        """Détermine la direction à prendre pour aller vers la cible en évitant les obstacles"""
        # Utiliser flood_fill pour trouver le meilleur chemin
        carte = game_dict["map"]
        height = len(carte)
        width = len(carte[0])
        
        # Initialisation de la matrice des distances et des parents
        distances = [[-1 for _ in range(width)] for _ in range(height)]
        parents = [[None for _ in range(width)] for _ in range(height)]
        distances[current_pos[1]][current_pos[0]] = 0
        
        # File pour le BFS
        queue = [(current_pos[0], current_pos[1])]
        target_found = False
        
        # Directions possibles
        directions = {'D': (1, 0), 'G': (-1, 0), 'B': (0, 1), 'H': (0, -1)}
        
        # BFS pour trouver le plus court chemin
        while queue and not target_found:
            x, y = queue.pop(0)
            
            if (x, y) == target_pos:
                target_found = True
                break
                
            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy
                
                # Vérifier les limites et les obstacles
                if (0 <= new_x < width and 0 <= new_y < height and 
                    distances[new_y][new_x] == -1 and carte[new_y][new_x] != 'C'):
                    distances[new_y][new_x] = distances[y][x] + 1
                    parents[new_y][new_x] = (x, y, direction)
                    queue.append((new_x, new_y))
        
        # Si on a trouvé un chemin, remonter jusqu'à la première direction
        if target_found:
            x, y = target_pos
            while parents[y][x] is not None:
                parent_x, parent_y, direction = parents[y][x]
                if (parent_x, parent_y) == current_pos:
                    return direction
                x, y = parent_x, parent_y
        
        # Si aucun chemin n'est trouvé, essayer les directions directes
        dx = target_pos[0] - current_pos[0]
        dy = target_pos[1] - current_pos[1]
        
        # Essayer d'abord vertical puis horizontal
        if abs(dy) >= abs(dx):
            if dy > 0 and self.can_move_to(current_pos, "B", game_dict):
                return "B"
            elif dy < 0 and self.can_move_to(current_pos, "H", game_dict):
                return "H"
            elif dx > 0 and self.can_move_to(current_pos, "D", game_dict):
                return "D"
            elif dx < 0 and self.can_move_to(current_pos, "G", game_dict):
                return "G"
        # Essayer d'abord horizontal puis vertical
        else:
            if dx > 0 and self.can_move_to(current_pos, "D", game_dict):
                return "D"
            elif dx < 0 and self.can_move_to(current_pos, "G", game_dict):
                return "G"
            elif dy > 0 and self.can_move_to(current_pos, "B", game_dict):
                return "B"
            elif dy < 0 and self.can_move_to(current_pos, "H", game_dict):
                return "H"
        
        return "N"

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

    def get_safe_direction(self, pos: tuple[int, int], bombes: list[dict], carte: list[list[str]]) -> str:
        """Trouve une direction sûre pour s'échapper"""
        # Liste des directions possibles
        directions = {"H": (0, -1), "B": (0, 1), "G": (-1, 0), "D": (1, 0)}
        best_direction = "N"
        best_safety = -1

        for direction, (dx, dy) in directions.items():
            new_x, new_y = pos[0] + dx, pos[1] + dy
            
            # Vérifier les limites et les murs
            if not (0 <= new_x < len(carte[0]) and 0 <= new_y < len(carte)):
                continue
            if carte[new_y][new_x] == "C":
                continue
                
            # Calculer un score de sécurité
            safety = 0
            for bombe in bombes:
                bombe_pos = bombe["position"]
                # Si nouvelle position pas alignée avec la bombe
                if new_x != bombe_pos[0] and new_y != bombe_pos[1]:
                    safety += 2
                # Si plus loin de la bombe qu'avant
                elif abs(new_x - bombe_pos[0]) + abs(new_y - bombe_pos[1]) > abs(pos[0] - bombe_pos[0]) + abs(pos[1] - bombe_pos[1]):
                    safety += 1
            
            if safety > best_safety:
                best_safety = safety
                best_direction = direction
                
        return best_direction

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

        # Si en danger à cause d'une bombe
        if game_dict["bombes"]:
            for bombe in game_dict["bombes"]:
                if not self.get_safe_distance(bombe["position"], bomber_pos):
                    safe_dir = self.get_safe_direction(bomber_pos, game_dict["bombes"], game_dict["map"])
                    if safe_dir != "N":
                        return safe_dir

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
            
        # Éviter les mouvements répétitifs
        if hasattr(self, 'derniere_position') and hasattr(self, 'position_counter'):
            if self.derniere_position == bomber_pos:
                self.position_counter += 1
                if self.position_counter >= 3:  # Si bloqué au même endroit pendant 3 tours
                    self.position_counter = 0
                    return random.choice(["H", "B", "G", "D"])  # Mouvement aléatoire pour se débloquer
            else:
                self.position_counter = 0
        else:
            self.position_counter = 0
            
        self.derniere_position = bomber_pos

        # Se déplacer vers le minerai seulement si on est en sécurité
        if not self.derniere_bombe or self.get_safe_distance(self.derniere_bombe, bomber_pos):
            direction = self.get_direction_to_target(bomber_pos, minerai_proche, game_dict)
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
