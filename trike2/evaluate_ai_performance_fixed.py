from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI, DQNAI
from trike_ai.agents.evolved_strategic_ai import EvolvedStrategicAI
from runner import run_ai_match  # Use your working runner.py
import csv
import os
import json
from datetime import datetime
import time

def load_best_strategic_ai():
    """Load the best evolved strategic AI from the saved configuration."""
    try:
        with open('evolved_strategic_players/best_strategic_ai.json', 'r') as f:
            data = json.load(f)
            best_ai_data = data['best_strategic_ai']
            
            # Create EvolvedStrategicAI with the best parameters
            ai = EvolvedStrategicAI(
                strategy_weights=best_ai_data['strategy_weights'],
                name="EvolvedStrategicAI-Best"
            )
            return ai
    except Exception as e:
        print(f"Failed to load best strategic AI: {e}")
        # Return a default EvolvedStrategicAI
        return EvolvedStrategicAI(name="EvolvedStrategicAI-Default")

def create_ai_agents():
    """Create all AI agents for evaluation."""
    agents = []
    
    try:
        print("Creating RandomAI...")
        agents.append(RandomAI(name="RandomAI"))
        print("✓ RandomAI created")
    except Exception as e:
        print(f"✗ Failed to create RandomAI: {e}")
    
    try:
        print("Creating MinimaxAI...")
        agents.append(MinimaxAI(depth=4, name="MinimaxAI-Hard"))
        print("✓ MinimaxAI created")
    except Exception as e:
        print(f"✗ Failed to create MinimaxAI: {e}")
    
    try:
        print("Creating MCTSAI...")
        agents.append(MCTSAI(iterations=1000, name="MCTSAI"))
        print("✓ MCTSAI created")
    except Exception as e:
        print(f"✗ Failed to create MCTSAI: {e}")
    
    try:
        print("Creating DQNAI...")
        agents.append(DQNAI(name="DQNAI-Advanced"))
        print("✓ DQNAI created")
    except Exception as e:
        print(f"✗ Failed to create DQNAI: {e}")
    
    try:
        print("Creating EvolvedStrategicAI...")
        agents.append(load_best_strategic_ai())
        print("✓ EvolvedStrategicAI created")
    except Exception as e:
        print(f"✗ Failed to create EvolvedStrategicAI: {e}")
    
    print(f"\nSuccessfully created {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.name}")
    
    return agents

