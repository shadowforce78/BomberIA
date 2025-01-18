from BB_IA_start import partie

IA1 = "IA_PECHINE_PLANQUE"
IA2 = "iawael"
IA3 = "iatheo3"
IA4 = "ianourane"

def run_multiple_simulations(num_simulations=100):
    ia_list = [IA1, IA2, IA3, IA4]
    total_scores = [0] * len(ia_list)
    map_file = "maps/battle0.txt"
    
    print(f"Running {num_simulations} simulations...")
    for i in range(num_simulations):
        if i % 10 == 0:  # Progress indicator
            print(f"Simulation {i}/{num_simulations}")
        scores = partie(ia_list, map_file)
        for j in range(len(scores)):
            total_scores[j] += scores[j]
    
    # Calculate averages
    avg_scores = [score/num_simulations for score in total_scores]
    
    print("\n=== Final Average Scores ===")
    print(f"After {num_simulations} simulations:")
    for i, ia in enumerate([IA1, IA2, IA3, IA4]):
        print(f"{ia}: {avg_scores[i]:.2f} points")
    
    return avg_scores

if __name__ == "__main__":
    run_multiple_simulations(10)