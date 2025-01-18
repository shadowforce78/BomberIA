##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################


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
                
        # Liste des positions des fantomes
        self.position_fantomes = set()
        for f in self.game_dict['fantômes']:
            self.position_fantomes.add(f['position'])

        # Chercher les parcours disponibles et le premier mur
        _, pred, target = self.parcours_largeur(carte, position, "M")

        # Partir de la bombe
        if self.attente is not None:
            # Si le temps est écoulé, arrêter d'attendre
            if game_dict['compteur_tour'] - self.attente > 4:
                self.attente = None

        if position in self.cases_touchees_par_bombe(game_dict['bombes'], carte) or self.attente is not None:
            case_sure, _, pred = self.trouver_case_sure_proche(position, game_dict['bombes'], carte)
            if case_sure:
                action = self.obtenir_direction(position, case_sure, pred)
                return action

        # Si un fantome est localisé proche, poser bombe
        if self.fantomeLocalise:
            self.fantomeLocalise = False
            self.attente = game_dict['compteur_tour']
            return "X"
        
        # Si un mur est trouvé
        if target:
            pos = self.obtenir_meilleure_position(carte, target, pred)
            chemin = self.calculer_chemin(position, pos, pred)
            if chemin:
                action = self.obtenir_direction(position, chemin[0])
                return action
            else:
                self.attente = game_dict['compteur_tour']
                action = "X"
                return action

        action = 'N' #Si aucune action n'est trouvée
        return action

    def parcours_largeur(self, niveau, sommet_depart, objectif=None):
        """
        Algorithme servant à:
            -Trouver les chemins possibles dans toute la carte.
            -Trouver le mur le plus proche
            -Détecter si un ennemie se trouve proche
        Args:
            niveau (list) : Carte du jeu
            sommet_depart (tuple) : Point de départ du parcours
            objectif (str) : Objectif à trouver (mur)
        Return:
            dict : Distance de chaque position découverte par rapport au point de départ
            dict : Position menant a chaque autre position accessible
            tuple : Position de l'objectif trouvé
        """
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
                
                if niveau[v[1]][v[0]] == ' ' : #si c'est une case vide
                    if v not in distance :  #si v est encore inconnu
                        # dans ce cas v est une case voisine vide et inconnue
                        distance[v] = distance[courant] + 1
                        pred[v] = courant
                        attente.append(v)  #v devra devenir courant plus tard

                elif objectif is not None and niveau[v[1]][v[0]] == objectif and self.attente is None: #Si la case est une mur, que c'est l'objectif et que le bomber n'est pas en attente
                    return distance, pred, v
                
        return distance, pred, None

    def calculer_chemin(self, depart, arrivee, predecesseurs):
        """
        Calcule le chemin à partir des prédécesseurs
        Args:
            depart (tuple) : Point de départ du chemin
            arrivee (tuple) : Point d'arriver.
            predecesseurs (dict) : Liste des prédécesseur
        Return:
            list : Liste du chemin du point de départ jusque l'arrivée
        """
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
        """
        Détermine la direction à prendre pour aller vers la position cible.
        Args:
            pos_actuelle (tuple) : Position de départ
            pos_cible (tuple) : Position d'arrivée (cible)
            predecesseurs (dict) : Liste des précédesseurs.
        Return:
            str : Direction à emprunter pour arriver à la position cible.
        """
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
        """
        Fonction permettant de trouver la meilleure position afin de détruire le plus de mur en un coup.
        Args:
            niveau (list) : Carte du jeu
            courant (tuple) : Position du mur
            pred (dict) : Liste des prédécesseurs pour arriver au mur.
        Return:
            tuple : position de la case la plus optimisée pour poser une bombe.
        """
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
        murs_adj_dict[courant] = 0 #Par défaut on met la position de départ (non valide car mur)

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
        Renvoie les cases touchées par UNE explosion à partir d'une position donnée et d'une portée.
        Arrête la propagation si une colonne ('C') ou une limite de carte est rencontrée.
        Args:
            position (tuple) : Position de la bombe
            portée (int) : Portée de la bombe
            niveau (list) : Carte du jeu
        Return:
            set : Set contenant les positions touchées par la bombe
        """
        x, y = position
        cases = set()
        
        # Directions possibles : Haut, Bas, Gauche, Droite
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for dx, dy in directions:
            for i in range(1, portée + 1):
                nx, ny = x + dx * i, y + dy * i #Calcul position par rapport a la direction et la portée

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
        """
        Renvoie les cases affectées par TOUTES les bombes à partir de leurs positions et de leurs rayons
        Args:
            bombes (list) : Liste de toutes les bombes (classes)
            niveau (list) : Carte du jeu
        Return:
            set : Set de toutes les cases qui seront touchées par une explosion
        """
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
    

    def calculer_cases_fantomes(self, fantomes):
        """
        Calcule les cases dangereuses autour des fantômes dans un rayon de 3.
        Args:
            fantomes (set): Ensemble des positions des fantômes (tuples (x, y)).
        Returns:
            set: Ensemble des cases dangereuses.
        """
        cases_fantomes = set()
        
        for x, y in fantomes:
            # Parcourir toutes les cases dans un rayon de 3 autour du fantôme
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    # Ajouter chaque case
                    cases_fantomes.add((x + dx, y + dy))
        
        return cases_fantomes


    def trouver_case_sure_proche(self, position, bombes, niveau):
        """
        Renvoie la case sûre la plus proche à partir de la position actuelle du bomber.
        Args:
            position (tuple) : Position du bomber
            bombes (list) : Liste des bombes (classes)
            niveau (list) : Carte du jeu
        Return:
            tuple : case la plus sûre
            dict : distances de la fonction parcours_largeur
            dict : prédécesseurs de la fonction parcours_largeur
        """
        danger = self.cases_touchees_par_bombe(bombes, niveau)
        cases_fantomes = self.calculer_cases_fantomes(self.position_fantomes)

        dist, pred, _ = self.parcours_largeur(niveau, position)
        for case in dist:
            if case not in danger and case not in cases_fantomes and niveau[case[1]][case[0]] == " ":
                return case, dist, pred  # Renvoie la première case sûre trouvée

        return None, dist, pred
