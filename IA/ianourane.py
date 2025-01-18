##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
import math

class IA_Bomber:
    def __init__(self, num_joueur : int, game_dic : dict, timerglobal : int, timerfantôme: int) -> None:
        """génère l'objet de la classe IA_Bomber

        Args:
            num_joueur (int): numéro de joueur attribué à l'IA
            game_dic (dict): descriptif de l'état initial de la partie
            timerglobal (int): temps du jeu
            timerfantôme (int): temps entre chaque apparition de fantômes
        """

        self.num_joueur = num_joueur
        self.game_dic = game_dic
        self.timerglobal = timerglobal
        self.timerfantôme = timerfantôme


############################################################################################
#                               GESTION DES DEPLACEMENTS                                   #
############################################################################################


    def mouvement(self, choix_mouvement, pos_joueur):
        """
        Détermine le déplacement à renvoyer en fonction de la nouvelle position

        Args:
            choix_mouvement (tuple) : position vers laquelle le joueur se dirige
            pos_joueur (tuple) : position actuelle du joueur
        
        Return:
            choix_action (str) : action (H, B, G, D) que le joueur va effectué
        """
        if choix_mouvement[0] == pos_joueur[0]:
            if choix_mouvement[1] < pos_joueur[1]:
                choix_action = 'H'
            else:
                choix_action = 'B'
        elif choix_mouvement[0] < pos_joueur[0]:
            choix_action = 'G'
        else:
            choix_action = 'D'
        return choix_action
    
    def parcours_largeur(self, niveau, sommet_depart):
        """
        Cette méthode nous permet d'obtenir les positions accessibles depuis un point de départ.

        Args:
            niveau (list) : Il s'agit de la carte du jeu
            sommet_départ (tuples) : Point de départ de notre recherche

        Return:
            distance (dic) : Dictionnaire des positions accessibles et leur distance en déplacement du point de départ
        """
        distance = {}
        distance[sommet_depart] = 0
        pred = {}
        attente = []  #file d'attente
        attente.append(sommet_depart)
        
        while len(attente) > 0:
            courant = attente.pop(0) #sommet dont on va chercher les voisins
            
            #chercher les voisins de courant
            voisins_possibles = [(courant[0]+1,courant[1]), (courant[0]-1,courant[1]), (courant[0],courant[1]+1), (courant[0],courant[1]-1) ]
            for v in voisins_possibles:
                if niveau[v[1]][v[0]] == ' ' : #si c'est une case vide
                    if v not in distance :  #si v est encore inconnu
                        # dans ce cas v est une case voisine vide et inconnue
                        distance[v] = distance[courant] + 1
                        pred[v] = courant
                        attente.append(v)  #v devra devenir courant plus tard
        return distance, pred
    
    def chemin(self, arrivée, départ, pred):
        """
        Donne une liste dans l'ordre des positions à effectués pour atteindre un chemin vers un point donné
        
        Args:
            arrivée (tuple) : destination / point que l'on souhaite atteindre
            départ (tuple) : Notre point de départ
            pred (dict) : Position se situant avant une autre par rapport au point de départ

        Return:
            chemin (list) : Contient dans l'ordre (du départ à l'arrivée) les positions à emprunter
        """
        chemin = []
        while arrivée != départ:
            chemin.append(arrivée)
            arrivée = pred[arrivée]
        chemin.append(départ)
        chemin.reverse()
        return chemin

    def voisin_bomber(self, x, y, dirx=1, diry=0, s=0):
        """
        Récupère les positions autour de la position du bomber.

        Args:
            x (int) : position x du bomber
            y (int) : position y du bomber
            dirx (int) : direction x a vérifier, par défaut sur 1
            diry (int) : direction y a vérifier, par défaut sur 0
            s (int) : nombre de direction vérifiées, par défaut sur 0

        Return:
            positions (list) : retourne quatres positions (les quatres positions voisines)
        """
        voisin = (x + dirx, y + diry) # On ajoute par défaut la position à droite du bomber
        if s == 4: # Quand toutes les directions ont été testés on arrête la fonction
            return []
        return [voisin] + self.voisin_bomber(x, y, -diry, dirx, s+1) # On effectue un appel récursive pour tester la fonction dans toutes les directions
    

