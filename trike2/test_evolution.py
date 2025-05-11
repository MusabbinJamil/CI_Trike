from trike_ai.training.evolutionary_optimizer import evolve_hybrid_ai

# Run with minimal configuration
evolve_hybrid_ai(
    population_size=4,      # Reduced from default 10
    generations=2,          # Reduced from default 5
    board_size=5,           # Smaller board for faster games
    num_rounds=1,           # Just one round per matchup
    verbose=True            # See what's happening
)