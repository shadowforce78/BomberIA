##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################


class IA_Bomber:
    def __init__(
        self, num_joueur: int, game_dict: dict, timerglobal: int, timerfantôme: int
    ) -> None:
        """génère l'objet de la classe IA_Bomber

        Args:
            num_joueur (int): numéro de joueur attribué à l'IA
            game_dic (dict): descriptif de l'état initial de la partie
        """
        # game_dict = {
        #     "map": [
        #         "CCCCCCCCCCCCCCCCCCCCC",
        #         "C                 M C",
        #         "CCCCCCCCCCCCCCCCCCCCC",
        #     ],
        #     "bombers": [{"position": (2, 1), "niveau": 0, "pv": 3, "num_joueur": 0}],
        #     "fantômes": [],
        #     "bombes": [],
        #     "compteur_tour": 0,
        #     "scores": [0],
        # }

        # H/B/G/D/X/N = Haut/Bas/Gauche/Droite/Bombe/Ne rien faire

        self.num_joueur = num_joueur
        self.game_dict = game_dict
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme

        self.map = game_dict["map"]
        self.joueur = game_dict["bombers"]
        self.fantômes = game_dict["fantômes"]
        self.dispositif = game_dict["bombes"]
        self.compteur_tour = game_dict["compteur_tour"]
        self.scores = game_dict["scores"]

        self.position = self.joueur[self.num_joueur]["position"]

        def get_min_distance(pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        self.get_min_distance = get_min_distance

        def get_minerais(self, map):
            minerais = []
            for y in range(len(map)):
                for x in range(len(map[y])):
                    if map[y][x] == "M":
                        minerais.append((x, y))
            return minerais

        self.get_minerais = get_minerais

        # Ajout des fonctions de pathfinding
        def get_neighbors(self, pos, map):
            neighbors = []
            directions = [(0, 1), (1, 0), (-1, 0), (0, -1)]
            for dx, dy in directions:
                new_x, new_y = pos[0] + dx, pos[1] + dy
                if (
                    0 <= new_y < len(map)
                    and 0 <= new_x < len(map[0])
                    and map[new_y][new_x] != "C"
                ):
                    neighbors.append((new_x, new_y))
            return neighbors

        self.get_neighbors = get_neighbors

        def find_path(self, start, goal, map):
            from collections import deque
            frontier = deque([(start, [start])])
            visited = {start}
            ghost_positions = [g["position"] for g in game_dict["fantômes"]]  # Récup. fantômes

            while frontier:
                pos, path = frontier.popleft()
                if pos == goal:
                    return path
                    
                for next_pos in self.get_neighbors(self, pos, map):
                    # Éviter les fantômes de près (distance 2)
                    if any(self.get_min_distance(next_pos, gp) <= 2 for gp in ghost_positions):
                        continue
                    if next_pos not in visited:
                        visited.add(next_pos)
                        new_path = list(path)
                        new_path.append(next_pos)
                        frontier.append((next_pos, new_path))
            return []

        self.find_path = find_path

        def heuristic(self, pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        self.heuristic = heuristic

        def get_direction(self, current_pos, next_pos):
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            if dx == 1:
                return "D"
            if dx == -1:
                return "G"
            if dy == 1:
                return "B"
            if dy == -1:
                return "H"
            return "N"

        self.get_direction = get_direction

        # Initialisation du chemin
        self.current_path = []
        self.path_index = 0
        self.moves = []  # Add this line to store moves
        self.backtracking = False  # Add tracking for backtrack state
        self.backtrack_moves = []  # Store the sequence of moves to backtrack

        def get_reverse_direction(direction):
            if direction == "H":
                return "B"
            if direction == "B":
                return "H"
            if direction == "G":
                return "D"
            if direction == "D":
                return "G"
            return "N"

        self.get_reverse_direction = get_reverse_direction

        # Add these new variables
        self.just_bombed = False
        self.safe_path = []
        self.bomb_timer = 0  # Add timer to track bomb countdown
        
        def find_safe_spot(self, pos, map):
            # Check positions at least 3 cells away for better safety
            safe_spots = []
            search_range = 5  # Augmenté à 5
            for y in range(max(0, pos[1] - search_range), min(len(map), pos[1] + search_range + 1)):
                for x in range(max(0, pos[0] - search_range), min(len(map[0]), pos[0] + search_range + 1)):
                    if (map[y][x] != 'C' and 
                        (x, y) != pos and 
                        abs(x - pos[0]) + abs(y - pos[1]) >= 5):  # Augmenté à 5
                        safe_spots.append((x, y))
            return min(safe_spots, key=lambda p: self.get_min_distance(pos, p), default=None)
            
        self.find_safe_spot = find_safe_spot

        def predict_ghost_positions(self, ghosts, current_pos):
            danger_zones = set()
            for ghost in ghosts:
                ghost_pos = ghost["position"]
                # Add current ghost position
                danger_zones.add(ghost_pos)
                # Add potential next positions
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    next_x = ghost_pos[0] + dx
                    next_y = ghost_pos[1] + dy
                    if (0 <= next_y < len(self.map) and 
                        0 <= next_x < len(self.map[0]) and 
                        self.map[next_y][next_x] != 'C'):
                        danger_zones.add((next_x, next_y))
            return danger_zones

        def is_ghost_nearby(self, pos, ghosts, safe_distance=4):  # Augmentation de la distance de sécurité
            for ghost in ghosts:
                ghost_pos = ghost["position"]
                if self.get_min_distance(pos, ghost_pos) <= safe_distance:
                    return True
            return False
        
        def is_position_safe(self, pos, game_dict):
            # Vérification immédiate des fantômes
            for ghost in game_dict["fantômes"]:
                if self.get_min_distance(pos, ghost["position"]) <= 4:  # Distance de sécurité augmentée
                    return False

            # Vérification des bombes avec distance de sécurité augmentée
            for bomb in game_dict["bombes"]:
                bomb_pos = bomb["position"]
                if ((pos[0] == bomb_pos[0] and abs(pos[1] - bomb_pos[1]) <= 5) or  # Augmenté à 5
                   (pos[1] == bomb_pos[1] and abs(pos[0] - bomb_pos[0]) <= 5) or  # Augmenté à 5
                   self.get_min_distance(pos, bomb_pos) < 5):  # Augmenté à 5
                    return False
                    
            # Éviter les autres bombers
            for bomber in game_dict["bombers"]:
                if bomber["num_joueur"] != self.num_joueur and bomber["pv"] > 0:
                    if self.get_min_distance(pos, bomber["position"]) <= 2:  # Distance de sécurité pour les autres bombers
                        return False
                    
            return True

        def find_safest_escape(self, pos, game_dict):
            safe_spots = []
            checked = set()
            to_check = [(pos, 0)]
            max_distance = 8  # Augmentation de la distance de recherche
            
            while to_check:
                current_pos, dist = to_check.pop(0)
                if current_pos in checked or dist > max_distance:
                    continue
                    
                checked.add(current_pos)
                
                # Un endroit est sûr s'il est loin des fantômes et des autres bombers
                is_safe = True
                # Vérifier les fantômes
                for ghost in game_dict["fantômes"]:
                    if self.get_min_distance(current_pos, ghost["position"]) <= 4:
                        is_safe = False
                        break
                        
                # Vérifier les autres bombers
                if is_safe:
                    for bomber in game_dict["bombers"]:
                        if bomber["num_joueur"] != self.num_joueur and bomber["pv"] > 0:
                            if self.get_min_distance(current_pos, bomber["position"]) <= 2:
                                is_safe = False
                                break
                
                # Une position est sûre si elle est à au moins 5 cases de toute bombe
                for bomb in game_dict["bombes"]:
                    bomb_pos = bomb["position"]
                    if ((current_pos[0] == bomb_pos[0] and abs(current_pos[1] - bomb_pos[1]) <= 5) or  # Augmenté à 5
                        (current_pos[1] == bomb_pos[1] and abs(current_pos[0] - bomb_pos[0]) <= 5) or  # Augmenté à 5
                        self.get_min_distance(current_pos, bomb_pos) < 5):  # Augmenté à 5
                        is_safe = False
                        break

                if is_safe and current_pos != pos:
                    safe_spots.append((current_pos, dist))
                    if len(safe_spots) >= 3:
                        break
                        
                for next_pos in self.get_neighbors(self, current_pos, game_dict["map"]):
                    if next_pos not in checked:
                        to_check.append((next_pos, dist + 1))
                        
            if safe_spots:
                # Calculer le score de sécurité pour chaque position
                def get_safety_score(spot):
                    ghost_distance = float('inf')
                    if game_dict["fantômes"]:
                        ghost_distance = min(self.get_min_distance(spot[0], g["position"]) 
                                          for g in game_dict["fantômes"])
                    
                    bomber_distance = float('inf')
                    active_bombers = [b for b in game_dict["bombers"] 
                                    if b["num_joueur"] != self.num_joueur and b["pv"] > 0]
                    if active_bombers:
                        bomber_distance = min(self.get_min_distance(spot[0], b["position"]) 
                                           for b in active_bombers)
                    
                    return min(ghost_distance, bomber_distance * 2)
                
                return max(safe_spots, key=get_safety_score)[0]
            return None

        self.predict_ghost_positions = predict_ghost_positions
        self.is_ghost_nearby = is_ghost_nearby
        self.is_position_safe = is_position_safe
        self.find_safest_escape = find_safest_escape

        def can_hit_ghost(self, pos, ghost_pos):
            # Vérifie si un fantôme est à exactement 1 case de distance
            return self.get_min_distance(pos, ghost_pos) == 1

        def is_safe_to_bomb(self, pos, game_dict):
            # Vérifie si on a une route d'échappement
            escape_spot = self.find_safe_spot(self, pos, game_dict["map"])
            if not escape_spot:
                return False
                
            # Vérifie qu'il n'y a pas d'autres bombes à proximité
            for bomb in game_dict["bombes"]:
                if self.get_min_distance(pos, bomb["position"]) < 4:
                    return False
            
            return True

        self.can_hit_ghost = can_hit_ghost
        self.is_safe_to_bomb = is_safe_to_bomb

        def is_ghost_pursuing(self, pos, ghost_pos, prev_ghost_positions):
            # Vérifie si un fantôme se rapproche sur plusieurs tours
            if ghost_pos not in prev_ghost_positions:
                return False
            prev_dist = self.get_min_distance(pos, prev_ghost_positions[ghost_pos])
            current_dist = self.get_min_distance(pos, ghost_pos)
            return current_dist < prev_dist

        def find_defensive_position(self, pos, ghost_pos, game_dict):
            # Cherche une position où poser un dispositif qui bloquera le fantôme
            best_pos = None
            max_safety = -1
            
            for neighbor in self.get_neighbors(self, pos, game_dict["map"]):
                # Vérifie si la position crée une barrière entre nous et le fantôme
                if (self.get_min_distance(neighbor, ghost_pos) == 1 and 
                    self.is_safe_to_bomb(self, neighbor, game_dict)):
                    # Calcule la sécurité de la position
                    safety = self.get_min_distance(neighbor, ghost_pos)
                    if safety > max_safety:
                        max_safety = safety
                        best_pos = neighbor
            
            return best_pos

        self.is_ghost_pursuing = is_ghost_pursuing
        self.find_defensive_position = find_defensive_position
        self.prev_ghost_positions = {}  # Pour suivre les mouvements des fantômes

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""
        self.position = game_dict["bombers"][self.num_joueur]["position"]
        
        # Mise à jour des positions précédentes des fantômes
        current_ghost_positions = {}
        for ghost in game_dict["fantômes"]:
            ghost_pos = ghost["position"]
            current_ghost_positions[ghost_pos] = ghost_pos

        # Vérifie si un fantôme nous poursuit
        pursuing_ghost = None
        for ghost in game_dict["fantômes"]:
            ghost_pos = ghost["position"]
            if (self.get_min_distance(self.position, ghost_pos) <= 3 and 
                self.is_ghost_pursuing(self, self.position, ghost_pos, self.prev_ghost_positions)):
                pursuing_ghost = ghost
                break

        # Si un fantôme nous poursuit, chercher une position défensive
        if pursuing_ghost:
            defensive_pos = self.find_defensive_position(self, self.position, 
                                                       pursuing_ghost["position"], 
                                                       game_dict)
            if defensive_pos:
                # Si on est à la position défensive, poser le dispositif
                if defensive_pos == self.position:
                    self.just_bombed = True
                    self.bomb_timer = 0
                    return "X"
                # Sinon, se déplacer vers la position défensive
                return self.get_direction(self, self.position, defensive_pos)

        # Mise à jour des positions des fantômes pour le prochain tour
        self.prev_ghost_positions = current_ghost_positions

        # Vérification prioritaire des fantômes
        if game_dict["fantômes"]:
            closest_ghost_dist = min(
                self.get_min_distance(self.position, g["position"]) 
                for g in game_dict["fantômes"]
            )
            
            if closest_ghost_dist <= 4:  # Si un fantôme est trop proche
                safe_spot = self.find_safest_escape(self, self.position, game_dict)
                if safe_spot:
                    escape_path = self.find_path(self, self.position, safe_spot, game_dict["map"])
                    if escape_path and len(escape_path) > 1:
                        return self.get_direction(self, self.position, escape_path[1])
                
                # Si pas de chemin sûr, s'éloigner du fantôme le plus proche
                closest_ghost = min(game_dict["fantômes"], 
                                  key=lambda g: self.get_min_distance(self.position, g["position"]))
                ghost_pos = closest_ghost["position"]
                best_move = None
                max_distance = -1
                
                for neighbor in self.get_neighbors(self, self.position, game_dict["map"]):
                    dist = self.get_min_distance(neighbor, ghost_pos)
                    if dist > max_distance:
                        max_distance = dist
                        best_move = neighbor
                
                if best_move and max_distance > self.get_min_distance(self.position, ghost_pos):
                    return self.get_direction(self, self.position, best_move)
                return "N"  # Rester immobile si aucun mouvement sûr

        # Vérifier d'abord si on peut attaquer un fantôme
        if game_dict["fantômes"]:
            for ghost in game_dict["fantômes"]:
                ghost_pos = ghost["position"]
                if (self.can_hit_ghost(self, self.position, ghost_pos) and 
                    self.is_safe_to_bomb(self, self.position, game_dict)):
                    self.just_bombed = True
                    self.bomb_timer = 0
                    return "X"

        # Update bomb timer if active
        if self.just_bombed:
            if self.bomb_timer < 5:  # Stay safe for 5 turns
                self.bomb_timer += 1
                
                if not self.safe_path:  # Find path to safety if we don't have one
                    safe_spot = self.find_safe_spot(self, self.position, game_dict["map"])
                    if safe_spot:
                        self.safe_path = self.find_path(self, self.position, safe_spot, game_dict["map"])
                        if self.safe_path:
                            self.safe_path = self.safe_path[1:]
                
                if self.safe_path:  # Move along safety path
                    next_pos = self.safe_path.pop(0)
                    return self.get_direction(self, self.position, next_pos)
                return "N"  # Stay put if no safe path found
            else:
                # Reset bomb-related variables after 5 turns
                self.just_bombed = False
                self.bomb_timer = 0
                self.safe_path = []
                self.current_path = []  # Reset current path to recalculate route

        # Normal minerai seeking behavior
        minerais = self.get_minerais(self, game_dict["map"])
        if not minerais:
            return "N"

        # If next to minerai and it's safe, place bomb
        for minerai in minerais:
            if (self.get_min_distance(self.position, minerai) == 1 and 
                self.is_position_safe(self, self.position, game_dict)):
                self.just_bombed = True
                self.bomb_timer = 0
                self.safe_path = []
                return "X"
        
        # If no path or end of path, calculate new path
        if not self.current_path or self.path_index >= len(self.current_path):
            closest_minerai = min(minerais, key=lambda m: self.get_min_distance(self.position, m))
            # Calculate path and verify each position is safe
            temp_path = self.find_path(self, self.position, closest_minerai, game_dict["map"])
            # Filter out unsafe positions
            safe_path = [pos for pos in temp_path if self.is_position_safe(self, pos, game_dict)]
            
            if safe_path:
                self.current_path = safe_path
                self.path_index = 1
            else:
                return "N"  # No safe path found
        
        # Verify next move is still safe
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            if not self.is_position_safe(self, next_pos, game_dict):
                self.current_path = []  # Reset path if it's no longer safe
                return "N"
            self.path_index += 1
            return self.get_direction(self, self.position, next_pos)
            
        # Vérification des autres bombers proches
        dangerous_bomber = False
        for bomber in game_dict["bombers"]:
            if bomber["num_joueur"] != self.num_joueur and bomber["pv"] > 0:
                if self.get_min_distance(self.position, bomber["position"]) <= 2:
                    dangerous_bomber = True
                    break

        if dangerous_bomber:
            safe_spot = self.find_safest_escape(self, self.position, game_dict)
            if safe_spot:
                escape_path = self.find_path(self, self.position, safe_spot, game_dict["map"])
                if escape_path and len(escape_path) > 1:
                    return self.get_direction(self, self.position, escape_path[1])

        # Vérifier d'abord si on est en danger immédiat
        for bomb in game_dict["bombes"]:
            bomb_pos = bomb["position"]
            if ((self.position[0] == bomb_pos[0] and abs(self.position[1] - bomb_pos[1]) <= 5) or  # Augmenté à 5
                (self.position[1] == bomb_pos[1] and abs(self.position[0] - bomb_pos[0]) <= 5) or  # Augmenté à 5
                self.get_min_distance(self.position, bomb_pos) <= 5):  # Augmenté à 5
                safe_spot = self.find_safest_escape(self, self.position, game_dict)
                if safe_spot:
                    self.safe_path = self.find_path(self, self.position, safe_spot, game_dict["map"])
                    if len(self.safe_path) > 1:
                        return self.get_direction(self, self.position, self.safe_path[1])
                return "N"

        return "N"