##############################################################################################
#                                   ACTION LIE AUX MURS                                      #
##############################################################################################


    def pos_mur(self, carte, x=0, y=0, positions=None):
        """
        Fonction récursive pour obtenir la position des murs.

        Args:
            carte (list) : Liste contenant des sous-listes, chacune représentant une ligne de la carte du jeu.
            x (int) : Position actuelle x (initialisée à 0).
            y (int) : Position actuelle y (initialisée à 0).
            positions (list) : Liste accumulant les positions des murs (initialisée à None).

        Returns:
            positions (list) : Liste contenant la position des murs sous la forme (x, y).
        """
        if positions is None:
            positions = []

        if not carte:  # Si la carte est vide, retourner les positions accumulées
            return positions

        ligne = carte[0]  # Récupérer la première ligne
        for i, lettre in enumerate(ligne):
            if lettre == "M": # Si la lettre est un mur, on ajoute sa position
                positions.append((x + i, y))

        # Appeler récursivement pour les lignes restantes
        return self.pos_mur(carte[1:], x, y + 1, positions)

    def mur_est_voisin(self, pos_voisines):
        """
        Détermine si le mur est voisin du joueur ou non.

        Args:
            pos_voisines (list) : Liste contenant les positions voisines du joueur

        Returns:
            positions_des_murs (list) : liste des murs voisins au joueur
        """
        positions_des_murs = []
        for position in pos_voisines:
            if position in self.position_murs: # Si la position voisine correspond à la position d'un mur on l'enregistre
                positions_des_murs += [position]
        return positions_des_murs
    
    def mur_plus_proche(self, carte, pos_mur, pos_bomber):
        """
        Renvoie les coordonnées du mur le plus proche du bomber.

        Args:
            carte (list) : carte du jeu
            pos_mur (list) : liste contenant les coordonées de tout les murs de la carte.
            pos_bomber (tuple) : coordonées du bomber.

        Return:
            voisin_mur_proche (tuple) : coordonées du mur le plus proche du joueur.
        """
        mur_accessible = []
        accessible, pred = self.parcours_largeur(carte, pos_bomber)
        voisin_mur = {}
        for mur in pos_mur:
            voisin_mur[mur] = self.voisin_bomber(mur[0], mur[1]) # On enregistre toutes les positions voisines de chaque murs
        for pos in pos_mur:
            for voisin in voisin_mur[pos]:
                if voisin in accessible: # On vérifie si une position voisine du mur est accessible
                    mur_accessible.append(voisin)
        if mur_accessible == []:
            return pos_bomber   # Si jamais aucun mur n'est accessible, on renvoie la position du joueur
                                # Il ne bougera donc pas et c'est naze, mais ça évite au jeu de crash
        voisin_mur_proche = mur_accessible[0]
        for voisin_mur in mur_accessible:
            if accessible[voisin_mur] < accessible[voisin_mur_proche]: # On cherche quel position voisine ET accessible est la plus proche
                voisin_mur_proche = voisin_mur
        return voisin_mur_proche # Accès à un mur avec la distance au joueur la plus petite


############################################################################################
#                               DETECTION D'UN DANGER                                      #
############################################################################################


    def bombe_est_proche(self, pos_bombes, accessible):
        """
        Indique si une bombe est proche.

        Args:
            pos_bombes (list) : Positions des bombes
            accessible (dict) : Positions acccessible par le joueur
        
        Return:
            bool, bombe (tuple) : Booléen indiquant si une bombe est proche et sa position (None si False)
        """
        for bombe in pos_bombes:
            if bombe in accessible and accessible[bombe] < 4:
                return True, bombe
        return False, None

    def ennemis_est_proche(self, case_accessible, pos_ennemi, distance_proximite):
        """
        Détermine si un ennemi est à proximité du joueur

        Args:
            case_accessible (dict) : dictionnaire des cases que le joueur peut atteindre
            pos_ennemi (list) : positions de tout les ennemis de la carte
            distance_proximite (int) : Distance maximale à partir de laquelle on déclare l'ennemi comme "proche"

        Return:
            bool : Vrai si un ennemi est proche, faux sinon
        """
        for position in pos_ennemi:
            if position in case_accessible and case_accessible[position] < distance_proximite:
                return True
        return False


