import random
import json
import os
import time
import copy
from typing import List, Tuple
from collections import deque
import numpy as np

from ..agents.evolved_strategic_ai import EvolvedStrategicAI
from .runner import run_ai_match
from ..agents.random_ai import RandomAI
from ..agents.minimax_ai import MinimaxAI

class StrategicIndividual:
    """Individual in the strategic AI evolution population."""
    
    def __init__(self, strategy_weights=None, name=None):
        if strategy_weights is None:
            strategy_weights = self._generate_random_weights()
        
        self.strategy_weights = strategy_weights
        self.fitness = 0.0
        self.games_played = 0
        self.games_won = 0
        self.name = name or f"Strategic-{id(self)}"
        
        # Create AI instance
        self.ai = EvolvedStrategicAI(
            name=self.name,
            strategy_weights=self.strategy_weights
        )
    
    def _generate_random_weights(self):
        """Generate random strategic weights."""
        return {
            # Early game strategies
            'center_control': random.randint(0, 100),
            'corner_avoidance': random.randint(0, 100),
            'side_preference': random.randint(0, 100),
            'corner_capture': random.randint(0, 100),
            
            # Middle game strategies
            'influence_maximization': random.randint(0, 100),
            'opponent_influence_reduction': random.randint(0, 100),
            'trap_avoidance': random.randint(0, 100),
            'region_separation_awareness': random.randint(0, 100),
            
            # Mid-late game strategies
            'pocket_identification': random.randint(0, 100),
            'enemy_pocket_filling': random.randint(0, 100),
            'own_pocket_avoidance': random.randint(0, 100),
            'stone_burial_strategy': random.randint(0, 100),
            
            # Late game strategies
            'corridor_control': random.randint(0, 100),
            'closing_avoidance': random.randint(0, 100),
            'endpoint_manipulation': random.randint(0, 100),
            
            # Trap strategies
            'set_trap': random.randint(0, 100),
            'extend_trap': random.randint(0, 100),
            'multiple_traps': random.randint(0, 100),
            'sacrifice_trap': random.randint(0, 100),
            'defuse_inside': random.randint(0, 100),
            'defuse_downstream': random.randint(0, 100),
            'lock_away_traps': random.randint(0, 100),
        }
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'strategy_weights': self.strategy_weights,
            'fitness': self.fitness,
            'games_played': self.games_played,
            'games_won': self.games_won,
            'name': self.name
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        individual = cls(
            strategy_weights=data['strategy_weights'],
            name=data['name']
        )
        individual.fitness = data.get('fitness', 0.0)
        individual.games_played = data.get('games_played', 0)
        individual.games_won = data.get('games_won', 0)
        return individual
    
    def __str__(self):
        return f"Strategic AI (Fitness: {self.fitness:.3f})"

def run_strategic_tournament(population: List[StrategicIndividual], 
                           board_size: int, 
                           num_rounds: int, 
                           verbose: bool = False):
    """Run tournament between strategic individuals."""
    
    # Create reference opponents
    random_ai = RandomAI(name="Random Reference")
    minimax_ai = MinimaxAI(name="Minimax Reference", depth=2)
    
    total_matches = len(population) * (num_rounds * 4 + len(population) * num_rounds)
    matches_played = 0
    
    for i, individual in enumerate(population):
        individual.games_played = 0
        individual.games_won = 0
        
        # Play against reference opponents
        for opponent in [random_ai, minimax_ai]:
            for _ in range(num_rounds):
                # As first player
                result = run_ai_match(individual.ai, opponent, board_size=board_size, verbose=False)
                winner, _ = result
                if winner == individual.ai.name:
                    individual.games_won += 1
                individual.games_played += 1
                matches_played += 1
                
                # As second player
                result = run_ai_match(opponent, individual.ai, board_size=board_size, verbose=False)
                winner, _ = result
                if winner == individual.ai.name:
                    individual.games_won += 1
                individual.games_played += 1
                matches_played += 1
                
                if verbose:
                    progress = (matches_played / total_matches) * 100
                    print(f"\rTournament progress: {progress:.1f}%", end="")
        
        # Play against other population members
        opponents = random.sample(population[:i] + population[i+1:], 
                                min(3, len(population)-1))
        
        for opponent in opponents:
            for _ in range(num_rounds):
                # As first player
                result = run_ai_match(individual.ai, opponent.ai, board_size=board_size, verbose=False)
                winner, _ = result
                if winner == individual.ai.name:
                    individual.games_won += 1
                individual.games_played += 1
                matches_played += 1
                
                # As second player
                result = run_ai_match(opponent.ai, individual.ai, board_size=board_size, verbose=False)
                winner, _ = result
                if winner == individual.ai.name:
                    individual.games_won += 1
                individual.games_played += 1
                matches_played += 1
                
                if verbose:
                    progress = (matches_played / total_matches) * 100
                    print(f"\rTournament progress: {progress:.1f}%", end="")
    
    # Calculate fitness
    for individual in population:
        if individual.games_played > 0:
            individual.fitness = individual.games_won / individual.games_played
        else:
            individual.fitness = 0.0
    
    if verbose:
        print()  # New line after progress
    
    return sorted(population, key=lambda x: x.fitness, reverse=True)

