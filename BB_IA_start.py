import BB_modele
from typing import Literal
import importlib
import os
import sys


def charger_IAs(noms_des_joueurs : list[str], game : BB_modele.Game):
    """Charge les objets IA contenus dans les fichiers (noms des joueurs) donnés
    
    Args:
        player_names ([str]): noms des joueurs
    Returns:
        list : liste des objet IAs par chaque indice de joueur
    """

    list_ia = []

    for i in range(len(noms_des_joueurs)):
        imp = importlib.import_module("IA." + noms_des_joueurs[i])
        list_ia.append(imp.IA_Bomber(i, game.to_dict(), game.timerglobal, game.timerfantôme ) )

    return list_ia
        

        


def partie(noms_des_joueurs : list[str], scenario : str):
    """
    Simule une partie du jeu BomberBUT

    Args:
        joueurs ([str]) : liste contenant les noms des joueurs i.e. les noms des fichiers contenant les IA
            (on peut mettre plusieurs fois le même nom)
        scenario : nom du fichier contenant la map de départ
    Returns:
        historique (str) : historique complet de la partie
        scores (list) : liste des scores des joueurs en fin de partie
    """

    game = BB_modele.charger_scenario(scenario)
    nb_joueurs = len(noms_des_joueurs)
    assert nb_joueurs == len(game.bombers)
    
    IAs = charger_IAs(noms_des_joueurs, game)
    
    game_over = False
    
    while not game_over:

        game.log("début_tour " + str(game.compteur_tour))        
        #phase joueurs
        for j in range(nb_joueurs):
            original_stdout = sys.stdout
            sys.stdout = open(os.devnull, 'w')
            action = IAs[j].action(game.to_dict())
            sys.stdout = original_stdout
            game.résoudre_action(j,action)

        #phase non joueur
        game.phase_non_joueur()

        #test game over
        game_over = game.is_game_over() 

    total_score = 0
    if type(game.scores) == list:
        for i in range(len(game.scores)):
            total_score += game.scores[i]
        game.log(f"total_score {total_score}")
    game.log("game_over")
    game.log(f"scores {game.scores}")

if __name__ == '__main__':
    partie(['IA_FIRST_TEST'], "maps/training4.txt")
    # partie(['IA_FIRST_TEST','IA_FIRST_TEST','IA_FIRST_TEST','IA_FIRST_TEST'], "maps/battle0.txt")
    