############################################################################################
#                       COMPORTEMENT FACE À UN DANGER                                      #
############################################################################################


    def pieger_ennemis(self, pos_player, ennemis, accessible):
        """
        Pose une bombe si le fantôme est proche et sur la même ligne (ou la même colonne)

        Args:
            pos_player (tuple) : Position du joueur
            ennemis (list) : Positions des ennemis
            accessible (dict) : Positions accessibles par le joueur

        Return:
            bool : Si vrai, on pose une bombe
        """
        pos_ennemis_proche = []
        for e in ennemis:
            if e in accessible and accessible[e] < 5:
                pos_ennemis_proche.append(e)
        for ennemi in pos_ennemis_proche:
            if (pos_player[0] == ennemi[0] or pos_player[1] == ennemi[1]):
                return True
        return False
            
    def eviter_ennemis(self, pos_ennemis, pos_player, carte):
        """
        Cherche à éviter les ennemis (autres joueurs et fantômes)
        
        Args:
            pos_ennemis (list) : Positions des ennemis
            pos_player (tuple) : Position du joueur
            carte (list) : Carte du jeu
        
        Return:
            meilleur_case (tuple) : Case permettant le mieux de se tenir à distance d'un ennemi
        """
        # Trouver le fantôme le plus proche
        ennemi_proche = pos_ennemis[0]
        distance_min = abs(pos_player[0] - ennemi_proche[0]) + abs(pos_player[1] - ennemi_proche[1])
        
        for ennemi in pos_ennemis:
            pos_ennemi = (ennemi[0], ennemi[1])
            distance = abs(pos_player[0] - pos_ennemi[0]) + abs(pos_player[1] - pos_ennemi[1])
            if distance < distance_min:
                distance_min = distance
                ennemi_proche = pos_ennemi
        
        # Obtenir les cases accessibles et leurs distances
        cases_accessibles, pred = self.parcours_largeur(carte, pos_player)
        
        # Filtrer les cases adjacentes (distance = 1)
        cases_adjacentes = [pos for pos, dist in cases_accessibles.items() if dist == 1]
        
        # Choisir la case qui maximise la distance avec le fantôme
        meilleure_case = None
        meilleure_distance = -1
        
        for case in cases_adjacentes:
            distance_ennemi = abs(case[0] - ennemi_proche[0]) + abs(case[1] - ennemi_proche[1])
            if distance_ennemi > meilleure_distance:
                meilleure_distance = distance_ennemi
                meilleure_case = case
                
        return meilleure_case

    def refuge(self, case_accessible, pos_bombe, portée, pos_joueur):
        """
        Renvoie la case à l'abris d'une bombe la plus proche de nous

        Args:
            case_accessible (dict) : case accessible par le joueur
            pos_joueur (tuple) : position du joueur
            portée (int) : portée de chaque bombe
        
        Return:
            best_refuge (tuple) : Case proche considérer comme à l'abris 
        """
        refuges = []
        for case in case_accessible:
            if case[0] != pos_bombe[0] and case[1] != pos_bombe[1]:
                refuges.append(case)

        # S'il n'y a aucun échappatoire sur une ligne et une colonne différentes
        if refuges == []:
            for case in case_accessible.items():
                if case[1] > portée:
                    refuges.append(case[0])
            # S'il n'y a vraiment aucun échappatoire (rip)
            if len(refuges) == 0:
                return pos_joueur
            best_refuge = refuges[0]
            for pos in refuges:
                if case_accessible[pos] > case_accessible[best_refuge]:
                    best_refuge = pos
        else:
            best_refuge = refuges[0]
            for pos in refuges:
                if case_accessible[pos] < case_accessible[best_refuge]:
                    best_refuge = pos
        return best_refuge         
    

