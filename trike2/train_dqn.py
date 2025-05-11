import argparse
import copy
import time
import torch
import numpy as np
from src.game import Game
from trike_ai.agents.random_ai import RandomAI
from trike_ai.agents.dqn_ai import DQNAI

def calculate_reward(game, dqn_player_index):
    """Calculate reward based on game outcome."""
    if not game.pawn.position:
        return 0  # Game hasn't progressed enough
    
    # Check if pawn is trapped
    is_trapped = game.board.is_pawn_trapped()
    if not is_trapped:
        return 0  # Game not over yet
    
    # Calculate scores
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
    
    # Calculate reward from DQN player's perspective
    dqn_score = player1_score if dqn_player_index == 0 else player2_score
    opponent_score = player2_score if dqn_player_index == 0 else player1_score
    
    if dqn_score > opponent_score:
        return 1.0  # Win
    elif dqn_score < opponent_score:
        return -1.0  # Loss
    else:
        return 0.1  # Draw
    
def train_dqn_agent(episodes=1000, board_size=7, save_interval=100, render_interval=100):
    """Train the DQN agent by playing against RandomAI."""
    dqn_agent = DQNAI(board_size=board_size, name="DQN Agent")
    random_agent = RandomAI(name="Random Agent")
    
    print(f"Training DQN against RandomAI for {episodes} episodes...")
    print(f"Using device: {dqn_agent.device}")
    
    wins = 0
    losses = 0
    draws = 0
    
    start_time = time.time()
    
    for episode in range(1, episodes + 1):
        game = Game(board_size)
        
        # Randomly decide who goes first
        dqn_goes_first = np.random.choice([True, False])
        agents = [dqn_agent, random_agent] if dqn_goes_first else [random_agent, dqn_agent]
        dqn_player_index = 0 if dqn_goes_first else 1
        
        game_over = False
        turn_count = 0
        current_player_index = 0
        
        # Reset the DQN agent for new game
        dqn_agent.reset()
        
        while not game_over and turn_count < 100:  # Add turn limit to prevent infinite games
            current_agent = agents[current_player_index]
            
            # Encode current state before making a move
            if current_agent == dqn_agent:
                pre_move_state = dqn_agent._encode_state(game)
            
            # Get agent's move
            move = current_agent.choose_move(game)
            
            if move is None:
                print(f"No valid moves for {current_agent.name}")
                break
                
            # Apply the move
            q, r = move
            current_player = game.players[current_player_index]
            
            # If this is first move, place pawn
            if game.pawn.position is None:
                game.board.place_checker(q, r, current_player)
                game.pawn.position = (q, r)
                game.board.pawn_position = (q, r)
                game.first_move_done = True
            else:
                # Regular move
                game.board.place_checker(q, r, current_player)
                game.pawn.position = (q, r)
                game.board.pawn_position = (q, r)
            
            # Handle pie rule
            if game.first_move_done and game.pie_rule_available and current_player_index == 1:
                # Simple heuristic for pie rule
                size = board_size
                center_q, center_r = size // 2, size // 2
                if abs(q - center_q) + abs(r - center_r) <= 1:
                    game.players.reverse()
                game.pie_rule_available = False
            
            # Check if game is over
            game_over = game.pawn.position is not None and game.board.is_pawn_trapped()
            
            # For DQN agent, store the experience
            if current_agent == dqn_agent:
                next_state = dqn_agent._encode_state(game)
                reward = calculate_reward(game, dqn_player_index)
                
                # Convert move to action index
                if 0 <= q < board_size and 0 <= r < board_size:
                    action_idx = q * board_size + r
                    
                    # Store experience
                    dqn_agent.store_experience(
                        pre_move_state, 
                        action_idx, 
                        reward, 
                        next_state, 
                        game_over
                    )
                    
                    # Train the network on stored experiences
                    dqn_agent.train(None)
            
            # Advance to next player
            current_player_index = (current_player_index + 1) % 2
            turn_count += 1
        
        # Calculate outcome
        if game_over:
            reward = calculate_reward(game, dqn_player_index)
            if reward > 0:
                wins += 1
            elif reward < 0:
                losses += 1
            else:
                draws += 1
        
        # Print progress
        if episode % 10 == 0:
            elapsed = time.time() - start_time
            print(f"Episode: {episode}/{episodes} | " 
                  f"Win rate: {wins/episode:.2f} | "
                  f"Epsilon: {dqn_agent.epsilon:.3f} | "
                  f"Time: {elapsed:.1f}s")
        
        # Save model periodically
        if episode % save_interval == 0:
            dqn_agent.save_model()
            print(f"Model saved at episode {episode}")
    
    # Final statistics
    print("\nTraining complete!")
    print(f"Wins: {wins}/{episodes} ({wins/episodes:.2%})")
    print(f"Losses: {losses}/{episodes} ({losses/episodes:.2%})")
    print(f"Draws: {draws}/{episodes} ({draws/episodes:.2%})")
    
    # Save final model
    dqn_agent.save_model()
    print("Final model saved")
    
    return dqn_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a DQN agent for Trike")
    parser.add_argument("--episodes", type=int, default=1000, 
                        help="Number of training episodes")
    parser.add_argument("--board_size", type=int, default=7,
                        help="Size of the Trike board")
    parser.add_argument("--save_interval", type=int, default=100,
                        help="How often to save the model")
    
    args = parser.parse_args()
    
    trained_agent = train_dqn_agent(
        episodes=args.episodes,
        board_size=args.board_size,
        save_interval=args.save_interval
    )