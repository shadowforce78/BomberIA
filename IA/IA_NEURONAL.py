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
        self.move_history = []  # Track last 5 positions
        self.stuck_threshold = 3  # Number of repeated positions to consider stuck
        self.last_position = None

    def get_state(self, game_dict: dict) -> Tuple:
        my_bomber = game_dict["bombers"][self.num_joueur]
        pos = my_bomber["position"]
        
        # Get immediate danger from bombs
        danger_zones = set()
        for bomb in game_dict["bombes"]:
            bx, by = bomb["position"]
            for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
                danger_zones.add((bx+dx, by+dy))
        
        # Enhanced local view with danger awareness
        local_view = []
        for dy in [-2, -1, 0, 1, 2]:
            for dx in [-2, -1, 0, 1, 2]:
                y, x = pos[1] + dy, pos[0] + dx
                if (x, y) in danger_zones:
                    cell = "D"  # Danger zone
                elif 0 <= y < len(game_dict["map"]) and 0 <= x < len(game_dict["map"][0]):
                    cell = game_dict["map"][y][x]
                else:
                    cell = "C"
                local_view.append(cell)

        # Calculate minimum distances
        ghost_dist = float('inf')
        powerup_dist = float('inf')
        
        for ghost in game_dict["fantômes"]:
            dist = abs(ghost["position"][0] - pos[0]) + abs(ghost["position"][1] - pos[1])
            ghost_dist = min(ghost_dist, dist)

        state = (
            tuple(local_view),
            my_bomber["pv"],
            1 if (pos[0], pos[1]) in danger_zones else 0,  # Immediate danger
            min(15, ghost_dist)  # Cap ghost distance
        )
        return state

    def get_reward(self, game_dict: dict) -> float:
        current_score = game_dict["scores"][self.num_joueur]
        my_bomber = game_dict["bombers"][self.num_joueur]
        pos = my_bomber["position"]
        
        # Heavy penalty for death
        if my_bomber["pv"] <= 0:
            return -20
        
        # Base rewards
        reward = 0.5  # Survival bonus
        
        # Score improvement reward
        score_diff = current_score - self.previous_score
        reward += score_diff * self.weights['score']
        self.previous_score = current_score
        
        # Ghost avoidance reward
        min_ghost_dist = float('inf')
        for ghost in game_dict["fantômes"]:
            dist = abs(ghost["position"][0] - pos[0]) + abs(ghost["position"][1] - pos[1])
            min_ghost_dist = min(min_ghost_dist, dist)
        
        if min_ghost_dist != float('inf'):
            ghost_reward = min(5, min_ghost_dist) * self.weights['ghost_distance']
            reward += ghost_reward
        
        # Safety reward
        state = self.get_state(game_dict)
        if state[2] == 1:  # In danger zone
            reward -= 2
        
        self.total_reward += reward
        return reward

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

    def is_stuck(self, current_pos):
        """Check if the bomber is stuck in a loop"""
        if len(self.move_history) >= self.stuck_threshold:
            return len(set(self.move_history[-self.stuck_threshold:])) == 1
        return False

    def find_escape_route(self, game_dict: dict, pos):
        """Find safe direction to move"""
        directions = [(0,1), (0,-1), (1,0), (-1,0)]
        safe_moves = []
        
        for dx, dy in directions:
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if 0 <= new_y < len(game_dict["map"]) and 0 <= new_x < len(game_dict["map"][0]):
                cell = game_dict["map"][new_y][new_x]
                if cell == " " and not any(b["position"] == (new_x, new_y) for b in game_dict["bombes"]):
                    safe_moves.append(("D" if dx > 0 else "G" if dx < 0 else "B" if dy > 0 else "H"))
        
        return safe_moves

    def action(self, game_dict: dict) -> str:
        current_state = self.get_state(game_dict)
        my_bomber = game_dict["bombers"][self.num_joueur]
        current_pos = my_bomber["position"]
        
        # Update position history
        if current_pos != self.last_position:
            self.move_history.append(current_pos)
            if len(self.move_history) > 5:
                self.move_history.pop(0)
        self.last_position = current_pos

        # Check for immediate danger
        if current_state[2] == 1:  # In danger zone
            escape_routes = self.find_escape_route(game_dict, current_pos)
            if escape_routes:
                return random.choice(escape_routes)

        # Check if stuck
        if self.is_stuck(current_pos):
            safe_moves = self.find_escape_route(game_dict, current_pos)
            if safe_moves:
                return random.choice(safe_moves)
            return "X"  # Place bomb to clear path if stuck

        # Normal Q-learning behavior
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