############################################################################################
#                                 EXECUTION DE L'IA                                        #
############################################################################################ 


    def action(self, game_dict : dict) -> str:
        """Appelé à chaque décision du joueur IA

        Args:
            game_dict (dict) : décrit l'état actuel de la partie au moment où le joueur doit décider son action

        Returns:
            str : une action 
        """

        # On définit les variables dont on a besoin
        self.carte = game_dict['map'] # On redéfinit la variable carte pour qu'elle soit à jour
        self.position_murs = self.pos_mur(self.carte)
        bombers = game_dict['bombers'] # On récupère les valeurs concernant les bomber
        pos_joueur = ()
        pos_autre_joueurs = []
    
        pos_joueur = bombers[self.num_joueur]['position'] # On récupère précisément la position du bomber

        for joueurs in range(len(bombers)):
            if joueurs != self.num_joueur:
                pos_autre_joueurs.append(bombers[joueurs]['position']) # On sauvegarde la position des autres joueurs du jeu

        case_accessible, case_pred = self.parcours_largeur(self.carte, pos_joueur)
        pos_voisines_bomber = self.voisin_bomber(pos_joueur[0], pos_joueur[1])
        pos_mur_à_éliminer = self.mur_est_voisin(pos_voisines_bomber) # Récupère la position des murs voisins

        # On récupère les positions des bombes
        pos_bombes = []
        for bombes in game_dict['bombes']:
            pos_bombes.append(bombes['position'])

        # On récupère les positions des fantômes
        pos_fantomes = []
        for fantomes in game_dict['fantômes']:
            pos_fantomes.append(fantomes['position'])

        # Si un fantome est à proximité
        if self.ennemis_est_proche(case_accessible, pos_fantomes, 5):
            if self.pieger_ennemis(pos_joueur, pos_fantomes, case_accessible) and not self.bombe_est_proche(pos_bombes, case_accessible)[0]:
                return 'X'
            else:
                meilleur_case = self.eviter_ennemis(pos_fantomes, pos_joueur, self.carte)
                choix_case = self.mouvement(meilleur_case, pos_joueur)
                return choix_case
            
        # Si un joueur adverse est à proximité    
        if self.ennemis_est_proche(case_accessible, pos_autre_joueurs, 2):
            if self.pieger_ennemis(pos_joueur, pos_autre_joueurs, case_accessible) and not self.bombe_est_proche(pos_bombes, case_accessible)[0]:
                return 'X'
            else :
                meilleur_case = self.eviter_ennemis(pos_autre_joueurs, pos_joueur, self.carte)
                choix_case = self.mouvement(meilleur_case, pos_joueur)
                return choix_case
            
        # Cas où une bombe est proche du joueur                        
        if self.bombe_est_proche(pos_bombes, case_accessible)[0]:
            range_bombe = game_dict['bombes'][0]['portée']
            bombe_proche = self.bombe_est_proche(pos_bombes, case_accessible)[1]
            choix_case = self.refuge(case_accessible, bombe_proche, range_bombe, pos_joueur)
            prochaine_case = self.chemin(choix_case, pos_joueur, case_pred)
            if len(prochaine_case) > 1:
                choix_action = self.mouvement(prochaine_case[1], pos_joueur)
            else:
                choix_action = 'N'
      
         # Si un mur est voisin           
        elif pos_mur_à_éliminer != []:
            choix_action = 'X'
        
        # S'il reste des murs à éliminer
        elif self.position_murs != []: 
            case_accessible, case_pred = self.parcours_largeur(self.carte, pos_joueur)
            murLePlusProche = self.mur_plus_proche(self.carte, self.position_murs, pos_joueur)
            chemin_mur = self.chemin(murLePlusProche, pos_joueur, case_pred)
            if len(chemin_mur) > 1:
                choix_action = self.mouvement(chemin_mur[1], pos_joueur)
            else:
                choix_action = self.mouvement(chemin_mur[0], pos_joueur)
        
        # S'il n'y a plus de murs, ni de fantômes, ni de joueurs adverses (n'arrivera sûrement jamais mais prévoir au cas où)
        else: 
            actions = ['D', 'G', 'H', 'B']
            choix_action = random.choice(actions)

        return choix_action