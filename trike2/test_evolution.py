from trike_ai.training.evolutionary_optimizer import evolve_hybrid_ai

# Run with optimized settings for better convergence
evolve_hybrid_ai(
    population_size=20,     # Increased population for more diversity
    generations=25,         # More generations to allow convergence
    board_size=5,          # Keep small board for speed
    num_rounds=3,          # More rounds per matchup for reliable fitness
    tournament_size=4,      # Larger tournament size for better selection
    mutation_rate=0.3,      # Higher mutation rate for more exploration
    crossover_rate=0.8,    # Higher crossover rate for more exploitation
    verbose=True
)