def tournament_selection(population: List[StrategicIndividual], 
                        tournament_size: int = 3) -> List[StrategicIndividual]:
    """Select parents using tournament selection."""
    parents = []
    
    for _ in range(len(population) // 2):
        tournament = random.sample(population, min(tournament_size, len(population)))
        winner = max(tournament, key=lambda x: x.fitness)
        parents.append(winner)
    
    return parents

def strategic_crossover(parent1: StrategicIndividual, 
                       parent2: StrategicIndividual,
                       crossover_rate: float = 0.7) -> Tuple[StrategicIndividual, StrategicIndividual]:
    """Create offspring through strategic crossover."""
    
    if random.random() > crossover_rate:
        return copy.deepcopy(parent1), copy.deepcopy(parent2)
    
    # Weighted average crossover with some randomness
    child1_weights = {}
    child2_weights = {}
    
    for key in parent1.strategy_weights:
        # Blend parents with random weight
        blend_ratio = random.uniform(0.3, 0.7)
        
        child1_weights[key] = int(
            blend_ratio * parent1.strategy_weights[key] + 
            (1 - blend_ratio) * parent2.strategy_weights[key]
        )
        
        child2_weights[key] = int(
            (1 - blend_ratio) * parent1.strategy_weights[key] + 
            blend_ratio * parent2.strategy_weights[key]
        )
        
        # Ensure bounds
        child1_weights[key] = max(0, min(100, child1_weights[key]))
        child2_weights[key] = max(0, min(100, child2_weights[key]))
    
    child1 = StrategicIndividual(strategy_weights=child1_weights)
    child2 = StrategicIndividual(strategy_weights=child2_weights)
    
    return child1, child2

def strategic_mutation(individual: StrategicIndividual, 
                      mutation_rate: float = 0.2) -> StrategicIndividual:
    """Mutate an individual's strategic weights."""
    
    mutated_weights = copy.deepcopy(individual.strategy_weights)
    
    for key in mutated_weights:
        if random.random() < mutation_rate:
            # Gaussian mutation
            mutation_amount = random.gauss(0, 10)  # Standard deviation of 10
            mutated_weights[key] = int(mutated_weights[key] + mutation_amount)
            
            # Ensure bounds
            mutated_weights[key] = max(0, min(100, mutated_weights[key]))
    
    return StrategicIndividual(strategy_weights=mutated_weights)

def save_strategic_results(hall_of_fame: List[StrategicIndividual], 
                          generation_results: List[dict]):
    """Save evolution results."""
    os.makedirs("evolved_strategic_players", exist_ok=True)
    
    # Save hall of fame
    hof_data = [individual.to_dict() for individual in hall_of_fame]
    with open("evolved_strategic_players/hall_of_fame.json", "w") as f:
        json.dump(hof_data, f, indent=2)
    
    # Save generation results
    with open("evolved_strategic_players/evolution_log.json", "w") as f:
        json.dump(generation_results, f, indent=2)
    
    # Save best individual as playable AI
    if hall_of_fame:
        best = max(hall_of_fame, key=lambda x: x.fitness)
        best_data = {
            "best_strategic_ai": best.to_dict(),
            "description": "Best strategic AI evolved through evolutionary algorithm",
            "strategies_learned": list(best.strategy_weights.keys())
        }
        with open("evolved_strategic_players/best_strategic_ai.json", "w") as f:
            json.dump(best_data, f, indent=2)

def evolve_strategic_ai(population_size: int = 20,
                       generations: int = 30,
                       board_size: int = 7,
                       num_rounds: int = 3,
                       tournament_size: int = 4,
                       mutation_rate: float = 0.25,
                       crossover_rate: float = 0.8,
                       verbose: bool = True):
    """
    Evolve strategic AI using evolutionary algorithms.
    
    This function evolves AI agents that learn sophisticated Trike strategies including:
    - Early game positioning (center control, corner avoidance)
    - Middle game tactics (influence maximization, trap avoidance)  
    - Late game strategy (corridor control, endpoint manipulation)
    - Advanced trap techniques (setting, extending, sacrificing traps)
    """
    
    print(f"Starting Strategic AI Evolution:")
    print(f"  Population: {population_size}")
    print(f"  Generations: {generations}")
    print(f"  Board size: {board_size}")
    print(f"  Rounds per matchup: {num_rounds}")
    print(f"  Tournament size: {tournament_size}")
    print(f"  Mutation rate: {mutation_rate}")
    print(f"  Crossover rate: {crossover_rate}")
    
    # Initialize population
    population = [StrategicIndividual() for _ in range(population_size)]
    
    hall_of_fame = []
    generation_results = []
    
    for generation in range(generations):
        print(f"\n=== Generation {generation + 1}/{generations} ===")
        
        start_time = time.time()
        
        # Run tournament
        sorted_population = run_strategic_tournament(
            population, board_size, num_rounds, verbose
        )
        
        generation_time = time.time() - start_time
        
        # Store best individual
        best_individual = sorted_population[0]
        hall_of_fame.append(copy.deepcopy(best_individual))
        
        # Record generation results
        gen_result = {
            "generation": generation + 1,
            "best_fitness": best_individual.fitness,
            "best_weights": best_individual.strategy_weights,
            "average_fitness": sum(ind.fitness for ind in sorted_population) / len(sorted_population),
            "generation_time": generation_time
        }
        generation_results.append(gen_result)
        
        # Print generation stats
        print(f"\nGeneration {generation + 1} Results:")
        print(f"  Best fitness: {best_individual.fitness:.3f}")
        print(f"  Average fitness: {gen_result['average_fitness']:.3f}")
        print(f"  Time: {generation_time:.1f}s")
        
        print("\nTop 5 Strategic Weights of Best Individual:")
        sorted_weights = sorted(best_individual.strategy_weights.items(), 
                              key=lambda x: x[1], reverse=True)
        for strategy, weight in sorted_weights[:5]:
            print(f"  {strategy}: {weight}")
        
        # Save intermediate results
        save_strategic_results(hall_of_fame, generation_results)
        
        # Create next generation (except for last generation)
        if generation < generations - 1:
            # Selection
            parents = tournament_selection(sorted_population, tournament_size)
            
            # Create new population
            new_population = []
            
            # Keep best individuals (elitism)
            elite_count = max(1, population_size // 10)
            new_population.extend(copy.deepcopy(sorted_population[:elite_count]))
            
            # Generate offspring
            while len(new_population) < population_size:
                parent1, parent2 = random.sample(parents, 2)
                child1, child2 = strategic_crossover(parent1, parent2, crossover_rate)
                
                # Mutate children
                child1 = strategic_mutation(child1, mutation_rate)
                child2 = strategic_mutation(child2, mutation_rate)
                
                new_population.append(child1)
                if len(new_population) < population_size:
                    new_population.append(child2)
            
            population = new_population[:population_size]
    
    # Final results
    print("\n" + "="*50)
    print("STRATEGIC AI EVOLUTION COMPLETE!")
    print("="*50)
    
    best_ever = max(hall_of_fame, key=lambda x: x.fitness)
    print(f"\nBest Strategic AI Found:")
    print(f"  Fitness: {best_ever.fitness:.3f}")
    print(f"  Games Won: {best_ever.games_won}/{best_ever.games_played}")
    
    print(f"\nTop Strategic Weights:")
    sorted_weights = sorted(best_ever.strategy_weights.items(), 
                          key=lambda x: x[1], reverse=True)
    for strategy, weight in sorted_weights[:10]:
        print(f"  {strategy}: {weight}")
    
    # Analyze learned strategies
    print(f"\nStrategic Analysis:")
    high_weights = {k: v for k, v in best_ever.strategy_weights.items() if v > 70}
    if high_weights:
        print("  Strong strategies learned:")
        for strategy, weight in high_weights.items():
            print(f"    - {strategy}: {weight}")
    
    # Save final results
    save_strategic_results(hall_of_fame, generation_results)
    
    print(f"\nResults saved to 'evolved_strategic_players/' directory")
    print(f"Best AI can be loaded from 'best_strategic_ai.json'")
    
    return best_ever, hall_of_fame, generation_results