import random
import json
import os
import time
from typing import List, Dict, Tuple, Any
import numpy as np
from trike_ai.agents import HybridAI
from trike_ai.training.runner import run_ai_match
from src.game import Game

class HybridIndividual:
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
        
        # Create the actual HybridAI instance
        self.ai = HybridAI(
            minimax_weight=minimax_weight/100, 
            mcts_weight=mcts_weight/100, 
            random_weight=random_weight/100,
            name=f"Hybrid_{minimax_weight}{mcts_weight}{random_weight}"
        )
    
    def __str__(self):
        return f"HybridAI({self.minimax_weight}-{self.mcts_weight}-{self.random_weight})"
    
    def get_name(self):
        """Generate a name representing the parameters"""
        return self.ai.name
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.ai.name,
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

def run_tournament_generation(population: List[HybridIndividual], board_size: int, num_rounds: int, verbose: bool):
    """Run tournament between individuals in the population"""
    for i, player1 in enumerate(population):
        player1.games_played = 0
        player1.games_won = 0
        
        # Each individual plays against several others
        opponents = random.sample(population[:i] + population[i+1:], 
                                 min(3, len(population)-1))
        
        for player2 in opponents:
            for _ in range(num_rounds):
                # First match: player1 goes first
                print(f"Match: {player1.ai.name} vs {player2.ai.name}")
                result = run_ai_match(player1.ai, player2.ai, board_size=board_size, verbose=verbose)
                
                # Check the format of result
                winner, scores = result
                if winner == player1.ai.name:  # player1 won
                    player1.games_won += 1
                
                player1.games_played += 1
                
                # Second match: player2 goes first (for fairness)
                print(f"Match: {player2.ai.name} vs {player1.ai.name}")
                result = run_ai_match(player2.ai, player1.ai, board_size=board_size, verbose=verbose)
                
                # Check format of result for second match too
                winner, scores = result
                if winner == player1.ai.name:  # player1 won
                    player1.games_won += 1
                
                player1.games_played += 1
    
    # Calculate fitness
    for individual in population:
        if individual.games_played > 0:
            individual.fitness = individual.games_won / individual.games_played
        else:
            individual.fitness = 0
            
    return sorted(population, key=lambda ind: ind.fitness, reverse=True)

def selection(population, tournament_size=3):
    """Tournament selection to pick parents"""
    selected = []
    
    for _ in range(len(population)):
        tournament = random.sample(population, min(tournament_size, len(population)))
        winner = max(tournament, key=lambda ind: ind.fitness)
        selected.append(winner)
    
    return selected

def crossover(parent1, parent2, crossover_rate=0.7):
    """Perform crossover between parents"""
    if random.random() > crossover_rate:
        # No crossover, return copies of parents
        return HybridIndividual(parent1.minimax_weight, parent1.mcts_weight, parent1.random_weight), \
               HybridIndividual(parent2.minimax_weight, parent2.mcts_weight, parent2.random_weight)
    
    # Single-point crossover
    child1 = HybridIndividual(parent1.minimax_weight, parent2.mcts_weight, parent2.random_weight)
    child2 = HybridIndividual(parent2.minimax_weight, parent1.mcts_weight, parent1.random_weight)
    
    # Normalize weights
    normalize_weights(child1)
    normalize_weights(child2)
    
    return child1, child2

def mutation(individual, mutation_rate=0.2, mutation_amount=10):
    """Apply mutation to an individual"""
    if random.random() > mutation_rate:
        return individual
    
    # Choose which weights to mutate
    weights_to_mutate = random.sample(['minimax', 'mcts', 'random'], random.randint(1, 2))
    
    for weight in weights_to_mutate:
        if weight == 'minimax':
            individual.minimax_weight += random.randint(-mutation_amount, mutation_amount)
        elif weight == 'mcts':
            individual.mcts_weight += random.randint(-mutation_amount, mutation_amount)
        else:  # random
            individual.random_weight += random.randint(-mutation_amount, mutation_amount)
    
    # Normalize weights
    normalize_weights(individual)
    
    return individual

