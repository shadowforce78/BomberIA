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
        self.timerfantôme = timerfantôme
        
        # Analyse initiale du dictionnaire
        self.analyze_game_dict(game_dic)

    def analyze_game_dict(self, game_dict: dict) -> None:
        """Analyse le contenu du dictionnaire du jeu"""
        print("\nContenu du dictionnaire game_dict:")
        for key, value in game_dict.items():
            print(f"\nClé: {key}")
            
            # Afficher un exemple de la valeur selon son type
            if isinstance(value, list):
                print(f"Type: Liste de longueur {len(value)}")
                if value:
                    for item in value:
                        print(f"Valeur: {item}")
            else:
                print(f"Valeur: {value}")

    def action(self, game_dict : dict) -> str:
        """Décide de l'action à faire"""
        # Pour l'instant, on analyse juste le dictionnaire à chaque tour
        self.analyze_game_dict(game_dict)
        
        # Action par défaut
        return 'N'

# Les clés attendues dans game_dict sont:
# - 'map': la carte du jeu (liste de strings)
# - 'bombers': liste des informations des bombers
# - 'fantômes': liste des fantômes
# - 'bombes': liste des bombes
# - 'compteur_tour': numéro du tour actuel
# - 'scores': liste des scores des joueurs


