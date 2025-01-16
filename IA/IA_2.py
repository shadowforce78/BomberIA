class IA_Bomber:
    def __init__(
        self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int
    ) -> None:
        self.num_joueur = num_joueur
        self.map = game_dic["map"]
        self.bombers = game_dic["bombers"]
        self.fantômes = game_dic["fantômes"]
        self.bombes = game_dic["bombes"]
        self.compteur_tour = game_dic["compteur_tour"]
        self.scores = game_dic["scores"]
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme
        self.last_bomb_position = None
        self.bomb_timer = 0
        self.escape_route = None

    def get_position(self) -> tuple:
        for bomber in self.bombers:
            if bomber["num_joueur"] == self.num_joueur:
                return bomber["position"]
        return None

    def get_minerais(self) -> list:
        minerais = []
        for y in range(len(self.map)):
            for x in range(len(self.map[y])):
                if self.map[y][x] == "M":
                    minerais.append((x, y))
        return minerais

    def is_position_safe(self, pos: tuple) -> bool:
        x, y = pos
        if not (0 <= x < len(self.map[0]) and 0 <= y < len(self.map)):
            return False
        return self.map[y][x] in [" ", "U"]

    def is_in_bomb_range(self, pos: tuple, bomb_pos: tuple, portée: int = 3) -> bool:
        x, y = pos
        bx, by = bomb_pos
        return (x == bx and abs(y - by) <= portée) or (
            y == by and abs(x - bx) <= portée
        )

    def get_escape_directions(self, pos: tuple) -> list:
        x, y = pos
        safe_directions = []
        moves = [
            ("H", (x, y - 1)),
            ("B", (x, y + 1)),
            ("G", (x - 1, y)),
            ("D", (x + 1, y)),
        ]

        for direction, new_pos in moves:
            if self.is_position_safe(new_pos):
                # Vérifier si la nouvelle position est hors de portée de toutes les bombes
                is_safe = True
                for bombe in self.bombes:
                    if self.is_in_bomb_range(
                        new_pos, bombe["position"], bombe["portée"]
                    ):
                        is_safe = False
                        break
                if is_safe:
                    safe_directions.append(direction)

        return safe_directions

    def should_place_bomb(self, pos: tuple) -> bool:
        x, y = pos
        # Vérifier la présence de minerai adjacent
        adjacent = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        for ax, ay in adjacent:
            if 0 <= ax < len(self.map[0]) and 0 <= ay < len(self.map):
                if self.map[ay][ax] == "M":
                    # Vérifier s'il existe une route d'échappement
                    escape_routes = self.get_escape_directions(pos)
                    return len(escape_routes) > 0
        return False

    def get_min_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_best_move_to_target(self, current: tuple, target: tuple) -> str:
        cx, cy = current
        tx, ty = target

        # Priorité au mouvement qui nous rapproche le plus de la cible
        if abs(tx - cx) > abs(ty - cy):
            if tx > cx and self.is_position_safe((cx + 1, cy)):
                return "D"
            elif tx < cx and self.is_position_safe((cx - 1, cy)):
                return "G"
            elif ty > cy and self.is_position_safe((cx, cy + 1)):
                return "B"
            elif ty < cy and self.is_position_safe((cx, cy - 1)):
                return "H"
        else:
            if ty > cy and self.is_position_safe((cx, cy + 1)):
                return "B"
            elif ty < cy and self.is_position_safe((cx, cy - 1)):
                return "H"
            elif tx > cx and self.is_position_safe((cx + 1, cy)):
                return "D"
            elif tx < cx and self.is_position_safe((cx - 1, cy)):
                return "G"

        # Si aucun mouvement direct n'est possible, essayer n'importe quelle direction sûre
        safe_directions = self.get_escape_directions((cx, cy))
        return safe_directions[0] if safe_directions else "N"

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

        # S'éloigner des bombes existantes
        for bombe in self.bombes:
            if self.get_min_distance(position, bombe["position"]) <= 2:
                safe_direction = self.find_safe_direction(position, bombe["position"])
                if safe_direction != "N":
                    return safe_direction

        # Récupération des minerais
        minerais = self.get_minerais()
        if not minerais:
            return "N"

        # Trouver le minerai le plus proche
        minerai_proche = min(minerais, key=lambda m: self.get_min_distance(position, m))

        # Si adjacent à un minerai, vérifier d'abord une route d'échappement
        if self.get_min_distance(position, minerai_proche) == 1:
            safe_direction = self.find_safe