def run_comprehensive_evaluation(num_matches=300, board_size=7, verbose=False):
    """
    Run comprehensive evaluation between all AI agents.
    """
    agents = create_ai_agents()
    
    if len(agents) < 2:
        print("Error: Need at least 2 agents to run evaluation!")
        return {}
    
    # Create results directory
    results_dir = "evaluation_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Prepare CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(results_dir, f"ai_evaluation_{timestamp}.csv")
    
    # CSV headers
    csv_headers = [
        'match_id', 'player1', 'player2', 'winner', 'player1_score', 'player2_score',
        'match_timestamp'
    ]
    
    # Initialize summary statistics
    summary_stats = {}
    for agent in agents:
        summary_stats[agent.name] = {
            'total_games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'total_score': 0,
            'opponent_scores': 0,
            'win_rate': 0.0,
            'loss_rate': 0.0,
            'draw_rate': 0.0,
            'avg_score': 0.0,
            'avg_opponent_score': 0.0,
            'score_differential': 0.0
        }
    
    match_id = 0
    total_matches = len(agents) * (len(agents) - 1) * num_matches
    completed_matches = 0
    successful_matches = 0
    
    print(f"\nStarting comprehensive AI evaluation...")
    print(f"Total matches to play: {total_matches}")
    print(f"Agents: {[agent.name for agent in agents]}")
    print(f"Results will be saved to: {csv_filename}")
    
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
        writer.writeheader()
        
        # Play each agent against every other agent
        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents):
                if i == j:  # Skip self-play
                    continue
                
                print(f"\n{agent1.name} vs {agent2.name}")
                print(f"Playing {num_matches} matches...")
                
                match_wins = 0
                matchup_successful = 0  # Track successful matches for this specific matchup
                matchup_errors = 0
                
                for match_num in range(num_matches):
                    match_id += 1
                    
                    try:
                        # Use your working run_ai_match function
                        # It returns (winner, (player1_score, player2_score))
                        winner, scores = run_ai_match(agent1, agent2, board_size=board_size, verbose=False)
                        player1_score, player2_score = scores
                        
                        match_timestamp = datetime.now().isoformat()
                        
                        # Update summary statistics
                        summary_stats[agent1.name]['total_games'] += 1
                        summary_stats[agent2.name]['total_games'] += 1
                        summary_stats[agent1.name]['total_score'] += player1_score
                        summary_stats[agent2.name]['total_score'] += player2_score
                        summary_stats[agent1.name]['opponent_scores'] += player2_score
                        summary_stats[agent2.name]['opponent_scores'] += player1_score
                        
                        if winner == agent1.name:
                            summary_stats[agent1.name]['wins'] += 1
                            summary_stats[agent2.name]['losses'] += 1
                            match_wins += 1
                        elif winner == agent2.name:
                            summary_stats[agent2.name]['wins'] += 1
                            summary_stats[agent1.name]['losses'] += 1
                        else:  # Draw
                            summary_stats[agent1.name]['draws'] += 1
                            summary_stats[agent2.name]['draws'] += 1
                        
                        # Write to CSV
                        writer.writerow({
                            'match_id': match_id,
                            'player1': agent1.name,
                            'player2': agent2.name,
                            'winner': winner,
                            'player1_score': player1_score,
                            'player2_score': player2_score,
                            'match_timestamp': match_timestamp
                        })
                        
                        successful_matches += 1
                        matchup_successful += 1
                        
                        if verbose or (match_num + 1) % 50 == 0:
                            print(f"  Match {match_num + 1}/{num_matches} completed. Winner: {winner}")
                        
                    except Exception as e:
                        matchup_errors += 1
                        if verbose:
                            print(f"Error in match {match_id}: {e}")
                        continue
                
                completed_matches += num_matches
                progress = (completed_matches / total_matches) * 100
                
                # Calculate success rate for this specific matchup
                matchup_success_rate = (matchup_successful / num_matches) * 100 if num_matches > 0 else 0
                
                # Calculate overall success rate across all matches so far
                overall_success_rate = (successful_matches / completed_matches) * 100 if completed_matches > 0 else 0
                
                print(f"  {agent1.name} won {match_wins}/{matchup_successful} successful matches")
                if matchup_errors > 0:
                    print(f"  Matchup success rate: {matchup_success_rate:.1f}% ({matchup_errors} errors)")
                else:
                    print(f"  Matchup success rate: {matchup_success_rate:.1f}%")
                print(f"  Overall success rate: {overall_success_rate:.1f}%")
                print(f"Overall progress: {completed_matches}/{total_matches} ({progress:.1f}%)")
    
    print(f"\nCompleted {successful_matches} successful matches out of {total_matches} attempted")
    if total_matches > successful_matches:
        overall_error_rate = ((total_matches - successful_matches) / total_matches) * 100
        print(f"Overall error rate: {overall_error_rate:.1f}%")
    
    # Calculate final statistics
    for agent_name, stats in summary_stats.items():
        if stats['total_games'] > 0:
            stats['win_rate'] = stats['wins'] / stats['total_games']
            stats['loss_rate'] = stats['losses'] / stats['total_games']
            stats['draw_rate'] = stats['draws'] / stats['total_games']
            stats['avg_score'] = stats['total_score'] / stats['total_games']
            stats['avg_opponent_score'] = stats['opponent_scores'] / stats['total_games']
            stats['score_differential'] = stats['avg_score'] - stats['avg_opponent_score']
    
    # Save summary statistics
    summary_filename = os.path.join(results_dir, f"ai_summary_{timestamp}.json")
    with open(summary_filename, 'w') as f:
        json.dump(summary_stats, f, indent=2)
    
    print(f"\nEvaluation completed!")
    print(f"Detailed results saved to: {csv_filename}")
    print(f"Summary statistics saved to: {summary_filename}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    print(f"{'Agent':<25} {'Win Rate':<10} {'Avg Score':<12} {'Score Diff':<12}")
    print(f"{'-'*60}")
    
    # Sort agents by win rate
    agents_with_games = [(name, stats) for name, stats in summary_stats.items() if stats['total_games'] > 0]
    sorted_agents = sorted(agents_with_games, key=lambda x: x[1]['win_rate'], reverse=True)
    
    for agent_name, stats in sorted_agents:
        win_rate = f"{stats['win_rate']:.3f}"
        avg_score = f"{stats['avg_score']:.2f}"
        score_diff = f"{stats['score_differential']:.2f}"
        print(f"{agent_name:<25} {win_rate:<10} {avg_score:<12} {score_diff:<12}")
    
    if not sorted_agents:
        print("No successful matches completed!")
    
    return summary_stats

def create_analysis_report(summary_stats, output_dir="evaluation_results"):
    """Create a detailed analysis report from the summary statistics."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = os.path.join(output_dir, f"analysis_report_{timestamp}.txt")
    
    with open(report_filename, 'w') as f:
        f.write("AI PERFORMANCE EVALUATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Evaluation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total agents evaluated: {len(summary_stats)}\n\n")
        
        # Filter agents that actually played games
        agents_with_games = [(name, stats) for name, stats in summary_stats.items() if stats['total_games'] > 0]
        
        if not agents_with_games:
            f.write("No successful matches were completed.\n")
            return
        
        # Sort by win rate
        sorted_agents = sorted(agents_with_games, key=lambda x: x[1]['win_rate'], reverse=True)
        
        f.write("RANKING BY WIN RATE:\n")
        f.write("-" * 30 + "\n")
        for rank, (agent_name, stats) in enumerate(sorted_agents, 1):
            f.write(f"{rank}. {agent_name}\n")
            f.write(f"   Win Rate: {stats['win_rate']:.3f} ({stats['wins']}/{stats['total_games']})\n")
            f.write(f"   Avg Score: {stats['avg_score']:.2f}\n")
            f.write(f"   Score Differential: {stats['score_differential']:.2f}\n\n")
        
        f.write("\nDETAILED STATISTICS:\n")
        f.write("-" * 30 + "\n")
        for agent_name, stats in sorted_agents:
            f.write(f"\n{agent_name}:\n")
            f.write(f"  Games Played: {stats['total_games']}\n")
            f.write(f"  Wins: {stats['wins']} ({stats['win_rate']:.3f})\n")
            f.write(f"  Losses: {stats['losses']} ({stats['loss_rate']:.3f})\n")
            f.write(f"  Draws: {stats['draws']} ({stats['draw_rate']:.3f})\n")
            f.write(f"  Average Score: {stats['avg_score']:.2f}\n")
            f.write(f"  Average Opponent Score: {stats['avg_opponent_score']:.2f}\n")
            f.write(f"  Score Differential: {stats['score_differential']:.2f}\n")
    
    print(f"Analysis report saved to: {report_filename}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive AI Performance Evaluation')
    parser.add_argument('--matches', type=int, default=300, help='Number of matches between each pair of agents')
    parser.add_argument('--board-size', type=int, default=7, help='Size of the game board')
    parser.add_argument('--verbose', action='store_true', help='Print detailed match information')
    
    args = parser.parse_args()
    
    print("Starting comprehensive AI evaluation...")
    summary_stats = run_comprehensive_evaluation(
        num_matches=args.matches,
        board_size=args.board_size,
        verbose=args.verbose
    )
    
    create_analysis_report(summary_stats)