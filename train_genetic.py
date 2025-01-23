from IA.genetic_manager import GeneticManager
from BB_IA_start import partie
import numpy as np

def train_genetic_ai(nb_generations: int = 100, population_size: int = 20):
    genetic_manager = GeneticManager(population_size, nb_generations)
    genetic_manager.create_initial_population()
    best_score = float('-inf')
    
    try:
        for generation in range(nb_generations):
            print(f"\n=== Generation {generation + 1}/{nb_generations} ===")
            scores = []
            
            # Évaluer chaque individu de la population
            for i, genes in enumerate(genetic_manager.population):
                print(f"Évaluation de l'individu {i + 1}/{population_size}")
                
                try:
                    genetic_manager.save_best_genes("temp_genes.json")
                    
                    total_score = 0
                    nb_parties = 10  # Augmenté pour une meilleure évaluation
                    for game_num in range(nb_parties):
                        game_scores = partie(["IA_NEURONAL"], "maps/training0.txt")
                        score = game_scores[0] if game_scores else 0
                        # Bonus pour encourager la survie et l'exploration
                        survival_bonus = 2.0  # Bonus de base pour avoir joué
                        total_score += score + survival_bonus
                    
                    avg_score = total_score / nb_parties
                    scores.append(max(0.5, avg_score))  # Score minimal augmenté
                    
                except Exception as e:
                    print(f"Erreur pendant l'évaluation: {e}")
                    scores.append(0.1)
            
            # Évolution
            try:
                # Convertir scores en array numpy si ce n'est pas déjà le cas
                scores_array = np.array(scores)
                
                # Trouver le meilleur score et son index
                current_best_idx = np.argmax(scores_array)
                current_best = float(scores_array[current_best_idx])  # Convertir en float Python standard
                
                # Stocker les gènes du meilleur individu avant l'évolution
                if current_best > best_score:
                    best_score = current_best
                    best_genes = genetic_manager.population[current_best_idx].copy()
                    genetic_manager.best_genes = best_genes
                    genetic_manager.save_best_genes("best_genes.json")
                
                # Évoluer avec la liste Python standard
                genetic_manager.evolve(scores)  # Pas besoin de conversion, utiliser la liste originale
                
                print(f"Meilleur score de la génération: {current_best}")
                print(f"Score moyen de la génération: {float(np.mean(scores_array))}")
                print(f"Meilleur score global: {best_score}")
                
            except Exception as e:
                print(f"Erreur pendant l'évolution: {e}")
                continue
            
    except KeyboardInterrupt:
        print("\nEntraînement interrompu par l'utilisateur")
        genetic_manager.save_best_genes("best_genes_interrupted.json")

if __name__ == "__main__":
    train_genetic_ai(nb_generations=50, population_size=10)  # Augmenté pour plus d'exploration
