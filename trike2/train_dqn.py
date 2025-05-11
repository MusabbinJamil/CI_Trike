import argparse
import copy
import time
import torch
import numpy as np
import os
from src.game import Game
from trike_ai.agents.random_ai import RandomAI
from trike_ai.agents.dqn_ai import DQNAI
from trike_ai.agents.minimax_ai import MinimaxAI

def calculate_reward(game, dqn_player_index, previous_state=None):
    """Enhanced reward function with stronger learning signals"""
    # Terminal state reward (end of game)
    if game.pawn.position and game.board.is_pawn_trapped():
        # Calculate scores
        pawn_pos = game.pawn.position
        neighbors = game.board.get_neighbors(*pawn_pos)
        under = game.board.grid[pawn_pos]
        adj = [game.board.grid.get(n) for n in neighbors]
        
        black_score = sum(1 for c in adj + [under] if c and c.color == "black")
        white_score = sum(1 for c in adj + [under] if c and c.color == "white")
        
        player1 = game.players[0]
        player2 = game.players[1]
        
        player1_score = black_score if player1.color == "black" else white_score
        player2_score = white_score if player1.color == "black" else black_score
        
        dqn_score = player1_score if dqn_player_index == 0 else player2_score
        opponent_score = player2_score if dqn_player_index == 0 else player1_score
        
        # More extreme rewards for game outcomes
        score_diff = dqn_score - opponent_score
        if score_diff > 0:
            return 5.0 + 0.5 * score_diff  # Much higher reward for victory
        elif score_diff < 0:
            return -3.0  # Stronger negative feedback
        else:
            return 0.5  # Small positive reward for draws
    
    # Intermediate rewards during gameplay
    elif game.pawn.position:
        # Reward for controlling the center
        size = game.board.size
        center_q, center_r = size // 2, size // 2
        pawn_q, pawn_r = game.pawn.position
        distance_to_center = abs(pawn_q - center_q) + abs(pawn_r - center_r)
        center_control_reward = 0.05 * (size - distance_to_center) / size  # Increased from 0.02
        
        # Reward for having more pieces of your color around the pawn
        if under := game.board.grid.get(game.pawn.position):
            neighbors = game.board.get_neighbors(*game.pawn.position)
            adj = [game.board.grid.get(n) for n in neighbors if n in game.board.grid]
            
            dqn_color = game.players[dqn_player_index].color
            friendly_pieces = sum(1 for c in adj if c and c.color == dqn_color)
            opponent_pieces = sum(1 for c in adj if c and c.color != dqn_color)
            
            # Reward strategy of surrounding with own pieces
            surrounding_reward = 0.04 * friendly_pieces - 0.02 * opponent_pieces
            
            return center_control_reward + surrounding_reward
    
    return 0  # Default reward

