import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import copy
import os
from trike_ai.agents.ai_base import AIBase

class QNetwork(nn.Module):
    """Neural network for DQN"""
    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, action_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        return self.fc4(x)

class ReplayBuffer:
    """Experience replay buffer"""
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
    
    def __len__(self):
        return len(self.buffer)

class DQNAI(AIBase):
    """
    Deep Q-Network AI agent for Trike.
    """
    
    def __init__(self, board_size=7, name="DQN AI", learning_rate=0.001, 
                 gamma=0.99, epsilon=1.0, epsilon_min=0.01, epsilon_decay=0.995):
        """
        Initialize the DQN AI agent.
        
        Args:
            board_size: Size of the Trike board
            name: Name of the AI agent
            learning_rate: Learning rate for the neural network
            gamma: Discount factor for future rewards
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Rate at which epsilon decays
        """
        self.name = name
        self.board_size = board_size
        self.state_size = 3 * board_size * board_size + 1  # 3 channels + player
        self.action_size = board_size * board_size  # All possible board positions
        
        # DQN parameters
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.update_target_every = 10
        self.batch_size = 64
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize networks
        self.q_network = QNetwork(self.state_size, self.action_size).to(self.device)
        self.target_network = QNetwork(self.state_size, self.action_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        # Replay memory
        self.memory = ReplayBuffer()
        
        # Training counters
        self.train_step = 0
        self.games_played = 0
    
    def choose_move(self, game_state):
        """
        Choose a move based on the current game state.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            tuple: (q, r) coordinates of the chosen move
        """
        valid_moves = self._get_valid_moves(game_state)
        if not valid_moves:
            return None
        
        # Exploration: random move
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_moves)
        
        # Exploitation: best move according to Q-values
        state_tensor = self._encode_state(game_state)
        with torch.no_grad():
            q_values = self.q_network(state_tensor).cpu().numpy().flatten()
        
        # Map valid moves to action indices
        action_indices = self._moves_to_indices(valid_moves, game_state)
        
        # Choose the best valid action
        best_action_value = float('-inf')
        best_move = None
        
        for move, action_idx in zip(valid_moves, action_indices):
            if q_values[action_idx] > best_action_value:
                best_action_value = q_values[action_idx]
                best_move = move
        
        return best_move if best_move else random.choice(valid_moves)
    
    def train(self, training_data):
        """
        Update network weights based on a batch of experiences.
        This is called during the training loop.
        
        Args:
            training_data: None (experience is stored internally)
        """
        if len(self.memory) < self.batch_size:
            return
        
        # Sample random batch from memory
        batch = self.memory.sample(self.batch_size)
        
        # Separate batch into components
        states = torch.cat([experience[0] for experience in batch]).to(self.device)
        actions = torch.tensor([experience[1] for experience in batch], dtype=torch.long).to(self.device)
        rewards = torch.tensor([experience[2] for experience in batch], dtype=torch.float32).to(self.device)
        next_states = torch.cat([experience[3] for experience in batch]).to(self.device)
        dones = torch.tensor([experience[4] for experience in batch], dtype=torch.float32).to(self.device)
        
        # Get current Q values for chosen actions
        q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Get max Q values for next states from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
        
        # Compute target Q values
        target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss and update network
        loss = self.criterion(q_values.squeeze(), target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Update target network
        self.train_step += 1
        if self.train_step % self.update_target_every == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def store_experience(self, state, action_idx, reward, next_state, done):
        """
        Store experience in replay buffer.
        
        Args:
            state: Current state tensor
            action_idx: Index of the action taken
            reward: Reward received
            next_state: Next state tensor
            done: Whether the game is over
        """
        self.memory.add(state, action_idx, reward, next_state, done)
    
    def reset(self):
        """Reset the agent for a new game."""
        # Increment games played
        self.games_played += 1
    
    def save_model(self, path="models"):
        """Save the model to disk."""
        if not os.path.exists(path):
            os.makedirs(path)
        torch.save(self.q_network.state_dict(), f"{path}/{self.name.replace(' ', '_')}.pt")
    
    def load_model(self, path):
        """Load the model from disk."""
        self.q_network.load_state_dict(torch.load(path))
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def _get_valid_moves(self, game_state):
        """Get valid moves from the game state."""
        # If this is the first move (pawn not placed yet)
        if game_state.pawn.position is None:
            # All empty cells are valid for the first move
            return [(q, r) for (q, r) in game_state.board.grid 
                   if game_state.board.grid[(q, r)] is None]
        
        # Otherwise, get valid moves from current pawn position
        valid_moves = []
        q_from, r_from = game_state.pawn.position
        
        for (q, r) in game_state.board.grid:
            if game_state.board.is_valid_move(q_from, r_from, q, r):
                valid_moves.append((q, r))
                
        return valid_moves
    
    def _encode_state(self, game_state):
        """
        Convert game state to a tensor for neural network input.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            torch.Tensor: Encoded game state
        """
        # Create a 3D representation of the board
        # Channel 0: Player 1 pieces
        # Channel 1: Player 2 pieces
        # Channel 2: Pawn position
        state = np.zeros((3, self.board_size, self.board_size))
        
        # Add pieces to appropriate channels
        for (q, r), checker in game_state.board.grid.items():
            if 0 <= q < self.board_size and 0 <= r < self.board_size:
                if checker is not None:
                    if checker.color == game_state.players[0].color:
                        state[0, q, r] = 1
                    else:
                        state[1, q, r] = 1
        
        # Add pawn position
        if game_state.pawn.position:
            q, r = game_state.pawn.position
            if 0 <= q < self.board_size and 0 <= r < self.board_size:
                state[2, q, r] = 1
        
        # Flatten state and add current player info
        state_flat = state.flatten()
        state_flat = np.append(state_flat, game_state.current_player_index)
        
        return torch.FloatTensor(state_flat).unsqueeze(0).to(self.device)
    
    def _moves_to_indices(self, moves, game_state):
        """
        Convert (q,r) moves to action indices for the neural network.
        
        Args:
            moves: List of (q,r) coordinate tuples
            game_state: Current state of the game
            
        Returns:
            list: List of action indices
        """
        indices = []
        for q, r in moves:
            if 0 <= q < self.board_size and 0 <= r < self.board_size:
                idx = q * self.board_size + r
                indices.append(idx)
        return indices
    
    def _index_to_move(self, index):
        """Convert action index back to (q,r) coordinates."""
        q = index // self.board_size
        r = index % self.board_size
        return (q, r)