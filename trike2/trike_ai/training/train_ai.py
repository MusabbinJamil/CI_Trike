from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI
from trike_ai.training.tournament import run_tournament
from trike_ai.training.parameter_tuning import tune_minimax_parameters, tune_mcts_parameters
import argparse

def main():
    parser = argparse.ArgumentParser(description='Train AI agents for Trike')
    parser.add_argument('--mode', choices=['tournament', 'tune_minimax', 'tune_mcts', 'single_match'],
                        default='tournament', help='Training mode')
    parser.add_argument('--rounds', type=int, default=10, help='Number of rounds in tournament')
    parser.add_argument('--board_size', type=int, default=7, help='Board size')
    parser.add_argument('--verbose', action='store_true', help='Print detailed game logs')
    
    args = parser.parse_args()
    
    if args.mode == 'tournament':
        print("Running tournament mode...")
        agents = [
            RandomAI(name="RandomAI"),
            MinimaxAI(depth=2, name="MinimaxAI-d2"),
            MinimaxAI(depth=3, name="MinimaxAI-d3"),
            MCTSAI(iterations=500, name="MCTSAI-i500"),
            MCTSAI(iterations=1000, name="MCTSAI-i1000")
        ]
        run_tournament(agents, num_rounds=args.rounds, board_size=args.board_size, verbose=args.verbose)
        
    elif args.mode == 'tune_minimax':
        print("Tuning Minimax parameters...")
        tune_minimax_parameters(
            depth_values=[2, 3, 4],
            board_sizes=[5, 7, 9]
        )
        
    elif args.mode == 'tune_mcts':
        print("Tuning MCTS parameters...")
        tune_mcts_parameters(
            iterations_values=[200, 500, 1000],
            board_sizes=[5, 7, 9]
        )
        
    elif args.mode == 'single_match':
        from trike_ai.training.runner import run_ai_match
        print("Running a single match between two agents...")
        minimax = MinimaxAI(depth=3, name="MinimaxAI-d3")
        mcts = MCTSAI(iterations=500, name="MCTSAI-i500")
        run_ai_match(minimax, mcts, board_size=args.board_size, verbose=True)

if __name__ == "__main__":
    main()