def train_dqn_agent(episodes=5000, board_size=7, save_interval=100, render_interval=1000):
    """Train the DQN agent by playing against multiple opponents."""
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Modified parameters for better learning
    dqn_agent = DQNAI(board_size=board_size, name="DQN Agent", 
                      epsilon=1.0, epsilon_min=0.15, epsilon_decay=0.9995)
    
    # Create multiple opponent types
    random_agent = RandomAI(name="Random Agent")
    minimax_easy = MinimaxAI(depth=1, name="Minimax Easy")
    
    # As training progresses, use better opponents
    def select_opponent(episode):
        if episode < episodes * 0.3:  # First 30% - just random
            return random_agent
        elif episode < episodes * 0.7:  # 30-70% - mix of random and minimax
            return np.random.choice([random_agent, minimax_easy])
        else:  # Last 30% - minimax
            return minimax_easy
    
    print(f"Training DQN against multiple opponents for {episodes} episodes...")
    print(f"Using device: {dqn_agent.device}")
    
    wins = 0
    losses = 0
    draws = 0
    
    start_time = time.time()
    
    for episode in range(1, episodes + 1):
        game = Game(board_size)
        
        # Randomly decide who goes first
        dqn_goes_first = np.random.choice([True, False])
        opponent = select_opponent(episode)
        agents = [dqn_agent, opponent] if dqn_goes_first else [opponent, dqn_agent]
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
            dqn_agent.save_model(f"models/DQN_Agent_{episode}ep.pt")
            print(f"Model saved at episode {episode}")
        
        # Self-play logic
        if episode % 500 == 0 and episode > 0:
            try:
                print(f"Starting self-play training at episode {episode}...")
                
                # Use existing model instead of saving a new one
                # This avoids permission issues with writing files
                model_path = "models/DQN_Agent_self_play_500.pt/DQN_Agent.pt"
                
                # Create opponent using existing model
                self_play_opponent = DQNAI(board_size=board_size, name="Self-Play Opponent")
                self_play_opponent.load_model(model_path)
                self_play_opponent.epsilon = 0.05  # Low exploration for opponent
                
                # Track self-play performance
                sp_wins = 0
                sp_games = 100
                
                # Run self-play games
                for sp_game in range(sp_games):
                    if sp_game % 20 == 0:
                        print(f"Self-play game {sp_game}/{sp_games}")
                        
                    # Create a new game for self-play
                    sp_game_instance = Game(board_size)
                    
                    # Randomly decide who goes first
                    dqn_goes_first = np.random.choice([True, False])
                    sp_agents = [dqn_agent, self_play_opponent] if dqn_goes_first else [self_play_opponent, dqn_agent]
                    sp_dqn_idx = 0 if dqn_goes_first else 1
                    
                    sp_game_over = False
                    sp_turn_count = 0
                    sp_current_player_idx = 0
                    
                    # Play the self-play game
                    while not sp_game_over and sp_turn_count < 100:
                        sp_current_agent = sp_agents[sp_current_player_idx]
                        
                        # Record state for DQN agent
                        if sp_current_agent == dqn_agent:
                            sp_pre_move_state = dqn_agent._encode_state(sp_game_instance)
                        
                        # Get agent's move
                        sp_move = sp_current_agent.choose_move(sp_game_instance)
                        
                        if sp_move is None:
                            break
                        
                        # Apply move
                        sp_q, sp_r = sp_move
                        sp_current_player = sp_game_instance.players[sp_current_player_idx]
                        
                        # Handle first move
                        if sp_game_instance.pawn.position is None:
                            sp_game_instance.board.place_checker(sp_q, sp_r, sp_current_player)
                            sp_game_instance.pawn.position = (sp_q, sp_r)
                            sp_game_instance.board.pawn_position = (sp_q, sp_r)
                            sp_game_instance.first_move_done = True
                        else:
                            # Regular move
                            sp_game_instance.board.place_checker(sp_q, sp_r, sp_current_player)
                            sp_game_instance.pawn.position = (sp_q, sp_r)
                            sp_game_instance.board.pawn_position = (sp_q, sp_r)
                        
                        # Handle pie rule
                        if sp_game_instance.first_move_done and sp_game_instance.pie_rule_available and sp_current_player_idx == 1:
                            size = board_size
                            center_q, center_r = size // 2, size // 2
                            if abs(sp_q - center_q) + abs(sp_r - center_r) <= 1:
                                sp_game_instance.players.reverse()
                            sp_game_instance.pie_rule_available = False
                        
                        # Check if game over
                        sp_game_over = sp_game_instance.pawn.position is not None and sp_game_instance.board.is_pawn_trapped()
                        
                        # For DQN agent, store experience
                        if sp_current_agent == dqn_agent:
                            sp_next_state = dqn_agent._encode_state(sp_game_instance)
                            sp_reward = calculate_reward(sp_game_instance, sp_dqn_idx)
                            
                            # Convert move to action index
                            if 0 <= sp_q < board_size and 0 <= sp_r < board_size:
                                sp_action_idx = sp_q * board_size + sp_r
                                
                                # Store and learn from experience
                                dqn_agent.store_experience(
                                    sp_pre_move_state,
                                    sp_action_idx,
                                    sp_reward,
                                    sp_next_state,
                                    sp_game_over
                                )
                                
                                # Train on this experience
                                dqn_agent.train(None)
                        
                        # Move to next player
                        sp_current_player_idx = (sp_current_player_idx + 1) % 2
                        sp_turn_count += 1
                    
                    # Track wins against self
                    if sp_game_over:
                        sp_final_reward = calculate_reward(sp_game_instance, sp_dqn_idx)
                        if sp_final_reward > 0:
                            sp_wins += 1
                
                print(f"Self-play complete: Won {sp_wins}/{sp_games} games ({sp_wins/sp_games:.2f})")
                
            except Exception as e:
                print(f"Error during self-play: {e}")
                import traceback
                traceback.print_exc()
                print("Continuing with regular training...")
    
    # Final statistics
    print("\nTraining complete!")
    print(f"Wins: {wins}/{episodes} ({wins/episodes:.2%})")
    print(f"Losses: {losses}/{episodes} ({losses/episodes:.2%})")
    print(f"Draws: {draws}/{episodes} ({draws/episodes:.2%})")
    
    # Save final model
    dqn_agent.save_model(f"models/DQN_Agent_{episode}ep.pt")
    print(f"Final model saved as DQN_Agent_{episodes}ep.pt")
    
    return dqn_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a DQN agent for Trike")
    parser.add_argument("--episodes", type=int, default=5000, 
                        help="Number of training episodes")
    parser.add_argument("--board_size", type=int, default=7,
                        help="Size of the Trike board")
    parser.add_argument("--save_interval", type=int, default=1000,
                        help="How often to save the model")
    
    args = parser.parse_args()
    
    trained_agent = train_dqn_agent(
        episodes=args.episodes,
        board_size=args.board_size,
        save_interval=args.save_interval
    )