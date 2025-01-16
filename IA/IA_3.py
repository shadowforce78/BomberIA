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

        minerai = get_minerais(self, self.map)
        distance = get_min_distance(self.position, minerai[0])

        def is_on_same_line(self, pos1, pos2):
            return pos1[0] == pos2[0] or pos1[1] == pos2[1]

        same_line = is_on_same_line(self, self.position, minerai[0])

        def get_obstacle(self, pos1, pos2, map):
            if pos1[0] == pos2[0]:
                for y in range(min(pos1[1], pos2[1]), max(pos1[1], pos2[1])):
                    if map[y][pos1[0]] == "C":
                        return True
            else:
                for x in range(min(pos1[0], pos2[0]), max(pos1[0], pos2[0])):
                    if map[pos1[1]][x] == "C":
                        return True
            return False

        if same_line:
            if not get_obstacle(self, self.position, minerai[0], self.map):
                if self.position[0] == minerai[0][0]:
                    if self.position[1] > minerai[0][1]:
                        self.direction = "H"
                    else:
                        self.direction = "B"
                else:
                    if self.position[0] > minerai[0][0]:
                        self.direction = "G"
                    else:
                        self.direction = "D"
                print(
                    f"Direction: {self.direction} sur la même ligne de {self.position} à {minerai[0]} en {distance} cases"
                )
            else:
                self.direction = "N"
                print(f"Obstacle detected between {self.position} and {minerai[0]}")

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA

        Args:
            game_dict (dict) : décrit l'état actuel de la partie au moment
            où le joueur doit décider son action

        Returns:
            str : une action
        """

        return "N"
