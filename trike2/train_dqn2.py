import argparse
import copy
import time
import torch
import numpy as np
import os
import random
import traceback
from collections import deque
from src.game import Game
from trike_ai.agents.dqn_ai import DQNAI
from trike_ai.agents.random_ai import RandomAI

def calculate_reward(game, dqn_player_index, previous_state=None):
    """Enhanced reward function with sophisticated learning signals"""
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
        
        # Extremely strong terminal rewards
        score_diff = dqn_score - opponent_score
        if score_diff > 0:
            return 20.0 + 2.0 * score_diff  # Much stronger positive feedback
        elif score_diff < 0:
            return -10.0 - 1.0 * abs(score_diff)  # Stronger negative feedback
        else:
            return 0.1  # Near-zero for draws
    
    # Sophisticated intermediate rewards
    elif game.pawn.position:
        reward = 0
        size = game.board.size
        center_q, center_r = size // 2, size // 2
        pawn_q, pawn_r = game.pawn.position
        
        # Phase detection - early, mid or late game
        total_pieces = sum(1 for pos in game.board.grid if game.board.grid[pos])
        game_phase = "early" if total_pieces < size else "mid" if total_pieces < size*2 else "late"
        
        # Early game - control the center
        if game_phase == "early":
            distance_to_center = abs(pawn_q - center_q) + abs(pawn_r - center_r)
            center_control = (size - distance_to_center) / size
            reward += 0.2 * center_control
        
        # Mid/Late game - surround the pawn with your pieces
        if game_phase in ["mid", "late"]:
            neighbors = game.board.get_neighbors(*game.pawn.position)
            adj = [game.board.grid.get(n) for n in neighbors if n in game.board.grid]
            
            dqn_color = game.players[dqn_player_index].color
            friendly_pieces = sum(1 for c in adj if c and c.color == dqn_color)
            opponent_pieces = sum(1 for c in adj if c and c.color != dqn_color)
            
            # Progressive reward for surrounding
            reward += 0.15 * friendly_pieces - 0.1 * opponent_pieces
            
            # Extra reward for trapping opponent
            if friendly_pieces >= len(adj) - 1 and len(adj) >= 3:
                reward += 0.5
                
        return reward
    
    return 0  # Default reward

