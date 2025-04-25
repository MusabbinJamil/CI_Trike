from src.game import Game
from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI

def run_ai_match(agent1, agent2, board_size=7, verbose=True):
    """
    Run a match between two AI agents.
    
    Args:
        agent1: First AI agent
        agent2: Second AI agent
        board_size: Size of the game board
        verbose: Whether to print game progress
    
    Returns:
        tuple: (winner, scores) where winner is the name of the winning agent or "Draw"
               and scores is (agent1_score, agent2_score)
    """
    game = Game(board_size)
    
    if verbose:
        print(f"Starting match: {agent1.name} vs {agent2.name}")
    
    # Continue until the game is over
    while not (game.pawn.position is not None and game.board.is_pawn_trapped()):
        current_player_index = game.current_player_index
        current_agent = agent1 if current_player_index == 0 else agent2
        
        # Get the agent's move
        move = current_agent.choose_move(game)
        
        if move is None:
            if verbose:
                print(f"No valid moves available for {current_agent.name}")
            break
            
        if verbose:
            print(f"{current_agent.name} chooses move: {move}")
            
        # Apply the move
        q, r = move
        current_player = game.players[current_player_index]
        
        # If this is first move, place pawn
        if game.pawn.position is None:
            game.board.place_checker(q, r, current_player)
            game.pawn.position = (q, r)
            game.board.pawn_position = (q, r)
        else:
            # Regular move - place checker and move pawn
            game.board.place_checker(q, r, current_player)
            game.pawn.position = (q, r)
            game.board.pawn_position = (q, r)
        
        # Pie rule implementation
        if game.first_move_done and game.pie_rule_available:
            if current_player_index == 1:
                # Simple heuristic for pie rule: use it if the first move was
                # too advantageous (e.g., central position)
                size = board_size
                center_q, center_r = size // 2, size // 2
                
                # If first move was close to center, agent2 might choose to swap
                if abs(q - center_q) + abs(r - center_r) <= 1:
                    if verbose:
                        print(f"{agent2.name} uses pie rule to swap colors")
                    game.players.reverse()
                    game.current_player_index = 1
            
            game.pie_rule_available = False
        else:
            # Normal turn, advance to next player
            game.current_player_index = (current_player_index + 1) % 2
    
    # Calculate final scores
    pawn_pos = game.pawn.position
    neighbors = game.board.get_neighbors(*pawn_pos)
    under = game.board.grid[pawn_pos]
    
    adj = [game.board.grid.get(n) for n in neighbors]
    
    black_score = sum(1 for c in adj + [under] if c and c.color == "black")
    white_score = sum(1 for c in adj + [under] if c and c.color == "white")
    
    # Determine winner
    player1 = game.players[0]
    player2 = game.players[1]
    
    player1_score = black_score if player1.color == "black" else white_score
    player2_score = white_score if player1.color == "black" else black_score
    
    if player1_score > player2_score:
        winner = agent1.name
    elif player2_score > player1_score:
        winner = agent2.name
    else:
        winner = "Draw"
    
    if verbose:
        print(f"Game over! Final scores:")
        print(f"{agent1.name}: {player1_score}")
        print(f"{agent2.name}: {player2_score}")
        print(f"Winner: {winner}")
    
    return winner, (player1_score, player2_score)


if __name__ == "__main__":
    # Example match between different AI agents
    random_ai = RandomAI()
    minimax_ai = MinimaxAI(depth=2)
    mcts_ai = MCTSAI(iterations=500)
    
    # Run a match
    run_ai_match(minimax_ai, mcts_ai, board_size=7, verbose=True)