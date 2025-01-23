##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################

import random
import numpy as np
from typing import Tuple
from .genetic_manager import GeneticManager

class IA_Bomber:
    def __init__(self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int) -> None:
        self.num_joueur = num_joueur
        self.actions = ["H", "B", "G", "D", "X", "N"]
        
        # Charger les gènes depuis le fichier
        genetic_manager = GeneticManager()
        genes = genetic_manager.load_best_genes("best_genes.json")  # Spécifier le fichier explicitement
        
        if genes is None:
            raise Exception("Fichier best_genes.json non trouvé! L'IA doit d'abord être entraînée.")
        
        # Utiliser les paramètres optimisés
        self.learning_rate = genes['learning_rate']
        self.discount_factor = genes['discount_factor']
        self.epsilon = 0.05  # Réduire l'exploration en production
        self.weights = genes['weights']
        
        self.q_table = {}
        self.last_state = None
        self.last_action = None
        self.previous_score = 0
        self.total_reward = 0  # Pour l'évaluation génétique

    def get_state(self, game_dict: dict) -> Tuple:
        """Convertit l'état du jeu en une représentation simplifiée"""
        my_bomber = game_dict["bombers"][self.num_joueur]
        pos = my_bomber["position"]
        
        # Créer une vue locale 3x3 autour du bomber
        local_view = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                y = pos[1] + dy
                x = pos[0] + dx
                if 0 <= y < len(game_dict["map"]) and 0 <= x < len(game_dict["map"][0]):
                    cell = game_dict["map"][y][x]
                else:
                    cell = "C"  # Traiter les bords comme des murs
                local_view.append(cell)

        # Inclure des informations importantes
        state = (
            tuple(local_view),  # Vue locale
            my_bomber["pv"],    # Points de vie
            len([b for b in game_dict["bombes"] if b["position"] == pos]),  # Bombe sur la position
            min([abs(f["position"][0] - pos[0]) + abs(f["position"][1] - pos[1]) 
                for f in game_dict["fantômes"]] if game_dict["fantômes"] else [10])  # Distance au fantôme le plus proche
        )
        return state

    def get_reward(self, game_dict: dict) -> float:
        """Calcule la récompense basée sur l'état du jeu"""
        current_score = game_dict["scores"][self.num_joueur]
        score_reward = (current_score - self.previous_score) * self.weights['score']
        self.previous_score = current_score

        my_bomber = game_dict["bombers"][self.num_joueur]
        
        # Récompense de base pour être en vie
        base_reward = 0.1
        
        # Récompense de survie
        survival_reward = self.weights['survival'] if my_bomber["pv"] > 0 else -10
        
        # Récompense pour l'exploration
        local_view = self.get_state(game_dict)[0]
        exploration_reward = 0.2 if " " in local_view else 0  # Récompense pour les cases vides accessibles
        
        # Récompense distance aux fantômes (modifiée)
        ghost_distances = []
        for ghost in game_dict["fantômes"]:
            dx = abs(ghost["position"][0] - my_bomber["position"][0])
            dy = abs(ghost["position"][1] - my_bomber["position"][1])
            dist = dx + dy
            ghost_distances.append(dist)
        
        # Plus de récompense quand on est loin des fantômes
        ghost_reward = min(ghost_distances) * self.weights['ghost_distance'] if ghost_distances else 5
        
        # Récompense power-up (augmentée)
        powerup_reward = self.weights['powerup'] * 2 if "U" in local_view else 0
        
        total_reward = base_reward + score_reward + survival_reward + ghost_reward + powerup_reward + exploration_reward
        self.total_reward += total_reward
        return total_reward

    def update_q_value(self, state, action, reward, next_state):
        """Met à jour la valeur Q pour une paire état-action"""
        if state not in self.q_table:
            self.q_table[state] = {a: 0 for a in self.actions}
            
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0 for a in self.actions}

        # Formule Q-learning
        old_value = self.q_table[state][action]
        next_max = max(self.q_table[next_state].values())
        new_value = (1 - self.learning_rate) * old_value + \
                   self.learning_rate * (reward + self.discount_factor * next_max)
        self.q_table[state][action] = new_value

    def action(self, game_dict: dict) -> str:
        current_state = self.get_state(game_dict)
        
        # Apprentissage de l'action précédente
        if self.last_state is not None:
            reward = self.get_reward(game_dict)
            self.update_q_value(self.last_state, self.last_action, reward, current_state)

        # Sélection de la nouvelle action (epsilon-greedy)
        if current_state not in self.q_table:
            self.q_table[current_state] = {a: 0 for a in self.actions}

        if random.random() < self.epsilon:
            # Exploration : action aléatoire
            action = random.choice(self.actions)
        else:
            # Exploitation : meilleure action connue
            action = max(self.q_table[current_state].items(), key=lambda x: x[1])[0]

        self.last_state = current_state
        self.last_action = action
        return action

    def get_fitness(self) -> float:
        """Retourne la performance de l'IA pour l'évolution génétique"""
        return self.total_reward
