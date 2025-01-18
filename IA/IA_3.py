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

        def is_ghost_nearby(self, pos, ghosts, safe_distance=2):
            for ghost in ghosts:
                if self.get_min_distance(pos, ghost["position"]) <= safe_distance:
                    return True
            return False
        
        def is_position_safe(self, pos, game_dict):
            # Check for ghosts
            if self.is_ghost_nearby(self, pos, game_dict["fantômes"]):
                return False
            # Check for bombs
            for bomb in game_dict["bombes"]:
                if self.get_min_distance(pos, bomb["position"]) < 2:
                    return False
            return True
            
        def find_safe_path(self, start, goal, game_dict):
            # Modified pathfinding that avoids ghosts
            from collections import deque
            frontier = deque([(start, [start])])
            visited = {start}
            
            while frontier:
                pos, path = frontier.popleft()
                if pos == goal:
                    return path
                    
                for next_pos in self.get_neighbors(self, pos, game_dict["map"]):
                    if next_pos not in visited and self.is_position_safe(self, next_pos, game_dict):
                        visited.add(next_pos)
                        new_path = list(path)
                        new_path.append(next_pos)
                        frontier.append((next_pos, new_path))
            return []

        self.is_ghost_nearby = is_ghost_nearby
        self.is_position_safe = is_position_safe
        self.find_safe_path = find_safe_path

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""
        self.position = game_dict["bombers"][self.num_joueur]["position"]
        
        # First priority: Check if we're in immediate danger from ghosts
        if self.is_ghost_nearby(self, self.position, game_dict["fantômes"], 1):
            # Try to find immediate escape route
            safe_spots = []
            for neighbor in self.get_neighbors(self, self.position, game_dict["map"]):
                if self.is_position_safe(self, neighbor, game_dict):
                    safe_spots.append(neighbor)
            
            if safe_spots:
                safest_spot = min(safe_spots, 
                                key=lambda p: min(self.get_min_distance(p, g["position"]) 
                                                for g in game_dict["fantômes"]))
                return self.get_direction(self, self.position, safest_spot)

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
        
        # If no path or end of path, calculate new safe path
        if not self.current_path or self.path_index >= len(self.current_path):
            closest_minerai = min(minerais, key=lambda m: self.get_min_distance(self.position, m))
            self.current_path = self.find_safe_path(self, self.position, closest_minerai, game_dict)
            self.path_index = 1
            if not self.current_path:  # If no safe path found
                return "N"
        
        # Verify next move is still safe
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            if not self.is_position_safe(self, next_pos, game_dict):
                self.current_path = []  # Reset path if it's no longer safe
                return "N"
            self.path_index += 1
            return self.get_direction(self, self.position, next_pos)
            
        return "N"
