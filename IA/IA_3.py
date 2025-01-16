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
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Bas, Haut, Droite, Gauche
            for dx, dy in directions:
                new_x, new_y = pos[0] + dx, pos[1] + dy
                if (0 <= new_y < len(map) and 
                    0 <= new_x < len(map[0]) and 
                    map[new_y][new_x] != 'C'):
                    neighbors.append((new_x, new_y))
            return neighbors

        self.get_neighbors = get_neighbors

        def heuristic(self, pos1, pos2):
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        self.heuristic = heuristic

        def find_path(self, start, goal, map):
            from heapq import heappush, heappop
            frontier = []
            heappush(frontier, (0, start))
            came_from = {start: None}
            cost_so_far = {start: 0}

            while frontier:
                current = heappop(frontier)[1]
                
                if current == goal:
                    break

                for next_pos in self.get_neighbors(self, current, map):
                    new_cost = cost_so_far[current] + 1
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + self.heuristic(self, goal, next_pos)
                        heappush(frontier, (priority, next_pos))
                        came_from[next_pos] = current

            # Reconstruction du chemin
            path = []
            current = goal
            while current is not None:
                path.append(current)
                current = came_from.get(current)
            path.reverse()
            return path if path[0] == start else []

        self.find_path = find_path

        def get_direction(self, current_pos, next_pos):
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            if dx == 1: return "D"
            if dx == -1: return "G"
            if dy == 1: return "B"
            if dy == -1: return "H"
            return "N"

        self.get_direction = get_direction

        # Initialisation du chemin
        minerais = self.get_minerais(self, self.map)
        if minerais:
            self.current_path = self.find_path(self, self.position, minerais[0], self.map)
            self.path_index = 1 if len(self.current_path) > 1 else 0
        else:
            self.current_path = []
            self.path_index = 0

        self.moves = []  # Add this line to store moves
        
        def get_reverse_direction(direction):
            if direction == "H": return "B"
            if direction == "B": return "H"
            if direction == "G": return "D"
            if direction == "D": return "G"
            return "N"

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""
        self.position = game_dict["bombers"][self.num_joueur]["position"]
        
        # Check if we're next to a minerai
        minerais = self.get_minerais(self, game_dict["map"])
        if minerais:
            closest_minerai = minerais[0]
            if self.get_min_distance(self.position, closest_minerai) == 1:
                move = "X"
                self.moves.append(move)  # Store the move
                return move
        
        if not self.current_path or self.path_index >= len(self.current_path):
            if minerais:
                self.current_path = self.find_path(self, self.position, minerais[0], game_dict["map"])
                self.path_index = 1 if len(self.current_path) > 1 else 0
            else:
                move = "N"
                self.moves.append(move)  # Store the move
                return move

        if self.path_index < len(self.current_path):
            next_pos = self.current_path[self.path_index]
            direction = self.get_direction(self, self.position, next_pos)
            self.path_index += 1
            self.moves.append(direction)  # Store the move
            return direction

        move = "N"
        self.moves.append(move)  # Store the move
        return move
