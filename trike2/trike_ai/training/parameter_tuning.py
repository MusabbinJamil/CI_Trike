from trike_ai.training.tournament import run_tournament
from trike_ai.agents import MinimaxAI, MCTSAI
import itertools

def tune_minimax_parameters(depth_values=None, board_sizes=None):
    """
    Tune parameters for MinimaxAI agent.
    
    Args:
        depth_values (list): List of depth values to test
        board_sizes (list): List of board sizes to test
    
    Returns:
        dict: Best parameters found
    """
    if depth_values is None:
        depth_values = [2, 3, 4]  # Default depths to test
    
    if board_sizes is None:
        board_sizes = [5, 7]  # Default board sizes to test
    
    best_params = {"depth": 2, "board_size": 7}
    best_score = 0
    
    for depth in depth_values:
        # Create agents for this parameter set
        agents = [
            MinimaxAI(depth=depth, name=f"MinimaxAI-d{depth}"),
            RandomAI(name="RandomAI-baseline")  # Use as baseline
        ]
        
        for board_size in board_sizes:
            print(f"\nTesting Minimax with depth={depth} on board_size={board_size}")
            # Run mini-tournament for this parameter set
            results = run_tournament(agents, num_rounds=5, board_size=board_size, verbose=False)
            
            # Check if this agent performs better than the current best
            current_score = results[f"MinimaxAI-d{depth}"]
            if current_score > best_score:
                best_score = current_score
                best_params = {"depth": depth, "board_size": board_size}
                print(f"New best parameters found: {best_params} (score: {best_score})")
    
    print(f"\nBest parameters found: {best_params} with score {best_score}")
    return best_params

def tune_mcts_parameters(iterations_values=None, board_sizes=None):
    """
    Tune parameters for MCTSAI agent.
    
    Args:
        iterations_values (list): List of iteration counts to test
        board_sizes (list): List of board sizes to test
    
    Returns:
        dict: Best parameters found
    """
    if iterations_values is None:
        iterations_values = [100, 500, 1000]  # Default iteration counts to test
    
    if board_sizes is None:
        board_sizes = [5, 7]  # Default board sizes to test
    
    best_params = {"iterations": 500, "board_size": 7}
    best_score = 0
    
    for iterations in iterations_values:
        # Create agents for this parameter set
        agents = [
            MCTSAI(iterations=iterations, name=f"MCTSAI-i{iterations}"),
            RandomAI(name="RandomAI-baseline")  # Use as baseline
        ]
        
        for board_size in board_sizes:
            print(f"\nTesting MCTS with iterations={iterations} on board_size={board_size}")
            # Run mini-tournament for this parameter set
            results = run_tournament(agents, num_rounds=5, board_size=board_size, verbose=False)
            
            # Check if this agent performs better than the current best
            current_score = results[f"MCTSAI-i{iterations}"]
            if current_score > best_score:
                best_score = current_score
                best_params = {"iterations": iterations, "board_size": board_size}
                print(f"New best parameters found: {best_params} (score: {best_score})")
    
    print(f"\nBest parameters found: {best_params} with score {best_score}")
    return best_params

if __name__ == "__main__":
    from trike_ai.agents import RandomAI
    
    print("Tuning MinimaxAI parameters...")
    best_minimax_params = tune_minimax_parameters(
        depth_values=[2, 3, 4],
        board_sizes=[5, 7]
    )
    
    print("\nTuning MCTSAI parameters...")
    best_mcts_params = tune_mcts_parameters(
        iterations_values=[200, 500, 1000],
        board_sizes=[5, 7]
    )
    
    print("\nBest configurations found:")
    print(f"MinimaxAI: {best_minimax_params}")
    print(f"MCTSAI: {best_mcts_params}")