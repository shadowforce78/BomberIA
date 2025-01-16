##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

# H, B, G, D, X, N
# Haut, Bas, Gauche, Droite, Bombe, Ne rien faire


import random


class IA_Bomber:
    def __init__(
        self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int
    ) -> None:
        """génère l'objet de la classe IA_Bomber

        Args:
            num_joueur (int): numéro de joueur attribué à l'IA
            game_dic (dict): descriptif de l'état initial de la partie
        """
        print(game_dic)

        self.num_joueur = num_joueur
        self.map = game_dic["map"]
        self.bombers = game_dic["bombers"]
        self.fantômes = game_dic["fantômes"]
        self.bombes = game_dic["bombes"]
        self.compteur_tour = game_dic["compteur_tour"]
        self.scores = game_dic["scores"]
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme

        # Get current position
        position = self.get_position()

        # Get minerais
        minerais = self.get_minerais()

        # Display information
        self.display_info()

    def get_position(self) -> tuple:
        """Retourne la position du bomber"""
        for bomber in self.bombers:
            if bomber["num_joueur"] == self.num_joueur:
                return bomber["position"]
        return None

    def get_min_distance(self, pos1: tuple, pos2: tuple) -> int:
        """Calcule la distance de Manhattan entre deux points"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def flood_fill(self, pos: tuple, target: str) -> list:
        """Remplit une zone de cases vides en partant d'une position"""
        # Get the dimensions of the map
        width = len(self.map[0])
        height = len(self.map)

        # Initialize the queue
        queue = [pos]

        # Initialize the visited set
        visited = set()

        # Initialize the result set
        result = []

        # While the queue is not empty
        while queue:
            # Get the current position
            current = queue.pop(0)

            # If the current position is not visited
            if current not in visited:
                # Mark the current position as visited
                visited.add(current)

                # Add the current position to the result set
                result.append(current)

                # Get the neighbors of the current position
                neighbors = [
                    (current[0] - 1, current[1]),
                    (current[0] + 1, current[1]),
                    (current[0], current[1] - 1),
                    (current[0], current[1] + 1),
                ]

                # For each neighbor
                for neighbor in neighbors:
                    # If the neighbor is within the bounds of the map
                    if 0 <= neighbor[0] < width and 0 <= neighbor[1] < height:
                        # If the neighbor is empty
                        if self.map[neighbor[1]][neighbor[0]] == target:
                            # Add the neighbor to the queue
                            queue.append(neighbor)

        # Return the result set
        return result

    def get_empty_cells(self) -> list:
        """Retourne la liste des positions des cases vides"""
        empty_cells = []
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == " ":
                    empty_cells.append((j, i))  # Note: returning (x,y) coordinates
        return empty_cells

    def get_minerais(self) -> list:
        """Retourne la liste des positions des minerais"""
        minerais = []
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if self.map[i][j] == "M":
                    minerais.append((j, i))  # Note: returning (x,y) coordinates
        return minerais

    def draw_map_with_path(self, path: list) -> None:
        """Dessine la carte avec un chemin tracé"""
        # Copy the map
        map_with_path = [list(row) for row in self.map]

        # Draw the path on the map
        for pos in path:
            x, y = pos
            map_with_path[y][x] = "O"

        # Print the map with the path
        for row in map_with_path:
            print("".join(row))

    # Affiche toutes les informations de la partie (minerais accessible, distance...)
    def display_info(self):
        print("Position du bomber:", self.get_position())
        print("Minerais:", self.get_minerais())
        print("Distance de Manhattan:", self.get_min_distance((0, 0), (3, 4)))
        print("Cases vides:", self.get_empty_cells())
        # Flood fill a partir de la position du bomber
        print("Flood fill:", self.flood_fill(self.get_position(), " "))
        print("Map avec chemin:")
        self.draw_map_with_path(self.flood_fill(self.get_position(), " "))

    def move(self, direction: str) -> str:
        """Déplace le bomber dans une direction"""
        # Get the current position
        position = self.get_position()

        # Get the new position
        new_position = None
        if direction == "H":
            new_position = (position[0], position[1] - 1)
        elif direction == "B":
            new_position = (position[0], position[1] + 1)
        elif direction == "G":
            new_position = (position[0] - 1, position[1])
        elif direction == "D":
            new_position = (position[0] + 1, position[1])

        # Check if the new position is within the bounds of the map
        if 0 <= new_position[0] < len(self.map[0]) and 0 <= new_position[1] < len(
            self.map
        ):
            # Check if the new position is empty
            if (
                self.map[new_position[1]][new_position[0]] == " "
            ):  # Note: using (x,y) coordinates

                # Update the map
                self.map[position[1]][position[0]] = " "
                self.map[new_position[1]][new_position[0]] = "B"

    def is_in_blast_range(self, position: tuple, bomb_position: tuple) -> bool:
        """Vérifie si une position est dans la zone d'explosion d'une bombe (croix de range 2)"""
        x, y = position
        bx, by = bomb_position

        # Vérification horizontale
        if y == by and abs(x - bx) <= 2:
            return True
        # Vérification verticale
        if x == bx and abs(y - by) <= 2:
            return True
        return False

    def find_safe_direction(self, position: tuple, bomb_position: tuple) -> str:
        """Trouve une direction sûre pour s'éloigner d'une bombe"""
        # Tester toutes les directions possibles
        directions = [
            ("H", (position[0], position[1] - 1)),
            ("B", (position[0], position[1] + 1)),
            ("G", (position[0] - 1, position[1])),
            ("D", (position[0] + 1, position[1])),
        ]

        safe_moves = []
        for direction, new_pos in directions:
            # Vérifier si la position est dans la carte et si la case est vide
            if (
                0 <= new_pos[0] < len(self.map[0])
                and 0 <= new_pos[1] < len(self.map)
                and self.map[new_pos[1]][new_pos[0]] == " "
                and not self.is_in_blast_range(new_pos, bomb_position)
            ):
                # Calculer la distance par rapport à la position dangereuse
                distance = self.get_min_distance(new_pos, bomb_position)
                safe_moves.append((distance, direction))

        # Retourner la direction qui nous éloigne le plus du danger
        if safe_moves:
            safe_moves.sort(reverse=True)  # Trier par distance décroissante
            return safe_moves[0][1]
        return "N"

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA"""

        # Mise à jour des informations de la partie
        self.map = game_dict["map"]
        self.bombers = game_dict["bombers"]
        self.bombes = game_dict["bombes"]
        self.fantômes = game_dict["fantômes"]
        self.compteur_tour = game_dict["compteur_tour"]

        # Récupération de la position actuelle
        position = self.get_position()
        if not position:
            return "N"

        # Récupération des minerais
        minerais = self.get_minerais()
        if not minerais:
            return "N"

        # Trouver le minerai le plus proche
        minerai_proche = min(minerais, key=lambda m: self.get_min_distance(position, m))

        # Si adjacent à un minerai, poser une bombe
        if self.get_min_distance(position, minerai_proche) == 1:
            safe_direction = self.find_safe_direction(position, position)
            if safe_direction != "N":
                return safe_direction
            else:
                return "N"

        # Sinon, se déplacer vers le minerai le plus proche
        dx = minerai_proche[0] - position[0]
        dy = minerai_proche[1] - position[1]

        # Déplacement prioritaire sur l'axe avec la plus grande distance
        if abs(dx) > abs(dy):
            if dx > 0:
                return "D"
            else:
                return "G"
        else:
            if dy > 0:
                return "B"
            else:
                return "H"
