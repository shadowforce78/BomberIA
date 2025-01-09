##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
from collections import deque
from typing import Optional, Tuple, List


class IA_Bomber:
    def __init__(
        self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int
    ) -> None:
        self.num_joueur = num_joueur
        self.height = len(game_dic["map"])
        self.width = len(game_dic["map"][0])
        self.current_path = []

    def get_position(self, game_dict: dict) -> Tuple[int, int]:
        """Récupère la position actuelle du bomber"""
        for bomber in game_dict["bombers"]:
            if bomber["num_joueur"] == self.num_joueur:
                return bomber["position"]
        return (-1, -1)

    def flood_fill(
        self, game_dict: dict, start_pos: Tuple[int, int]
    ) -> Optional[List[str]]:
        """Utilise le flood fill pour trouver le chemin le plus court vers le minerai le plus proche"""
        visited = set()
        queue = deque([(start_pos, [])])
        map_data = game_dict["map"]

        while queue:
            (x, y), path = queue.popleft()

            if map_data[y][x] == "M":  # Minerai trouvé
                return path

            # Vérifie les 4 directions
            directions = [
                ("D", (x + 1, y)),
                ("G", (x - 1, y)),
                ("H", (x, y - 1)),
                ("B", (x, y + 1)),
            ]
            for direction, (new_x, new_y) in directions:
                if (
                    (new_x, new_y) not in visited
                    and 0 <= new_x < self.width
                    and 0 <= new_y < self.height
                    and map_data[new_y][new_x] not in ["C", "E"]
                ):
                    visited.add((new_x, new_y))
                    queue.append(((new_x, new_y), path + [direction]))

        return None

    def action(self, game_dict: dict) -> str:
        """Détermine l'action à effectuer"""
        current_pos = self.get_position(game_dict)

        # Si nous n'avons pas de chemin actuel, cherchons-en un nouveau
        if not self.current_path:
            path = self.flood_fill(game_dict, current_pos)
            if path:
                self.current_path = path

        # Si nous avons un chemin
        if self.current_path:
            # Si nous sommes adjacents à un minerai, posons une bombe
            x, y = current_pos
            adjacent_positions = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
            for adj_x, adj_y in adjacent_positions:
                if 0 <= adj_x < self.width and 0 <= adj_y < self.height:
                    if game_dict["map"][adj_y][adj_x] == "M":
                        self.current_path = []
                        return "X"

            # Sinon, suivons le chemin
            next_move = self.current_path.pop(0)
            return next_move

        # Si nous n'avons pas de chemin, restons immobiles
        return "N"
