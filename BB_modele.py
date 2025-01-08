from typing import Literal
import random

## CONSTANTES ################################################################

RAPPORT = True
PV_START = 3
TIMER_BOMB = 5

## TYPES BASIQUES ############################################################

Action = Literal['H', 'B', 'G', 'D','X', 'N'] #haut, bas, gauche, droite, bombe, passe
Map = list[list[str]]

class Position:
    """Classe permettant de stocker une position (x,y) sur la carte"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """permet d'ajouter une position à une direction H/B/G/D"""

        if other=='H':
            return Position(self.x,self.y-1)
        elif other=='B':
            return Position(self.x,self.y+1)
        elif other=='G':
            return Position(self.x-1,self.y)
        elif other=='D':
            return Position(self.x+1,self.y)
        else:
            raise Exception()
            

    def __eq__(self, other) -> bool:
        if isinstance(other, Position):
            return self.x==other.x and self.y==other.y
        return False

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self):
        return f'({self.x},{self.y})'

    def to_dict(self):
        return (self.x,self.y)

## CLASSES DE DONNES PRINCIPALES #############################################

class Bomber:
    """stoke les données d'un personnage joueur"""
    def __init__(self, pos : Position, num_joueur: int):
        self.position : Position = pos
        self.niveau : int = 0
        self.pv : int = PV_START #points de vie
        self.num_joueur : int = num_joueur

    def to_dict(self):
        return {'position': self.position.to_dict(),'niveau':self.niveau,'pv':self.pv,'num_joueur': self.num_joueur}

class Fantôme:
    """stocke les données d'un fantôme"""
    def __init__(self, pos : Position):
        self.position : Position = pos
        self.case_précédente : Position | None = None #case du fantôme au tour précédent
        self.pv = 1 

    def __str__(self):
        return f"Fantome en {self.position}, précédemment en {self.case_précédente}"

    def to_dict(self):
        return {'position':self.position.to_dict(),'case prec': self.case_précédente.to_dict() if self.case_précédente else None}

class Bombe:
    """stocke les données d'une bombe posée sur la map"""
    def __init__(self, pos : Position, portée : int, propriétaire : int):
        self.position : Position = pos
        self.timer : int = TIMER_BOMB
        self.portée : int = portée
        self.propriétaire : int = propriétaire # numéro de joueur

    def to_dict(self):
        return {'position':self.position.to_dict(), 'timer':self.timer, 'portée':self.portée, 'proprio':self.propriétaire}

## CLASSE GAME CONTENANT LA LOGIQUE DU JEU

