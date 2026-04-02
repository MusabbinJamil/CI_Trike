from src.game import Game
from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI

def run_ai_match(agent1, agent2, board_size=7, verbose=True):
    """
    Run a match between two AI agents and return detailed results.
    
    Returns:
        dict: Match results including winner, scores, and game statistics
    """
    # Initialize game
    game = Game(board_size=board_size)
    game.setup_players()
    
    # Track game statistics
    total_moves = 0
    start_time = time.time()
    
    # Assign agents to players
    agents = [agent1, agent2]
    
    if verbose:
        print(f"Match: {agent1.name} vs {agent2.name}")
        print(f"Board size: {board_size}x{board_size}")
        print("-" * 40)
    
    # Game loop
    while not game.is_game_over():
        current_player_index = game.current_player_index
        current_agent = agents[current_player_index]
        
        try:
            # Get move from AI
            move = current_agent.get_move(game)
            
            if move is None:
                if verbose:
                    print(f"{current_agent.name} returned None move - game may be over")
                break
            
            # Apply the move
            q, r = move
            
            if game.pawn.position is None:
                # First move - place pawn
                if game.board.is_valid_position(q, r):
                    game.place_pawn(q, r)
                    total_moves += 1
                    if verbose:
                        print(f"{current_agent.name} placed pawn at ({q}, {r})")
                else:
                    if verbose:
                        print(f"Invalid pawn placement by {current_agent.name}")
                    break
            else:
                # Regular move
                q_from, r_from = game.pawn.position
                if game.board.is_valid_move(q_from, r_from, q, r):
                    # Place stone and move pawn
                    current_player = game.players[current_player_index]
                    game.board.place_stone(q_from, r_from, current_player.color)
                    game.pawn.move_to(q, r)
                    total_moves += 1
                    
                    if verbose:
                        print(f"{current_agent.name} moved pawn from ({q_from}, {r_from}) to ({q}, {r})")
                else:
                    if verbose:
                        print(f"Invalid move by {current_agent.name}")
                    break
            
            # Switch to next player
            game.current_player_index = (game.current_player_index + 1) % 2
            
        except Exception as e:
            if verbose:
                print(f"Error during {current_agent.name}'s turn: {e}")
            break
    
    # Calculate final scores
    pawn_pos = game.pawn.position
    if pawn_pos is None:
        # Game ended without proper completion
        return {
            'winner': 'Draw',
            'player1_score': 0,
            'player2_score': 0,
            'total_moves': total_moves,
            'game_duration': time.time() - start_time,
            'error': 'Game ended without pawn placement'
        }
    
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
        winner = 'Draw'
    
    game_duration = time.time() - start_time
    
    if verbose:
        print(f"Final scores: {agent1.name}: {player1_score}, {agent2.name}: {player2_score}")
        print(f"Winner: {winner}")
        print(f"Total moves: {total_moves}")
        print(f"Game duration: {game_duration:.2f} seconds")
    
    return {
        'winner': winner,
        'player1_score': player1_score,
        'player2_score': player2_score,
        'total_moves': total_moves,
        'game_duration': game_duration
    }


if __name__ == "__main__":
    # Example match between different AI agents
    random_ai = RandomAI()
    minimax_ai = MinimaxAI(depth=2)
    mcts_ai = MCTSAI(iterations=500)
    
    # Run a match
    run_ai_match(minimax_ai, mcts_ai, board_size=7, verbose=True)