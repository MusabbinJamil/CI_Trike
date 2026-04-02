from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI, DQNAI
from trike_ai.agents.evolved_strategic_ai import EvolvedStrategicAI
from trike_ai.training.runner import run_ai_match  # Use your existing runner!
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
    agents = [
        RandomAI(name="RandomAI"),
        MinimaxAI(depth=4, name="MinimaxAI-Hard"),  # Hard difficulty
        MCTSAI(iterations=1000, name="MCTSAI"),
        DQNAI(name="DQNAI-Advanced"),  # Assuming this is your advanced DQN
        load_best_strategic_ai()
    ]
    return agents

def run_comprehensive_evaluation(num_matches=300, board_size=7, verbose=False):
    """
    Run comprehensive evaluation between all AI agents.
    """
    agents = create_ai_agents()
    
    # Create results directory
    results_dir = "evaluation_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Prepare CSV file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(results_dir, f"ai_evaluation_{timestamp}.csv")
    
    # CSV headers
    csv_headers = [
        'match_id', 'player1', 'player2', 'winner', 'player1_score', 'player2_score',
        'game_duration', 'total_moves', 'match_timestamp'
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
    total_matches = len(agents) * (len(agents) - 1) * num_matches  # Each pair plays both ways
    completed_matches = 0
    successful_matches = 0
    
    print(f"Starting comprehensive AI evaluation...")
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
                for match_num in range(num_matches):
                    match_id += 1
                    
                    try:
                        # Use your existing run_ai_match function!
                        result = run_ai_match(agent1, agent2, board_size=board_size, verbose=False)
                        
                        # Check if result is in the expected format
                        if isinstance(result, dict):
                            # New format from your updated runner
                            winner = result.get('winner', 'Unknown')
                            player1_score = result.get('player1_score', 0)
                            player2_score = result.get('player2_score', 0)
                            total_moves = result.get('total_moves', 0)
                            game_duration = result.get('game_duration', 0)
                            
                            # Skip if there was an error
                            if result.get('error'):
                                if verbose:
                                    print(f"  Match {match_num + 1} error: {result['error']}")
                                continue
                        else:
                            # Old format (winner, scores)
                            winner, scores = result
                            player1_score, player2_score = scores
                            total_moves = 0  # Not available in old format
                            game_duration = 0  # Not available in old format
                        
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
                            'game_duration': round(game_duration, 3),
                            'total_moves': total_moves,
                            'match_timestamp': match_timestamp
                        })
                        
                        successful_matches += 1
                        
                        if verbose or (match_num + 1) % 50 == 0:
                            print(f"  Match {match_num + 1}/{num_matches} completed. Winner: {winner}")
                        
                    except Exception as e:
                        if verbose:
                            print(f"Error in match {match_id}: {e}")
                        continue
                
                completed_matches += num_matches
                progress = (completed_matches / total_matches) * 100
                print(f"  {agent1.name} won {match_wins}/{num_matches} matches")
                print(f"Overall progress: {completed_matches}/{total_matches} ({progress:.1f}%)")
    
    print(f"\nCompleted {successful_matches} successful matches out of {total_matches} attempted")
    
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