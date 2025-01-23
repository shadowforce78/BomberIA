import random
import json
import os
import numpy as np
from typing import Dict, List

class GeneticManager:
    def __init__(self, population_size: int = 20, generations: int = 100):
        self.population_size = population_size
        self.generations = generations
        self.current_generation = 0
        self.best_genes = None
        self.population: List[Dict] = []
        self.scores_history = []
        
    def create_initial_population(self):
        """Crée la population initiale avec des paramètres aléatoires"""
        self.population = []
        for _ in range(self.population_size):
            genes = {
                'learning_rate': random.uniform(0.15, 0.25),  # Plage optimisée
                'discount_factor': random.uniform(0.85, 0.95),  # Valeurs plus élevées
                'epsilon': random.uniform(0.15, 0.25),  # Plus d'exploration
                'weights': {
                    'score': random.uniform(2.0, 4.0),      # Augmenté
                    'survival': random.uniform(2.0, 4.0),   # Augmenté
                    'ghost_distance': random.uniform(1.5, 3.0),
                    'powerup': random.uniform(1.5, 3.0)
                }
            }
            self.population.append(genes)
    
    def select_parents(self, scores: List[float]) -> List[Dict]:
        """Sélectionne les meilleurs individus pour la reproduction"""
        scores = np.array(scores)
        
        # Si tous les scores sont 0, utiliser une distribution uniforme
        if np.sum(scores) == 0:
            probs = np.ones(len(scores)) / len(scores)
        else:
            # Ajouter un petit epsilon pour éviter la division par 0
            scores = scores + 1e-10
            probs = scores / scores.sum()
        
        # Sélectionner les parents avec une probabilité proportionnelle à leur score
        selected_indices = np.random.choice(
            len(self.population), 
            size=max(len(self.population)//2, 1),  # Au moins 1 parent
            p=probs, 
            replace=False
        )
        return [self.population[i] for i in selected_indices]
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Croise deux parents pour créer un enfant"""
        child = {}
        for key in parent1.keys():
            if isinstance(parent1[key], dict):
                child[key] = {}
                for subkey in parent1[key].keys():
                    if random.random() < 0.5:
                        child[key][subkey] = parent1[key][subkey]
                    else:
                        child[key][subkey] = parent2[key][subkey]
            else:
                if random.random() < 0.5:
                    child[key] = parent1[key]
                else:
                    child[key] = parent2[key]
        return child
    
    def mutate(self, genes: Dict, mutation_rate: float = 0.2) -> Dict:  # Taux augmenté
        """Applique une mutation aléatoire aux gènes"""
        mutated = genes.copy()
        for key in mutated.keys():
            if isinstance(mutated[key], dict):
                for subkey in mutated[key].keys():
                    if random.random() < mutation_rate:
                        # Mutation plus forte
                        mutated[key][subkey] *= random.uniform(0.6, 1.6)
            else:
                if random.random() < mutation_rate:
                    if key == 'learning_rate':
                        mutated[key] = random.uniform(0.15, 0.25)
                    elif key == 'discount_factor':
                        mutated[key] = random.uniform(0.85, 0.95)
                    elif key == 'epsilon':
                        mutated[key] = random.uniform(0.15, 0.25)
        return mutated
    
    def evolve(self, scores: List[float]):
        """Fait évoluer la population vers la génération suivante"""
        # Ajout d'une vérification des scores
        if not scores:
            return  # Ne rien faire si pas de scores
            
        # Convertir en array numpy et normaliser les scores
        scores_array = np.array(scores)
        scores_array = scores_array - np.min(scores_array) + 1  # Assure que tous les scores sont > 0
        
        # Sauvegarder le meilleur individu en utilisant argmax
        best_index = np.argmax(scores_array)
        self.best_genes = self.population[best_index].copy()
        
        # Sélectionner les parents
        parents = self.select_parents(scores_array)
        
        # Créer la nouvelle population
        new_population = [self.best_genes]  # Élitisme
        
        while len(new_population) < self.population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = self.crossover(parent1, parent2)
            child = self.mutate(child)
            new_population.append(child)
        
        self.population = new_population
        self.current_generation += 1
        
    def save_best_genes(self, filename: str = "best_genes.json"):
        """Sauvegarde les meilleurs gènes dans un fichier"""
        if self.best_genes:
            with open(filename, 'w') as f:
                json.dump(self.best_genes, f)
    
    def load_best_genes(self, filename: str = "best_genes.json") -> Dict:
        """Charge les meilleurs gènes depuis un fichier"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return None