def train_advanced_self_play(episodes=5000, board_size=7, save_interval=100):
    """Train a DQN agent using advanced self-play techniques"""
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    
    # Initialize the main learning agent with optimized parameters
    main_agent = DQNAI(
        board_size=board_size, 
        name="DQN Main",
        epsilon=1.0, 
        epsilon_min=0.05,  # Lower min epsilon 
        epsilon_decay=0.998,  # Moderate decay
        learning_rate=0.001,  # Optimize learning rate
        gamma=0.99  # Higher discount factor
    )
    
    # Create a pool of historical agents for diverse opponents
    agent_pool = deque(maxlen=5)  # Keep last 5 snapshots
    
    # Add a random agent as initial opponent
    random_agent = RandomAI(name="Random Agent")
    
    print(f"Training DQN using advanced self-play for {episodes} episodes...")
    print(f"Using device: {main_agent.device}")
    
    # Statistics tracking
    wins = 0
    losses = 0
    draws = 0
    win_rates = []
    
    start_time = time.time()
    
    for episode in range(1, episodes + 1):
        game = Game(board_size)
        
        # Select opponent - 20% random agent, 80% from pool (if available)
        if not agent_pool or random.random() < 0.2:
            opponent = random_agent
        else:
            # Choose a random historical agent from the pool
            opponent = random.choice(agent_pool)
        
        # Randomly decide who goes first
        main_goes_first = np.random.choice([True, False])
        agents = [main_agent, opponent] if main_goes_first else [opponent, main_agent]
        main_idx = 0 if main_goes_first else 1
        
        game_over = False
        turn_count = 0
        current_player_idx = 0
        
        # Reset agent for new game
        main_agent.reset()
        
        while not game_over and turn_count < 100:  # Turn limit
            current_agent = agents[current_player_idx]
            
            # Store current state for the main agent
            if current_agent == main_agent:
                pre_move_state = main_agent._encode_state(game)
            
            # Get move from current agent
            move = current_agent.choose_move(game)
            
            if move is None:
                break
                
            # Apply the move
            q, r = move
            current_player = game.players[current_player_idx]
            
            # First move handling
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
            if game.first_move_done and game.pie_rule_available and current_player_idx == 1:
                size = board_size
                center_q, center_r = size // 2, size // 2
                if abs(q - center_q) + abs(r - center_r) <= 1:
                    game.players.reverse()
                game.pie_rule_available = False
            
            # Check if game is over
            game_over = game.pawn.position is not None and game.board.is_pawn_trapped()
            
            # For main agent, store experience and train
            if current_agent == main_agent:
                next_state = main_agent._encode_state(game)
                reward = calculate_reward(game, main_idx)
                
                # Convert move to action index
                if 0 <= q < board_size and 0 <= r < board_size:
                    action_idx = q * board_size + r
                    
                    # Store experience with priority for winning moves
                    main_agent.store_experience(
                        pre_move_state,
                        action_idx,
                        reward,
                        next_state,
                        game_over
                    )
                    
                    # Train after every move
                    main_agent.train(None)
            
            # Advance to next player
            current_player_idx = (current_player_idx + 1) % 2
            turn_count += 1
        
        # Update statistics
        if game_over:
            final_reward = calculate_reward(game, main_idx)
            if final_reward > 0:
                wins += 1
            elif final_reward < 0:
                losses += 1
            else:
                draws += 1
                
        # Every 100 episodes, add current state to the pool
        if episode % 100 == 0:
            # Create a snapshot of current agent
            snapshot = DQNAI(board_size=board_size, name=f"Historical-{episode}")
            snapshot.q_network.load_state_dict(copy.deepcopy(main_agent.q_network.state_dict()))
            snapshot.epsilon = 0.1  # Fixed exploration for historical agents
            
            # Add to pool
            agent_pool.append(snapshot)
            print(f"Added agent snapshot at episode {episode}, pool size: {len(agent_pool)}")
        
        # Print progress
        if episode % 10 == 0:
            elapsed = time.time() - start_time
            win_rate = wins / episode if episode > 0 else 0
            win_rates.append(win_rate)
            
            # Calculate recent performance (last 100 games)
            recent_win_rate = sum(win_rates[-10:]) / min(10, len(win_rates))
            
            print(f"Episode: {episode}/{episodes} | " 
                  f"Win rate: {win_rate:.2f} | "
                  f"Recent: {recent_win_rate:.2f} | "
                  f"Epsilon: {main_agent.epsilon:.3f} | "
                  f"Time: {elapsed:.1f}s")
        
        # Save model periodically
        if episode % save_interval == 0:
            main_agent.save_model(f"models/DQN_Advanced_{episode}ep.pt")
            print(f"Model saved at episode {episode}")
            
        # Adaptive learning rate - reduce if win rate plateaus
        if episode % 200 == 0 and episode > 0:
            if len(win_rates) >= 20 and abs(win_rates[-1] - win_rates[-20]) < 0.05:
                for param_group in main_agent.optimizer.param_groups:
                    param_group['lr'] *= 0.9
                print(f"Reducing learning rate to {param_group['lr']:.6f}")
    
    # Final statistics
    print("\nAdvanced Self-Play Training complete!")
    print(f"Wins: {wins}/{episodes} ({wins/episodes:.2%})")
    print(f"Losses: {losses}/{episodes} ({losses/episodes:.2%})")
    print(f"Draws: {draws}/{episodes} ({draws/episodes:.2%})")
    
    # Save final model
    main_agent.save_model(f"models/DQN_Advanced_Final_{episodes}ep.pt")
    print(f"Final model saved as DQN_Advanced_Final_{episodes}ep.pt")
    
    return main_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a DQN agent with advanced self-play")
    parser.add_argument("--episodes", type=int, default=2000, 
                        help="Number of training episodes")
    parser.add_argument("--board_size", type=int, default=7,
                        help="Size of the Trike board")
    parser.add_argument("--save_interval", type=int, default=500,
                        help="How often to save the model")
    
    args = parser.parse_args()
    
    trained_agent = train_advanced_self_play(
        episodes=args.episodes,
        board_size=args.board_size,
        save_interval=args.save_interval
    )