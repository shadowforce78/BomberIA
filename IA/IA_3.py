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
        self.bombers = game_dict["bombers"]
        self.fantômes = game_dict["fantômes"]
        self.bombes = game_dict["bombes"]
        self.compteur_tour = game_dict["compteur_tour"]
        self.scores = game_dict["scores"]

        self.position = self.bombers[self.num_joueur]["position"]

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

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""
        self.position = game_dict["bombers"][self.num_joueur]["position"]

        # Check if we're next to a minerai
        minerais = self.get_minerais(self, game_dict["map"])
        if not minerais:
            return "N"

        # If next to minerai, place bomb
        for minerai in minerais:
            if self.get_min_distance(self.position, minerai) == 1:
                return "X"
        
        # If no path or end of path, calculate new path
        if not self.current_path or self.path_index >= len(self.current_path):
            closest_minerai = min(minerais, key=lambda m: self.get_min_distance(self.position, m))
            self.current_path = self.find_path(self, self.position, closest_minerai, game_dict["map"])
            self.path_index = 1
            if not self.current_path:  # If no path found
                return "N"
        
        # Get next move from path
        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            self.path_index += 1
            return self.get_direction(self, self.position, next_pos)
            
        return "N"
