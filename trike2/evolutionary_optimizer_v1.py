import subprocess
import random
import json
import os
import time
import argparse
from typing import List, Dict, Tuple, Any
import numpy as np

class Individual:
    """Represents a set of HybridAI parameters"""
    
    def __init__(self, minimax_weight=None, mcts_weight=None, random_weight=None):
        """
        Initialize with either provided weights or random weights
        that sum to 100
        """
        if minimax_weight is None or mcts_weight is None or random_weight is None:
            # Generate random weights that sum to 100
            minimax_weight = random.randint(20, 70)
            mcts_weight = random.randint(20, 100 - minimax_weight)
            random_weight = 100 - minimax_weight - mcts_weight
        
        self.minimax_weight = minimax_weight
        self.mcts_weight = mcts_weight
        self.random_weight = random_weight
        self.fitness = 0
        self.games_played = 0
        self.games_won = 0
    
    def __str__(self):
        return f"HybridAI({self.minimax_weight}-{self.mcts_weight}-{self.random_weight})"
    
    def get_name(self):
        """Generate a name representing the parameters"""
        return f"Hybrid_{self.minimax_weight}{self.mcts_weight}{self.random_weight}"
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "minimax_weight": self.minimax_weight,
            "mcts_weight": self.mcts_weight,
            "random_weight": self.random_weight,
            "fitness": self.fitness,
            "games_played": self.games_played,
            "games_won": self.games_won
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Individual from dictionary data"""
        ind = cls(
            minimax_weight=data["minimax_weight"],
            mcts_weight=data["mcts_weight"],
            random_weight=data["random_weight"]
        )
        ind.fitness = data.get("fitness", 0)
        ind.games_played = data.get("games_played", 0)
        ind.games_won = data.get("games_won", 0)
        return ind

class EvolutionaryOptimizer:
    """Evolutionary algorithm to optimize HybridAI parameters"""
    
    def __init__(self, 
                 population_size=10, 
                 generations=5, 
                 tournament_size=3,
                 crossover_rate=0.7,
                 mutation_rate=0.2,
                 mutation_amount=10,
                 games_per_match=3,
                 board_size=9,
                 output_dir="evolution_results",
                 headless=True):
        """
        Initialize the evolutionary algorithm
        
        Args:
            population_size: Number of individuals in population
            generations: Number of generations to run
            tournament_size: Size of tournament for selection
            crossover_rate: Probability of crossover
            mutation_rate: Probability of mutation
            mutation_amount: Maximum amount to mutate by
            games_per_match: Number of games per match between opponents
            board_size: Size of game board
            output_dir: Directory to store results
            headless: Whether to run games without GUI
        """
        self.population_size = population_size
        self.generations = generations
        self.tournament_size = tournament_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.mutation_amount = mutation_amount
        self.games_per_match = games_per_match
        self.board_size = board_size
        self.output_dir = output_dir
        self.headless = headless
        
        self.population = []
        self.hall_of_fame = []
        self.generation_results = []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
    def initialize_population(self):
        """Generate initial random population"""
        self.population = [Individual() for _ in range(self.population_size)]
        
    def run_game(self, player1: Individual, player2: Individual) -> Tuple[str, int, int]:
        """
        Run a single game between two individuals
        
        Returns:
            Tuple of (winner_name, player1_score, player2_score)
        """
        scores_file = "trike_scores.json"
        
        # Back up existing scores file if it exists
        if os.path.exists(scores_file):
            backup_file = f"trike_scores_backup_{int(time.time())}.json"
            os.rename(scores_file, backup_file)
        
        # Construct command with arguments for both players
        player1_name = player1.get_name()
        player2_name = player2.get_name()
        
        cmd = [
            "python", "-m", "src.guiv2", 
            "--board_size", str(self.board_size),
            "--player1_name", player1_name,
            "--player1_ai", "HybridAI",
            "--player1_minimax_weight", str(player1.minimax_weight),
            "--player1_mcts_weight", str(player1.mcts_weight),
            "--player1_random_weight", str(player1.random_weight),
            "--player2_name", player2_name,
            "--player2_ai", "HybridAI",
            "--player2_minimax_weight", str(player2.minimax_weight),
            "--player2_mcts_weight", str(player2.mcts_weight),
            "--player2_random_weight", str(player2.random_weight),
            "--auto_play", "True",  # Add this flag to make games auto-play
            "--close_when_done", "True"  # Add this flag to auto-close when game ends
        ]
        
        if self.headless:
            cmd.append("--headless")
        
        print(f"Running game: {player1_name} vs {player2_name}")
        
        try:
            # Run the game with a timeout to prevent hanging
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
            
            # Parse the scores file to determine winner and scores
            time.sleep(1)  # Give a moment for scores file to be written
            
            if os.path.exists(scores_file):
                with open(scores_file, 'r') as f:
                    scores = json.load(f)
                
                player1_score = scores.get(player1_name, 0)
                player2_score = scores.get(player2_name, 0)
                
                if player1_score > player2_score:
                    winner = player1_name
                elif player2_score > player1_score:
                    winner = player2_name
                else:
                    winner = "Draw"
                    
                return winner, player1_score, player2_score
            else:
                print("Score file not found after game completion")
                return "Error", 0, 0
                
        except subprocess.TimeoutExpired:
            print("Game timed out - killing process and continuing")
            return "Timeout", 0, 0
        except Exception as e:
            print(f"Error running game: {e}")
            return "Error", 0, 0
    
    def run_tournament(self):
        """Run tournament between all individuals in population"""
        results = []
        
        # Make each individual play against several others
        for i, player1 in enumerate(self.population):
            # Reset stats for this tournament
            player1.games_played = 0
            player1.games_won = 0
            
            # Play against a subset of other players
            opponents = random.sample(self.population[:i] + self.population[i+1:], 
                                     min(self.tournament_size, len(self.population)-1))
            
            for player2 in opponents:
                for _ in range(self.games_per_match):
                    # Alternate who goes first
                    if _ % 2 == 0:
                        winner, p1_score, p2_score = self.run_game(player1, player2)
                        if winner == player1.get_name():
                            player1.games_won += 1
                    else:
                        winner, p2_score, p1_score = self.run_game(player2, player1)
                        if winner == player1.get_name():
                            player1.games_won += 1
                    
                    player1.games_played += 1
                    
                    # Record the result
                    results.append({
                        "player1": player1.get_name(),
                        "player2": player2.get_name(),
                        "winner": winner,
                        "p1_score": p1_score,
                        "p2_score": p2_score
                    })
        
        # Calculate fitness for each individual
        for individual in self.population:
            if individual.games_played > 0:
                individual.fitness = individual.games_won / individual.games_played
            else:
                individual.fitness = 0
        
        return results
    
    def selection(self) -> List[Individual]:
        """
        Tournament selection to pick parents for next generation
        
        Returns:
            Selected individuals
        """
        selected = []
        
        for _ in range(self.population_size):
            # Pick random tournament participants
            tournament = random.sample(self.population, 
                                      min(self.tournament_size, len(self.population)))
            
            # Select winner (individual with highest fitness)
            winner = max(tournament, key=lambda ind: ind.fitness)
            selected.append(winner)
        
        return selected
    
    def crossover(self, parent1: Individual, parent2: Individual) -> Tuple[Individual, Individual]:
        """
        Perform crossover between two parents
        
        Returns:
            Two new offspring
        """
        if random.random() > self.crossover_rate:
            # No crossover, return copies of parents
            return Individual(parent1.minimax_weight, parent1.mcts_weight, parent1.random_weight), \
                   Individual(parent2.minimax_weight, parent2.mcts_weight, parent2.random_weight)
        
        # Single-point crossover - use minimax weight as crossover point
        child1 = Individual(parent1.minimax_weight, parent2.mcts_weight, parent2.random_weight)
        child2 = Individual(parent2.minimax_weight, parent1.mcts_weight, parent1.random_weight)
        
        # Normalize weights to ensure they sum to 100
        self._normalize_weights(child1)
        self._normalize_weights(child2)
        
        return child1, child2
    
    def mutation(self, individual: Individual) -> Individual:
        """
        Apply mutation to an individual
        
        Returns:
            Mutated individual
        """
        # Decide if we should mutate
        if random.random() > self.mutation_rate:
            return individual
        
        # Choose which weight(s) to mutate
        weights_to_mutate = random.sample(['minimax', 'mcts', 'random'], 
                                         random.randint(1, 2))  # Mutate 1 or 2 weights
        
        # Apply mutation
        for weight in weights_to_mutate:
            if weight == 'minimax':
                individual.minimax_weight += random.randint(-self.mutation_amount, self.mutation_amount)
            elif weight == 'mcts':
                individual.mcts_weight += random.randint(-self.mutation_amount, self.mutation_amount)
            elif weight == 'random':
                individual.random_weight += random.randint(-self.mutation_amount, self.mutation_amount)
        
        # Normalize weights to ensure they sum to 100
        self._normalize_weights(individual)
        
        return individual
    
    def _normalize_weights(self, individual: Individual):
        """Ensure weights are positive and sum to 100"""
        # Ensure all weights are at least 5%
        individual.minimax_weight = max(5, individual.minimax_weight)
        individual.mcts_weight = max(5, individual.mcts_weight)
        individual.random_weight = max(5, individual.random_weight)
        
        # Normalize to sum to 100
        total = individual.minimax_weight + individual.mcts_weight + individual.random_weight
        individual.minimax_weight = int((individual.minimax_weight / total) * 100)
        individual.mcts_weight = int((individual.mcts_weight / total) * 100)
        individual.random_weight = 100 - individual.minimax_weight - individual.mcts_weight
    
    def evolve(self):
        """Run the evolutionary algorithm"""
        print("Starting evolutionary optimization...")
        print(f"Population size: {self.population_size}, Generations: {self.generations}")
        
        # Initialize population
        self.initialize_population()
        
        for generation in range(self.generations):
            print(f"\nGeneration {generation+1}/{self.generations}")
            
            # Run tournament
            tournament_results = self.run_tournament()
            
            # Print current population fitness
            self.population.sort(key=lambda ind: ind.fitness, reverse=True)
            print("\nCurrent Population:")
            for i, ind in enumerate(self.population):
                print(f"  {i+1}. {ind} - Fitness: {ind.fitness:.3f} ({ind.games_won}/{ind.games_played})")
            
            # Add best individual to hall of fame
            best_individual = max(self.population, key=lambda ind: ind.fitness)
            self.hall_of_fame.append(best_individual)
            
            # Store generation results
            gen_result = {
                "generation": generation + 1,
                "best_fitness": best_individual.fitness,
                "best_individual": best_individual.to_dict(),
                "population": [ind.to_dict() for ind in self.population],
                "tournament_results": tournament_results
            }
            self.generation_results.append(gen_result)
            
            # Save progress so far
            self._save_results()
            
            if generation < self.generations - 1:
                # Select parents
                parents = self.selection()
                
                # Create new population through crossover and mutation
                new_population = []
                while len(new_population) < self.population_size:
                    parent1, parent2 = random.sample(parents, 2)
                    child1, child2 = self.crossover(parent1, parent2)
                    
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    
                    new_population.append(child1)
                    if len(new_population) < self.population_size:
                        new_population.append(child2)
                
                self.population = new_population
        
        # Final results
        print("\nEvolution complete!")
        print("\nHall of Fame (Best from each generation):")
        for i, ind in enumerate(self.hall_of_fame):
            print(f"  Gen {i+1}: {ind} - Fitness: {ind.fitness:.3f}")
        
        best_ever = max(self.hall_of_fame, key=lambda ind: ind.fitness)
        print(f"\nBest configuration found: {best_ever}")
        print(f"  Minimax Weight: {best_ever.minimax_weight}")
        print(f"  MCTS Weight: {best_ever.mcts_weight}")
        print(f"  Random Weight: {best_ever.random_weight}")
        print(f"  Fitness: {best_ever.fitness:.3f}")
    
    def _save_results(self):
        """Save results to JSON file"""
        results = {
            "parameters": {
                "population_size": self.population_size,
                "generations": self.generations,
                "tournament_size": self.tournament_size,
                "crossover_rate": self.crossover_rate,
                "mutation_rate": self.mutation_rate,
                "mutation_amount": self.mutation_amount,
                "games_per_match": self.games_per_match,
                "board_size": self.board_size
            },
            "hall_of_fame": [ind.to_dict() for ind in self.hall_of_fame],
            "generation_results": self.generation_results
        }
        
        filename = os.path.join(self.output_dir, f"evolution_results_{int(time.time())}.json")
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")

        # Also save best player in an easy-to-use format
        best_ever = max(self.hall_of_fame, key=lambda ind: ind.fitness)
        evolved_player = {
            "name": f"Evolved_AI_{int(best_ever.fitness*100)}",
            "minimax_weight": best_ever.minimax_weight,
            "mcts_weight": best_ever.mcts_weight,
            "random_weight": best_ever.random_weight,
            "fitness": best_ever.fitness,
            "generation": len(self.hall_of_fame)
        }
        
        evolved_file = "evolved_players.json"
        try:
            if os.path.exists(evolved_file):
                with open(evolved_file, 'r') as f:
                    players = json.load(f)
            else:
                players = []
                
            # Add new player
            players.append(evolved_player)
            
            # Sort by fitness
            players.sort(key=lambda p: p.get("fitness", 0), reverse=True)
            
            # Keep only top 5 players
            players = players[:5]
            
            with open(evolved_file, 'w') as f:
                json.dump(players, f, indent=2)
                
            print(f"Best player saved to {evolved_file} for use in games")
        except Exception as e:
            print(f"Error saving evolved player: {e}")

def main():
    """Main function to run the evolutionary optimizer"""
    parser = argparse.ArgumentParser(description="Evolve HybridAI parameters for Trike")
    
    parser.add_argument("--population", type=int, default=10,
                        help="Population size (default: 10)")
    parser.add_argument("--generations", type=int, default=5,
                        help="Number of generations (default: 5)")
    parser.add_argument("--tournament_size", type=int, default=3,
                        help="Tournament size for selection (default: 3)")
    parser.add_argument("--crossover_rate", type=float, default=0.7,
                        help="Crossover rate (default: 0.7)")
    parser.add_argument("--mutation_rate", type=float, default=0.2,
                        help="Mutation rate (default: 0.2)")
    parser.add_argument("--games_per_match", type=int, default=2,
                        help="Games per match between opponents (default: 2)")
    parser.add_argument("--board_size", type=int, default=9,
                        help="Board size (default: 9)")
    parser.add_argument("--output_dir", type=str, default="evolution_results",
                        help="Output directory (default: evolution_results)")
    parser.add_argument("--headless", action="store_true",
                        help="Run in headless mode without GUI")
    
    args = parser.parse_args()
    
    optimizer = EvolutionaryOptimizer(
        population_size=args.population,
        generations=args.generations,
        tournament_size=args.tournament_size,
        crossover_rate=args.crossover_rate,
        mutation_rate=args.mutation_rate,
        games_per_match=args.games_per_match,
        board_size=args.board_size,
        output_dir=args.output_dir,
        headless=args.headless
    )
    
    optimizer.evolve()

if __name__ == "__main__":
    main()