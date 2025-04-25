from trike_ai.training.runner import run_ai_match
import time
import csv
import os
from datetime import datetime

def run_tournament(agents, num_rounds=10, board_size=7, verbose=False):
    """
    Run a tournament between multiple AI agents.
    
    Args:
        agents (list): List of AI agent instances
        num_rounds (int): Number of rounds each pair of agents will play
        board_size (int): Size of the game board
        verbose (bool): Whether to print detailed game progress
        
    Returns:
        dict: Dictionary with agent names as keys and their total scores as values
    """
    results = {agent.name: 0 for agent in agents}
    matches = []
    
    print(f"Starting tournament with {len(agents)} agents, {num_rounds} rounds each")
    start_time = time.time()
    
    # Each agent plays against every other agent
    for i, agent1 in enumerate(agents):
        for j, agent2 in enumerate(agents):
            if i >= j:  # Skip self-play and duplicate matchups
                continue
                
            print(f"\nMatchup: {agent1.name} vs {agent2.name}")
            agent1_wins = 0
            agent2_wins = 0
            draws = 0
            
            for round_num in range(num_rounds):
                # Alternate who goes first
                if round_num % 2 == 0:
                    first_agent, second_agent = agent1, agent2
                else:
                    first_agent, second_agent = agent2, agent1
                
                print(f"  Round {round_num+1}: {first_agent.name} goes first")
                
                # Reset agents before each match
                first_agent.reset()
                second_agent.reset()
                
                # Run the match
                winner, (score1, score2) = run_ai_match(
                    first_agent, second_agent, 
                    board_size=board_size, 
                    verbose=verbose
                )
                
                # Record results based on who went first
                if round_num % 2 == 0:
                    if winner == agent1.name:
                        agent1_wins += 1
                    elif winner == agent2.name:
                        agent2_wins += 1
                    else:
                        draws += 1
                    match_result = (agent1.name, agent2.name, winner, score1, score2)
                else:
                    if winner == agent2.name:
                        agent1_wins += 1  # agent2 was first but maps to agent1 in our counting
                    elif winner == agent1.name:
                        agent2_wins += 1  # agent1 was first but maps to agent2 in our counting
                    else:
                        draws += 1
                    match_result = (agent2.name, agent1.name, winner, score1, score2)
                
                matches.append(match_result)
                
            # Update tournament results
            results[agent1.name] += agent1_wins
            results[agent2.name] += agent2_wins
            
            print(f"  Results: {agent1.name} won {agent1_wins}, {agent2.name} won {agent2_wins}, draws: {draws}")
    
    # Sort results by win count
    results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
    
    duration = time.time() - start_time
    print(f"\nTournament completed in {duration:.2f} seconds")
    print("\nFinal Tournament Results:")
    for agent_name, wins in results.items():
        print(f"{agent_name}: {wins} wins")
    
    # Save results to CSV
    save_tournament_results(results, matches)
    
    return results

def save_tournament_results(results, matches):
    """Save tournament results to CSV files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("results", exist_ok=True)
    
    # Save summary results
    with open(f"results/tournament_summary_{timestamp}.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Agent', 'Wins'])
        for agent_name, wins in results.items():
            writer.writerow([agent_name, wins])
    
    # Save detailed match results
    with open(f"results/tournament_matches_{timestamp}.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Agent1', 'Agent2', 'Winner', 'Score1', 'Score2'])
        for match in matches:
            writer.writerow(match)
    
    print(f"Results saved to 'results/tournament_*_{timestamp}.csv'")


if __name__ == "__main__":
    from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI
    
    # Create agents with different parameters
    agents = [
        RandomAI(name="RandomAI"),
        MinimaxAI(depth=2, name="MinimaxAI-d2"),
        MinimaxAI(depth=3, name="MinimaxAI-d3"),
        MCTSAI(iterations=500, name="MCTSAI-i500"),
        MCTSAI(iterations=1000, name="MCTSAI-i1000")
    ]
    
    # Run tournament
    run_tournament(agents, num_rounds=6, board_size=7, verbose=False)