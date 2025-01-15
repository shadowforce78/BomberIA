import random

class IA_Bomber:
    def __init__(self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int) -> None:
        """Initialise l'IA avec son numéro de joueur et les paramètres du jeu."""
        self.num_joueur = num_joueur
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme
        self.derniere_action = None
        self.compte_recul = 0  # Nombre de tours pendant lesquels reculer
        self.direction_recul = None

    def is_safe_position(self, pos: tuple[int, int], game_dict: dict) -> bool:
        """Vérifie si une position est sûre en fonction des bombes et des fantômes."""
        for bombe in game_dict.get("bombes", []):
            bombe_pos = bombe["position"]
            portée = bombe["portée"]
            if pos[0] == bombe_pos[0] or pos[1] == bombe_pos[1]:
                distance = abs(pos[0] - bombe_pos[0]) + abs(pos[1] - bombe_pos[1])
                if distance <= portée:
                    return False

        for fantome in game_dict.get("fantômes", []):
            fantome_pos = fantome["position"]
            if abs(pos[0] - fantome_pos[0]) + abs(pos[1] - fantome_pos[1]) <= 1:
                return False

        return True

    def get_safe_direction(self, pos: tuple[int, int], game_dict: dict) -> str:
        """Trouve une direction sûre pour éviter les dangers."""
        directions = {"H": (0, -1), "B": (0, 1), "G": (-1, 0), "D": (1, 0)}
        for direction, (dx, dy) in directions.items():
            new_pos = (pos[0] + dx, pos[1] + dy)
            if self.is_safe_position(new_pos, game_dict):
                return direction
        return "N"

    def should_place_bomb(self, pos: tuple[int, int], game_dict: dict) -> bool:
        """Détermine si une bombe doit être posée."""
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if 0 <= new_y < len(game_dict["map"]) and 0 <= new_x < len(game_dict["map"][0]):
                if game_dict["map"][new_y][new_x] == "M":  # Minerai adjacent
                    return True
        return False

    def action(self, game_dict: dict) -> str:
        """Prend une décision basée sur l'état actuel du jeu."""
        # Position actuelle
        bomber_pos = None
        for bomber in game_dict["bombers"]:
            if bomber["num_joueur"] == self.num_joueur:
                bomber_pos = bomber["position"]
                break

        if not bomber_pos:
            return "N"

        # Gestion de la fuite (si en recul)
        if self.compte_recul > 0:
            self.compte_recul -= 1
            return self.direction_recul

        # Vérification des bombes proches
        in_danger = not self.is_safe_position(bomber_pos, game_dict)
        if in_danger:
            self.direction_recul = self.get_safe_direction(bomber_pos, game_dict)
            if self.direction_recul != "N":
                self.compte_recul = 3  # Recul pendant 3 tours
                return self.direction_recul

        # Poser une bombe si un minerai est adjacent
        if self.should_place_bomb(bomber_pos, game_dict):
            self.compte_recul = 3  # Prépare un recul après avoir posé une bombe
            self.direction_recul = self.get_safe_direction(bomber_pos, game_dict)
            return "X"

        # Recherche de minerais
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_x, new_y = bomber_pos[0] + dx, bomber_pos[1] + dy
            if 0 <= new_y < len(game_dict["map"]) and 0 <= new_x < len(game_dict["map"][0]):
                if game_dict["map"][new_y][new_x] == "M":  # Aller vers un minerai
                    return {0: "H", 1: "B", -1: "G", 2: "D"}[(dy, dx)]

        # Mouvement aléatoire (si aucune autre action)
        return random.choice(["H", "B", "G", "D", "N"])
