"""
Train strategic AI using evolutionary algorithms.

This script evolves AI agents that learn sophisticated Trike strategies including:
- Early game positioning (center control, corner avoidance, strategic placement)
- Middle game tactics (influence maximization, trap avoidance, region control)
- Late game strategy (corridor control, endpoint manipulation)
- Advanced trap techniques (setting, extending, multiple traps, sacrificing traps)
- Defensive strategies (defusing traps, locking away threats)

The evolutionary process creates a population of AI agents with different strategic
weights, then evolves them through tournament play, crossover, and mutation to
discover optimal strategic combinations.
"""

import argparse
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from trike_ai.training.strategic_evolution import evolve_strategic_ai

def main():
    parser = argparse.ArgumentParser(
        description="Evolve strategic AI for Trike game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test run
  python train_strategic_evolution.py --population 10 --generations 5 --board_size 5
  
  # Full evolution run
  python train_strategic_evolution.py --population 30 --generations 50 --board_size 7
  
  # High mutation rate for exploration
  python train_strategic_evolution.py --mutation_rate 0.4 --crossover_rate 0.6
        """
    )
    
    parser.add_argument("--population", type=int, default=20,
                        help="Population size (default: 20)")
    parser.add_argument("--generations", type=int, default=30,
                        help="Number of generations (default: 30)")
    parser.add_argument("--board_size", type=int, default=7,
                        help="Board size for games (default: 7)")
    parser.add_argument("--rounds", type=int, default=3,
                        help="Rounds per matchup (default: 3)")
    parser.add_argument("--tournament_size", type=int, default=4,
                        help="Tournament selection size (default: 4)")
    parser.add_argument("--mutation_rate", type=float, default=0.25,
                        help="Mutation rate (default: 0.25)")
    parser.add_argument("--crossover_rate", type=float, default=0.8,
                        help="Crossover rate (default: 0.8)")
    parser.add_argument("--quiet", action="store_true",
                        help="Reduce output verbosity")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.population < 4:
        print("Error: Population size must be at least 4")
        return 1
    
    if args.board_size < 3:
        print("Error: Board size must be at least 3")
        return 1
    
    if not (0 <= args.mutation_rate <= 1):
        print("Error: Mutation rate must be between 0 and 1")
        return 1
    
    if not (0 <= args.crossover_rate <= 1):
        print("Error: Crossover rate must be between 0 and 1")
        return 1
    
    print("Strategic AI Evolution for Trike Game")
    print("="*40)
    print()
    print("This will evolve AI agents to learn sophisticated strategies:")
    print("• Early game: Center control, corner avoidance, strategic positioning")
    print("• Middle game: Influence maximization, opponent reduction, trap awareness")
    print("• Late game: Corridor control, endpoint manipulation") 
    print("• Trap strategies: Setting, extending, multiple traps, sacrificing")
    print("• Defense: Defusing traps, locking away threats")
    print()
    
    try:
        # Run evolution
        best_ai, hall_of_fame, results = evolve_strategic_ai(
            population_size=args.population,
            generations=args.generations,
            board_size=args.board_size,
            num_rounds=args.rounds,
            tournament_size=args.tournament_size,
            mutation_rate=args.mutation_rate,
            crossover_rate=args.crossover_rate,
            verbose=not args.quiet
        )
        
        print("\n" + "="*50)
        print("EVOLUTION SUCCESSFUL!")
        print("="*50)
        print(f"Best AI achieved {best_ai.fitness:.1%} win rate")
        print("Strategic weights and full results saved to 'evolved_strategic_players/'")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nEvolution interrupted by user")
        return 1
    except Exception as e:
        print(f"\nError during evolution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())