def normalize_weights(individual):
    """Ensure weights are positive and sum to 100"""
    individual.minimax_weight = max(5, individual.minimax_weight)
    individual.mcts_weight = max(5, individual.mcts_weight)
    individual.random_weight = max(5, individual.random_weight)
    
    total = individual.minimax_weight + individual.mcts_weight + individual.random_weight
    individual.minimax_weight = int((individual.minimax_weight / total) * 100)
    individual.mcts_weight = int((individual.mcts_weight / total) * 100)
    individual.random_weight = 100 - individual.minimax_weight - individual.mcts_weight
    
    # Update the AI instance
    individual.ai = HybridAI(
        minimax_weight=individual.minimax_weight/100, 
        mcts_weight=individual.mcts_weight/100, 
        random_weight=individual.random_weight/100,
        name=f"Hybrid_{individual.minimax_weight}{individual.mcts_weight}{individual.random_weight}"
    )

def save_results(hall_of_fame, generation_results, output_dir="evolution_results"):
    """Save evolution results to file"""
    os.makedirs(output_dir, exist_ok=True)
    
    results = {
        "hall_of_fame": [ind.to_dict() for ind in hall_of_fame],
        "generation_results": generation_results
    }
    
    filename = os.path.join(output_dir, f"evolution_results_{int(time.time())}.json")
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to {filename}")
    
    # Save best player in a separate file for easy access
    best_ever = max(hall_of_fame, key=lambda ind: ind.fitness)
    evolved_player = {
        "name": f"Evolved_AI_{int(best_ever.fitness*100)}",
        "minimax_weight": best_ever.minimax_weight,
        "mcts_weight": best_ever.mcts_weight,
        "random_weight": best_ever.random_weight,
        "fitness": best_ever.fitness
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

def evolve_hybrid_ai(population_size=10, generations=5, board_size=7, num_rounds=3, verbose=False):
    """Run evolutionary optimization for HybridAI"""
    print(f"Starting evolutionary optimization with population={population_size}, generations={generations}")
    
    # Initialize population
    population = [HybridIndividual() for _ in range(population_size)]
    hall_of_fame = []
    generation_results = []
    
    for generation in range(generations):
        print(f"\n== Generation {generation+1}/{generations} ==")
        
        # Run tournament for this generation
        sorted_pop = run_tournament_generation(population, board_size, num_rounds, verbose)
        
        # Store best individual in hall of fame
        best_individual = sorted_pop[0]
        hall_of_fame.append(best_individual)
        
        # Store generation results
        gen_result = {
            "generation": generation + 1,
            "best_fitness": best_individual.fitness,
            "best_individual": best_individual.to_dict(),
            "population": [ind.to_dict() for ind in sorted_pop]
        }
        generation_results.append(gen_result)
        
        # Print current generation stats
        print("\nCurrent Population:")
        for i, ind in enumerate(sorted_pop[:5]):  # Show top 5
            print(f"  {i+1}. {ind} - Fitness: {ind.fitness:.3f} ({ind.games_won}/{ind.games_played})")
        
        # Save intermediate results
        save_results(hall_of_fame, generation_results)
        
        if generation < generations - 1:
            # Selection
            parents = selection(sorted_pop)
            
            # Create new population
            new_population = []
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(parents, 2)
                child1, child2 = crossover(parent1, parent2)
                
                child1 = mutation(child1)
                child2 = mutation(child2)
                
                new_population.append(child1)
                if len(new_population) < population_size:
                    new_population.append(child2)
            
            population = new_population
    
    # Final results
    print("\nEvolution complete!")
    print("\nHall of Fame (Best from each generation):")
    for i, ind in enumerate(hall_of_fame):
        print(f"  Gen {i+1}: {ind} - Fitness: {ind.fitness:.3f}")
    
    best_ever = max(hall_of_fame, key=lambda ind: ind.fitness)
    print(f"\nBest configuration found: {best_ever}")
    print(f"  Minimax Weight: {best_ever.minimax_weight}%")
    print(f"  MCTS Weight: {best_ever.mcts_weight}%")
    print(f"  Random Weight: {best_ever.random_weight}%")
    print(f"  Fitness: {best_ever.fitness:.3f}")
    
    # Save final results
    save_results(hall_of_fame, generation_results)