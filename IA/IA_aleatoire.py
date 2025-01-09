##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random

class IA_Bomber:
    def __init__(self, num_joueur : int, game_dic : dict, timerglobal : int, timerfantôme: int) -> None:
        """génère l'objet de la classe IA_Bomber

        Args:
            num_joueur (int): numéro de joueur attribué à l'IA
            game_dic (dict): descriptif de l'état initial de la partie
        """

    #TODO
    pass


    def action(self, game_dict : dict) -> str:
        """Appelé à chaque décision du joueur IA

        Args:
            game_dict (dict) : décrit l'état actuel de la partie au moment
            où le joueur doit décider son action

        Returns:
            str : une action 
        """

        #############################################################
        #ICI il FAUT compléter/remplacer et faire votre version !   #
        #############################################################

        #exemple d'IA basique
        #ici pour prescrire une suite d'actions fixes au début si on veut
        t = game_dict['compteur_tour']
        suite = ['D','D','D','X','G','G','G']
        if t < len(suite):
            return suite[t]

        #puis choisir des actions au hasard
        actions = ['D', 'G', 'H', 'B','X','N']
        return random.choice(actions)