class Game:
    """contient toutes les données et la logique du jeu"""
    def __init__(self, carte: Map, pos_bombers : list[Position], pos_ethernets : list[Position], timerglobal: int, timerfantôme: int ):
        self.carte : Map = carte
        self.hauteur = len(carte)
        self.largeur = len(carte[0])
        self.bombers : list[Bomber] = [Bomber(pos_bombers[i], i) for i in range(len(pos_bombers))]
        self.fantômes : list[Fantôme] = []
        self.bombes : list [Bombe] = []
        self.compteur_tour : int = 0
        self.ethernets : list[Position] = pos_ethernets
        self.bombers_éliminés : bool = False
        self.fantômes_éliminés : bool = False
        self.scores : list[int] = [0]*len(self.bombers)
        self.timerglobal : int = timerglobal
        self.timerfantôme : int = timerfantôme
        self.événements = []
        

    ## UTILITAIRES ###########################################################

    def to_dict(self) -> dict:
        return {'map': ["".join(l) for l in self.carte], 
                'bombers' : [b.to_dict() for b in self.bombers], 
                'fantômes': [f.to_dict() for f in self.fantômes],
                'bombes' : [b.to_dict() for b in self.bombes],
                'compteur_tour': self.compteur_tour,
                'scores' : list(self.scores)}


    def affiche_carte(self):
        for l in self.carte:
            print("".join(l))


    def est_non_bloquant(self, pos: Position) -> bool:
        """Indique si une position est non bloquante

        Args:
            pos (Position): position à tester

        Returns:
            bool: la position est-elle non bloquante ?
        """
        if self.carte[pos.y][pos.x] in ['C', 'M', 'E']:
            return False
        elif pos in [b.position for b in self.bombers]:
            return False
        elif pos in [f.position for f in self.fantômes]:
            return False
        return True

    def log(self, événement : str):
        self.événements.append(événement)
        if RAPPORT:
            print(événement)

    ## GESTION DES BOMBERS ###################################################
            
    def résoudre_action(self, num_joueur : int, action : Action):
        """Résout l'action du bomber de numéro donné en cas de déplacement
        ou de bombe (X)
        """
       
        if action == 'X':
            self.poser_bombe(num_joueur)

        elif action in ['H', 'B', 'G', 'D']:
            self.deplacement_bomber(num_joueur, action)
        

    def poser_bombe(self,num_joueur:int):
        """pose une bombe sur la case du joueur de numéro donné
        s'il est possible de le faire

        Args:
            num_joueur (int): numéro du joueur
        """
        pos = self.bombers[num_joueur].position # case de la bombe

        #condition : il n'y a pas déjà une bombe
        if pos not in [b.position for b in self.bombes]:
            portée = 1 + self.bombers[num_joueur].niveau // 2
            self.bombes.append(Bombe(pos,portée,num_joueur))
            self.log(f"pose_bombe {num_joueur} {pos}")


    def deplacement_bomber(self, num_joueur: int, direction : Action):
        """gestion d'un déplacement de bomber si possible

        Args:
            num_joueur (int): numéro du bomber
            direction (Action): direction du déplacement
        """
        bomber = self.bombers[num_joueur]
        new = bomber.position + direction #nouvelle position

        if self.est_non_bloquant(new):
            self.log(f"b_mouvement {num_joueur} {bomber.position} {new}")
            bomber.position = new

            #ramassage update
            if self.carte[new.y][new.x] == 'U':
                self.carte[new.y][new.x] = ' '
                bomber.niveau +=1
                self.log(f"niveau_plus {bomber.num_joueur}")
                if bomber.niveau %2 == 1:
                    bomber.pv += 1
                    self.log(f"pv_plus {bomber.num_joueur}")
               


    def blesser(self, bomber: Bomber):
        """blessure sur un bomber

        Args:
            bomber (Bomber): le bomber blessé
        """
        bomber.pv -= 1
        self.log(f"blessure {bomber.num_joueur}")
        #test mort de bomber
        if bomber.pv < 0:
            self.bombers_éliminés = True
            self.log(f"b_élimination {bomber.num_joueur}")


    ## GESTION DES FANTOMES ##################################################
    
    def déplacement_fantôme(self, f: Fantôme):
        """gestion du déplacement d'un fantôme
        Args:
            f (Fantôme): le fantôme qui doit se déplacer
        """


        pos : Position = f.position #position de départ
        voisines : list[Position] = [] #destinations possibles
        for d in ['H','B','G','D']:
            v : Position = pos + d
            if self.est_non_bloquant(v):
                voisines.append(v)
        new = None
        if len(voisines)==1: #dans ce cas pas de choix
            new = voisines[0]
        elif len(voisines) > 1: #on tire une position qui ne soit pas la précédente
            new = random.choice(voisines)
            while new == f.case_précédente:
                new = random.choice(voisines)
        if new:
            self.log(f"f_mouvement {f.position} {new}")
            f.position = new
        
        #mise à jour position précédente dans tous les cas
        f.case_précédente = pos     


    def attaque_fantôme(self, f : Fantôme):
        """attaque d'un fantôme sur les cases voisines
        """

        for d in ['H','B','G','D']:
            v = f.position + d
            for b in self.bombers:
                if b.position == v:
                    self.log(f"attaque {b.num_joueur}")
                    self.blesser(b)

 
    def apparition_fantômes(self):
        """Apparition des fantômes près des ethernets
        """
        if self.compteur_tour > 0 and self.compteur_tour % self.timerfantôme == 0:
            for pos in self.ethernets:
                voisines : list[Position] = [] #cases possibles
                for d in ['H','B','G','D']:
                    v = pos + d
                    if self.est_non_bloquant(v):
                        voisines.append(v)
                if voisines:
                    new = random.choice(voisines)
                    f = Fantôme(new)
                    self.fantômes.append(f)
                    self.log(f"apparition {new}" )


    ## FIN DE TOUR ###########################################################

    def update_éliminations(self):
        """suppression des bombers et fantômes éliminés
        """
        if self.bombers_éliminés:
            self.bombers = [b for b in self.bombers if b.pv > 0]
            self.bombers_éliminés = False
        if self.fantômes_éliminés:
            self.fantômes = [f for f in self.fantômes if f.pv >0]
            self.fantômes_éliminés = False


    def update_bombes(self) -> set[Bombe]:
        """Met à jour les compteurs de bombes et renvoie 
        l'ensemble des bombes qui explosent

        Returns:
            set[Bombe]: bombes qui explosent
        """
        for b in self.bombes:
            b.timer -= 1
        explosions = set(b for b in self.bombes if b.timer <= 0)
        return explosions

   
    def explose(self, b: Bombe) -> set[Bombe]:
        """Explosion de la bombe ; renvoie les explosions en chaîne
        

        Args:
            b (Bombe): la bombe qui explose

        Returns:
            _type_: _description_
        """
        self.log(f"explosion_bombe {b.position}")

        self.bombes.remove(b)
        chaîne = set() #contiendra les bombes qui explosent en chaîne


        #calcul des cases qui subissent l'explosion
        cases = [b.position]
        for d in ['H','B','G','D']:
            v = b.position
            for k in range(b.portée):
                v = v + d
                if self.carte[v.y][v.x] != 'C':
                    cases.append(v)
                else:
                    break
        
        #résultat des explosions
        for c in cases:
            if self.carte[c.y][c.x] == 'U':
                self.carte[c.y][c.x] = ' '
                self.log(f"update_explosé {c}")
            elif self.carte[c.y][c.x] == 'M':
                self.carte[c.y][c.x] = ' '
                self.log(f"minerai_explosé {c}")
                #score +1 pour le bomber qui a explosé le minerai
                for bomber in self.bombers:
                    if bomber.num_joueur == b.propriétaire:
                        self.scores[bomber.num_joueur] += 1
                        self.log(f"score {bomber.num_joueur}")
            
                        
            for bomber in self.bombers:
                if bomber.position == c:
                    self.blesser(bomber)

            for f in self.fantômes:
                if f.position == c:
                    f.pv = 0
                    self.log(f"f_éliminé {f.position}")
                    self.carte[c.y][c.x] = 'U'

            #explosions en chaîne        
            for bombe in self.bombes:
                if bombe.position == c:
                    chaîne.add(bombe)

        return chaîne
            
            
    def is_game_over(self):
        return len(self.bombers)==0 or self.compteur_tour == self.timerglobal
    

    ## BOUCLE PRINCIPALE DES ACTIONS

    def phase_non_joueur(self):
        
        #déplacement fantômes
        for f in self.fantômes:
            self.déplacement_fantôme(f)

        #phase attaque des fantômes
        for f in self.fantômes:
            self.attaque_fantôme(f)
        
        #phase apparition fantômes
        self.apparition_fantômes()

        #phase explosion
        explosions = self.update_bombes() #bombes qui doivent exploser
        while explosions:
            chaine = self.explose(explosions.pop())
            explosions.update(chaine)

        #fin de tour
        self.compteur_tour += 1
        self.log("fin_tour\n")

    
def charger_scenario(scenario: str) -> Game:
    
    #chargement de la map des éléments fixes
    with open(scenario) as f:
        l = f.readlines()
        timerglobal = int(l[0].split()[1])
        timerfantome = int(l[1].split()[1])
        carte = [list(s.strip()) for s in l[3:]]

    #chargement des elements mobiles
    positions_bombers = []
    positions_ethernets = []
    for x in range(len(carte[0])):
        for y in range(len(carte)):
            if carte[y][x] == 'P':
                positions_bombers.append(Position(x,y))
                carte[y][x] = ' '
            elif carte[y][x] == 'E':
                positions_ethernets.append(Position(x,y))
    
    return Game(carte, positions_bombers, positions_ethernets, timerglobal, timerfantome)

    

