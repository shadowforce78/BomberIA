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
                    nb_parties = 3
                    for _ in range(nb_parties):
                        game_scores = partie(["IA_NEURONAL"], "maps/training0.txt")
                        total_score += game_scores[0] if game_scores else 0
                    
                    avg_score = total_score / nb_parties
                    scores.append(max(0.1, avg_score))
                    
                except Exception as e:
                    print(f"Erreur pendant l'évaluation: {e}")
                    scores.append(0.1)
            
            # Évolution
            try:
                # Convertir scores en array numpy si ce n'est pas déjà le cas
                scores_array = np.array(scores)
                
                # Utiliser argmax au lieu de index pour trouver le meilleur score
                current_best_idx = np.argmax(scores_array)
                current_best = scores_array[current_best_idx]
                
                genetic_manager.evolve(scores_array.tolist())  # Convertir en liste si nécessaire
                
                if current_best > best_score:
                    best_score = current_best
                    genetic_manager.save_best_genes("best_genes.json")
                
                print(f"Meilleur score de la génération: {current_best}")
                print(f"Score moyen de la génération: {np.mean(scores_array)}")
                print(f"Meilleur score global: {best_score}")
                
            except Exception as e:
                print(f"Erreur pendant l'évolution: {e}")
                continue
            
    except KeyboardInterrupt:
        print("\nEntraînement interrompu par l'utilisateur")
        genetic_manager.save_best_genes("best_genes_interrupted.json")

if __name__ == "__main__":
    train_genetic_ai(nb_generations=500, population_size=100)
