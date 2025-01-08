##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random

class IA_Bomber:
    def __init__(self, num_joueur : int, game_dic : dict, timerglobal : int, timerfantôme: int) -> None:
        """génère l'objet de la classe IA_Bomber"""
        self.num_joueur = num_joueur
        self.timerglobal = timerglobal
        self.timerfantome = timerfantôme
        self.largeur = len(game_dic['map'][0])
        self.hauteur = len(game_dic['map'])
        # print(game_dic)

    def trouve_minerais(self, carte):
        """Trouve toutes les positions des minerais sur la carte"""
        minerais = []
        for y in range(self.hauteur):
            for x in range(self.largeur):
                if carte[y][x] == 'M':
                    minerais.append((x, y))
                    print(f"Minerais trouvés: {minerais}")  
        return minerais

    def distance_manhattan(self, pos1, pos2):
        """Calcule la distance Manhattan entre deux positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def meilleure_direction(self, pos_actuelle, pos_cible):
        """Détermine la meilleure direction pour aller vers la cible"""
        x1, y1 = pos_actuelle
        x2, y2 = pos_cible
        
        if x1 < x2: return 'D' # Droite
        if x1 > x2: return 'G' # Gauche
        if y1 < y2: return 'B' # Bas
        if y1 > y2: return 'H' # Haut
        return 'N' # Aucun mouvement

    def action(self, game_dict : dict) -> str:
        """Décide de l'action à effectuer"""
        # Récupérer la position actuelle du bomber
        ma_pos = game_dict['bombers'][self.num_joueur]['position']
        x, y = ma_pos

        # Convertir la carte en liste 2D pour un accès plus facile
        carte = [list(ligne) for ligne in game_dict['map']]

        # Vérifier les cases adjacentes pour les minerais
        directions = {'D': (1, 0), 'G': (-1, 0), 'H': (0, -1), 'B': (0, 1)}
        for direction, (dx, dy) in directions.items():
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.largeur and 0 <= new_y < self.hauteur:
                if carte[new_y][new_x] == 'M':
                    # Poser une bombe si adjacent à un minerai
                    # Puis se déplacer pour éviter de perdre de vie
                    for move_direction, (mx, my) in directions.items():
                        move_x, move_y = x + mx, y + my
                        if (0 <= move_x < self.largeur and 
                            0 <= move_y < self.hauteur and 
                            carte[move_y][move_x] not in ['C']):
                            return 'X' + move_direction

        # Trouver tous les minerais
        minerais = self.trouve_minerais(carte)
        if not minerais:
            return random.choice(['D', 'G', 'H', 'B'])

        # Trouver le minerai le plus proche
        distances = [(m, self.distance_manhattan(ma_pos, m)) for m in minerais]
        minerai_plus_proche = min(distances, key=lambda x: x[1])[0]

        # Se déplacer vers le minerai le plus proche
        direction = self.meilleure_direction(ma_pos, minerai_plus_proche)
        new_pos = (x + directions[direction][0], y + directions[direction][1])
        
        # Vérifier si le mouvement est possible (pas de mur)
        if (0 <= new_pos[0] < self.largeur and 
            0 <= new_pos[1] < self.hauteur and 
            carte[new_pos[1]][new_pos[0]] not in ['C']):
            return direction

        # Si le mouvement n'est pas possible, choisir une direction aléatoire
        return random.choice(['D', 'G', 'H', 'B'])


