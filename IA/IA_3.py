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
            # Simple BFS implementation
            from collections import deque
            frontier = deque([(start, [start])])
            visited = {start}
            
            while frontier:
                pos, path = frontier.popleft()
                if pos == goal:
                    return path
                    
                for next_pos in self.get_neighbors(self, pos, map):
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
            search_range = 4  # Increased search range
            for y in range(max(0, pos[1] - search_range), min(len(map), pos[1] + search_range + 1)):
                for x in range(max(0, pos[0] - search_range), min(len(map[0]), pos[0] + search_range + 1)):
                    if (map[y][x] != 'C' and 
                        (x, y) != pos and 
                        abs(x - pos[0]) + abs(y - pos[1]) >= 3):  # Increased minimum distance
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

        def is_ghost_nearby(self, pos, ghosts, safe_distance=3):  # Increased safe distance
            for ghost in ghosts:
                ghost_pos = ghost["position"]
                if self.get_min_distance(pos, ghost_pos) <= safe_distance:
                    # Check if ghost is moving towards us
                    dx = pos[0] - ghost_pos[0]
                    dy = pos[1] - ghost_pos[1]
                    if abs(dx) <= 1 and abs(dy) <= 1:  # Adjacent positions are extra dangerous
                        return True
                    if (abs(dx) > abs(dy) and dx > 0) or (abs(dy) > abs(dx) and dy > 0):
                        return True
            return False
        
        def is_position_safe(self, pos, game_dict):
            danger_zones = self.predict_ghost_positions(self, game_dict["fantômes"], pos)
            
            # Position is unsafe if it's in predicted ghost paths
            if pos in danger_zones:
                return False
                
            # Check for immediate ghost proximity
            if self.is_ghost_nearby(self, pos, game_dict["fantômes"]):
                return False
                
            # Check for bombs
            for bomb in game_dict["bombes"]:
                if self.get_min_distance(pos, bomb["position"]) < 3:  # Increased bomb safety distance
                    return False
                    
            return True

        def find_safest_escape(self, pos, game_dict):
            safe_spots = []
            checked = set()
            to_check = [(pos, 0)]  # (position, distance)
            
            while to_check:
                current_pos, dist = to_check.pop(0)
                if current_pos in checked:
                    continue
                    
                checked.add(current_pos)
                
                if self.is_position_safe(self, current_pos, game_dict) and current_pos != pos:
                    safe_spots.append((current_pos, dist))
                    if len(safe_spots) >= 3:  # Found enough safe spots
                        break
                        
                for next_pos in self.get_neighbors(self, current_pos, game_dict["map"]):
                    if next_pos not in checked:
                        to_check.append((next_pos, dist + 1))
                        
            if safe_spots:
                # Return the closest safe spot
                return min(safe_spots, key=lambda x: x[1])[0]
            return None

        self.predict_ghost_positions = predict_ghost_positions
        self.is_ghost_nearby = is_ghost_nearby
        self.is_position_safe = is_position_safe
        self.find_safest_escape = find_safest_escape

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""
        self.position = game_dict["bombers"][self.num_joueur]["position"]
        
        # First priority: Check if we're in immediate danger from ghosts
        if not self.is_position_safe(self, self.position, game_dict):
            safe_spot = self.find_safest_escape(self, self.position, game_dict)
            if safe_spot:
                escape_path = self.find_path(self, self.position, safe_spot, game_dict["map"])
                if escape_path and len(escape_path) > 1:
                    return self.get_direction(self, self.position, escape_path[1])
            # If no safe path found, try to move away from closest ghost
            closest_ghost = min(game_dict["fantômes"], 
                              key=lambda g: self.get_min_distance(self.position, g["position"]))
            ghost_pos = closest_ghost["position"]
            for neighbor in self.get_neighbors(self, self.position, game_dict["map"]):
                if self.get_min_distance(neighbor, ghost_pos) > self.get_min_distance(self.position, ghost_pos):
                    return self.get_direction(self, self.position, neighbor)
            return "N"  # No safe move found

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
            
        return "N"