##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
import sys
import os

class IA_Bomber:
    def __init__(self, num_joueur : int, game_dic : dict, timerglobal : int, timerfantôme: int) -> None:
        """génère l'objet de la classe IA_Bomber

        Args:
            num_joueur (int): numéro de joueur attribué à l'IA
            game_dic (dict): descriptif de l'état initial de la partie
        """

        self.game_dict = game_dic
        self.num_joueur = num_joueur
        self.attente = None
        self.position_fantomes = set()
        self.fantomeLocalise = False
        self.timeToWait = None
        self.historique = []

    #TODO
    pass

    def action(self, game_dict: dict) -> str:
        """Appelé à chaque décision du joueur IA
        Args:
            game_dict (dict): décrit l'état actuel de la partie
        Returns:
            str: une action ('D', 'G', 'H', 'B', 'X', 'N')
        """
        self.game_dict = game_dict
        position = game_dict['bombers'][self.num_joueur]['position']
        carte = game_dict['map']

        #On remplace les autre bombes par des "colonnes" pour éviter de se bloquer
        for bomber in game_dict['bombers']:
            if bomber['num_joueur'] != self.num_joueur:
                x, y = bomber['position']  # Extraire la position de la bombe
                carte[y] = carte[y][:x] + "C" + carte[y][x + 1:]
                
        self.position_fantomes = set()

        if len(self.historique) > 10:
            self.historique.pop(0)
        if self.historique.count("N") > 0: self.historique.remove("N")

        for f in self.game_dict['fantômes']:
            self.position_fantomes.add(f['position'])
        # Chercher mur et poser bombe
        _, pred, target = self.parcours_largeur(carte, position, "M")
        # Partir de la bombe
        if self.attente is not None:
            # Si le temps est écoulé, arrêter d'attendre
            if game_dict['compteur_tour'] - self.attente > 4:
                self.attente = None
            else: 
                case_sure, _, pred = self.trouver_case_sure_proche(position, game_dict['bombes'], carte)
                if case_sure:

                    action = self.obtenir_direction(position, case_sure, pred)
                    self.historique.append(action)  # Enregistrer l'action
                    return action

        if position in self.cases_touchees_par_bombe(game_dict['bombes'], carte):
            case_sure, _, pred = self.trouver_case_sure_proche(position, game_dict['bombes'], carte)
            print("viesviesviesviesviesviesviesviesvies")
            if case_sure:

                action = self.obtenir_direction(position, case_sure, pred)
                self.historique.append(action)  # Enregistrer l'action
                return action



        if target:
            pos = self.obtenir_meilleure_position(carte, target, pred)
            chemin = self.calculer_chemin(position, pos, pred)
            if chemin:
                action = self.obtenir_direction(position, chemin[0])
                self.historique.append(action)  # Enregistrer l'action
                return action
            else:
                self.attente = game_dict['compteur_tour']
                action = "X"
                self.historique.append(action)  # Enregistrer l'action
                return action

        action = 'N'
        self.historique.append(action)  # Enregistrer l'action
        return action

    def parcours_largeur(self, niveau, sommet_depart, objectif=None):
        distance = {}
        distance[sommet_depart] = 0
        pred = {}
        attente = []  #file d'attente
        attente.append(sommet_depart)
        
        while len(attente) > 0:
            courant = attente.pop(0) #sommet dont on va chercher les voisins
            
            #chercher les voisins de courant
            voisins_possibles = [(courant[0]+1,courant[1]), (courant[0]-1,courant[1]), (courant[0],courant[1]+1), (courant[0],courant[1]-1)]

            for v in voisins_possibles:
                if v in self.position_fantomes and distance[courant] <= (self.game_dict['bombers'][self.num_joueur]['niveau']//2)+2:
                    self.fantomeLocalise = True
                    return distance, pred, None
                
                if niveau[v[1]][v[0]] == ' ' : #si c'est une case vide
                    if v not in distance :  #si v est encore inconnu
                        # dans ce cas v est une case voisine vide et inconnue
                        distance[v] = distance[courant] + 1
                        pred[v] = courant
                        attente.append(v)  #v devra devenir courant plus tard

                elif objectif is not None and niveau[v[1]][v[0]] == objectif and self.attente is None: #Si la case est une mur, que c'est l'objectif et que le bomber n'est pas en attente
                    return distance, pred, v
                
        return distance, pred, None

    def inverse_action(self, action):
        match action:
            case "Q":
                return "D"
            case "D":
                return "Q"
            case "H":
                return "B"
            case "B":
                return "H"
            case _:
                return "N"

    def calculer_chemin(self, depart, arrivee, predecesseurs):
        """Calcule le chemin à partir des prédécesseurs"""
        if not predecesseurs:
            return []
            
        chemin = []
        position = arrivee
        
        while position != depart:
            chemin.append(position)
            if position not in predecesseurs:
                return []
            position = predecesseurs[position]
            
        chemin.reverse()
        return chemin

    def obtenir_direction(self, pos_actuelle, pos_cible, predecesseurs=None):
        """Détermine la direction à prendre pour aller vers la position cible"""
        if pos_actuelle is None or pos_cible is None: return "N"
        dx = pos_cible[0] - pos_actuelle[0]
        dy = pos_cible[1] - pos_actuelle[1]

        if dx == 1 and dy == 0:  # Droite
            return 'D'
        if dx == -1 and dy == 0:  # Gauche
            return 'G'
        if dx == 0 and dy == 1:  # Bas
            return 'B'
        if dx == 0 and dy == -1:  # Haut
            return 'H'

        # Si la cible est éloignée, trouver une case intermédiaire
        if predecesseurs is not None:
            chemin = self.calculer_chemin(pos_actuelle, pos_cible, predecesseurs)
            if chemin:
                return self.obtenir_direction(pos_actuelle, chemin[0])  # Première étape du chemin
            return 'N'  # Si aucun chemin n'est possible

        return 'N'
    
    def obtenir_meilleure_position(self, niveau, courant, pred):
        # Liste des voisins possibles autour de la position actuelle
        voisins_possibles = [
            (courant[0] + 1, courant[1]),        # Bas
            (courant[0] - 1, courant[1]),        # Haut
            (courant[0], courant[1] + 1),        # Droite
            (courant[0], courant[1] - 1),        # Gauche
            (courant[0] - 1, courant[1] - 1),    # Haut-gauche (diagonale)
            (courant[0] - 1, courant[1] + 1),    # Haut-droit (diagonale)
            (courant[0] + 1, courant[1] - 1),    # Bas-gauche (diagonale)
            (courant[0] + 1, courant[1] + 1)     # Bas-droit (diagonale)
        ]

        # Dictionnaire pour stocker le nombre de murs adjacents pour chaque position
        murs_adj_dict = {}
        murs_adj_dict[courant] = 0 #Par défaut on met la position de départ
        # Parcours des voisins possibles
        for v in voisins_possibles:
            # Vérifier si le voisin est valide (dans `pred` et sur une case vide " ")
            if v in pred and niveau[v[1]][v[0]] == " ":
                compteur_murs = 0

                # Vérifier les cases adjacentes au voisin (dans un rayon de 1)
                adjacents = [
                    (v[0] + 1, v[1]),
                    (v[0] - 1, v[1]),
                    (v[0], v[1] + 1),
                    (v[0], v[1] - 1)
                ]

                for adj in adjacents:
                    # Si une case adjacente est un mur ('M'), incrémenter le compteur
                    if niveau[adj[1]][adj[0]]  == "M":
                        compteur_murs += 1

                # Stocker le résultat dans le dictionnaire
                if compteur_murs > 0:
                    murs_adj_dict[v] = compteur_murs

        # Trouver la position avec le maximum de murs adjacents
        if murs_adj_dict:
            meilleure_position = max(murs_adj_dict, key=murs_adj_dict.get)
            return meilleure_position

        # Si aucun voisin valide, retourner la position actuelle
        return courant
    


    def obtenir_pattern_explosion(self, position, portée, niveau):
        """
        Renvoie les cases touchées par une explosion à partir d'une position donnée et d'une portée.
        Arrête la propagation si une colonne ('C') ou une limite est rencontrée.
        """
        x, y = position
        cases = set()
        
        # Directions possibles : Haut, Bas, Gauche, Droite
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for dx, dy in directions:
            for i in range(1, portée + 1):
                nx, ny = x + dx * i, y + dy * i

                # Vérifier les limites de la carte
                if ny < 0 or ny >= len(niveau) or nx < 0 or nx >= len(niveau[0]):
                    break

                # Ajouter la case actuelle
                cases.add((nx, ny))

                # Arrêter si une colonne ('C') est rencontrée
                if niveau[ny][nx] == 'C':
                    break

        return cases
    

    
    def cases_touchees_par_bombe(self, bombes, niveau):
        """Renvoie les cases affectées par une bombe à partir de sa position et de son rayon"""
        cases_dangereuses = set()

        for bombe in bombes:
            position = bombe['position']
            portée = bombe['portée']

            # Obtenir le pattern d'explosion pour cette bombe
            explosion = self.obtenir_pattern_explosion(position, portée, niveau)

            # Ajouter toutes les cases touchées par cette bombe
            cases_dangereuses.update(explosion)

            # Ajouter la position de la bombe elle-même
            cases_dangereuses.add(position)

        return cases_dangereuses
    
    def trouver_case_sure_proche(self, position, bombes, niveau):
        """Renvoie la case sûre la plus proche à partir de la position actuelle"""
        danger = self.cases_touchees_par_bombe(bombes, niveau)
        cases_fantomes = set()
        for fantome in self.position_fantomes:
            x, y = fantome
            # Ajouter les cases adjacentes à une distance de 1
            cases_fantomes.update({
                (x + 1, y),
                (x - 1, y),
                (x, y + 1),
                (x, y - 1)
            })
            # Ajouter les cases à une distance de 2
            cases_fantomes.update({
                (x + 2, y),
                (x - 2, y),
                (x, y + 2),
                (x, y - 2),
                (x + 1, y + 1),
                (x + 1, y - 1),
                (x - 1, y + 1),
                (x - 1, y - 1)
            })
            

        dist, pred, _ = self.parcours_largeur(niveau, position)
        for case in dist:
            if case not in danger and case not in cases_fantomes and niveau[case[1]][case[0]] == " ":
                return case, dist, pred  # Renvoie la première case sûre trouvée

        return None, dist, pred
