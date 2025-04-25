import copy
import random
import math
from collections import defaultdict
from trike_ai.agents.ai_base import AIBase

# Monte Carlo Tree Search (MCTS) Node
class MCTSNode:
    """Node for Monte Carlo Tree Search."""
    
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move  # Move that led to this state
        self.children = []
        self.visits = 0
        self.wins = 0
        self.untried_moves = self._get_valid_moves(game_state)
        self.player = game_state.current_player_index
    
    def _get_valid_moves(self, game_state):
        """Get valid moves for the current state."""
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
    
    def is_fully_expanded(self):
        """Check if all possible child nodes have been created."""
        return len(self.untried_moves) == 0
    
    def is_terminal(self):
        """Check if this node represents a terminal state (game over)."""
        return (self.game_state.pawn.position is not None and 
                self.game_state.board.is_pawn_trapped())
    
    def select_child(self, exploration_weight=1.41):
        """
        Select a child node using UCT formula.
        
        Args:
            exploration_weight (float): Weight for exploration term in UCT
        
        Returns:
            MCTSNode: Selected child node
        """
        # UCT = wins/visits + exploration_weight * sqrt(ln(parent_visits)/visits)
        log_parent_visits = math.log(self.visits)
        
        def uct_score(child):
            exploitation = child.wins / child.visits if child.visits > 0 else 0
            exploration = exploration_weight * math.sqrt(log_parent_visits / child.visits) if child.visits > 0 else float('inf')
            return exploitation + exploration
            
        return max(self.children, key=uct_score)


class MCTSAI(AIBase):
    """
    AI agent using Monte Carlo Tree Search.
    """
    
    def __init__(self, iterations=1000, name="MCTS AI"):
        """
        Initialize the MCTS AI agent.
        
        Args:
            iterations (int): Number of MCTS iterations to run
            name (str): Name of the AI agent
        """
        self.iterations = iterations
        self.name = name
    
    def choose_move(self, game_state):
        """
        Choose the best move using MCTS algorithm.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            tuple: (q, r) coordinates of the best move
        """
        # Check if there are valid moves
        valid_moves = self._get_valid_moves(game_state)
        if not valid_moves:
            return None
        
        # First move optimization - choose center or near-center
        if game_state.pawn.position is None:
            board_size = len(game_state.board.grid) ** 0.5 // 2  # Approximate
            center_q, center_r = int(board_size), int(board_size)
            
            # Try to get a position close to center
            for q, r in sorted(valid_moves, 
                              key=lambda pos: abs(pos[0]-center_q) + abs(pos[1]-center_r)):
                if (q, r) in valid_moves:
                    return (q, r)
        
        # Full MCTS for other moves
        root = MCTSNode(copy.deepcopy(game_state))
        
        # Run MCTS iterations
        for _ in range(self.iterations):
            # 1. Selection
            node = root
            while not node.is_terminal() and node.is_fully_expanded():
                node = node.select_child()
            
            # 2. Expansion
            if not node.is_terminal() and not node.is_fully_expanded():
                move = random.choice(node.untried_moves)
                node.untried_moves.remove(move)
                child_state = self._simulate_move(node.game_state, move)
                node.children.append(MCTSNode(child_state, parent=node, move=move))
                node = node.children[-1]
            
            # 3. Simulation
            result = self._rollout(node.game_state)
            
            # 4. Backpropagation
            while node:
                node.visits += 1
                # Update wins if result is favorable for the player at this node
                current_player = node.player
                opponent = (current_player + 1) % 2
                
                if result[current_player] > result[opponent]:
                    node.wins += 1
                elif result[current_player] == result[opponent]:
                    node.wins += 0.5  # Tie counts as half-win
                
                node = node.parent
        
        # Choose child with most visits
        if root.children:
            best_child = max(root.children, key=lambda c: c.visits)
            return best_child.move
        else:
            # Fallback to random move if MCTS didn't explore any moves
            return random.choice(valid_moves)
    
    def _simulate_move(self, game_state, move):
        """
        Simulate a move on a copy of the game state.
        
        Args:
            game_state: Current game state
            move: (q, r) coordinates for the move
            
        Returns:
            New game state after the move
        """
        # Create a deep copy of the game state
        new_state = copy.deepcopy(game_state)
        
        # Apply the move
        q, r = move
        current_player = new_state.players[new_state.current_player_index]
        
        # If this is first move, place pawn
        if new_state.pawn.position is None:
            new_state.board.place_checker(q, r, current_player)
            new_state.pawn.position = (q, r)
            new_state.board.pawn_position = (q, r)
        else:
            # Regular move - place checker and move pawn
            new_state.board.place_checker(q, r, current_player)
            new_state.pawn.position = (q, r)
            new_state.board.pawn_position = (q, r)
        
        # Swap player
        new_state.current_player_index = (new_state.current_player_index + 1) % 2
        
        return new_state
    
    def _rollout(self, game_state):
        """
        Simulate a random playout from the current state until game end.
        
        Args:
            game_state: Current game state
            
        Returns:
            tuple: (player1_score, player2_score) at the end of the game
        """
        state = copy.deepcopy(game_state)
        
        # Play until the game ends
        while state.pawn.position is None or not state.board.is_pawn_trapped():
            valid_moves = self._get_valid_moves(state)
            if not valid_moves:
                break
                
            # Choose a random move
            move = random.choice(valid_moves)
            
            # Apply the move
            q, r = move
            current_player = state.players[state.current_player_index]
            
            # If this is first move, place pawn
            if state.pawn.position is None:
                state.board.place_checker(q, r, current_player)
                state.pawn.position = (q, r)
                state.board.pawn_position = (q, r)
            else:
                # Regular move - place checker and move pawn
                state.board.place_checker(q, r, current_player)
                state.pawn.position = (q, r)
                state.board.pawn_position = (q, r)
            
            # Swap player
            state.current_player_index = (state.current_player_index + 1) % 2
        
        # Evaluate the final state
        pawn_pos = state.pawn.position
        if pawn_pos:
            neighbors = state.board.get_neighbors(*pawn_pos)
            under = state.board.grid[pawn_pos]
            
            adj = [state.board.grid.get(n) for n in neighbors]
            
            black_score = sum(1 for c in adj + [under] if c and c.color == "black")
            white_score = sum(1 for c in adj + [under] if c and c.color == "white")
            
            # Return scores for each player
            player1 = state.players[0]
            player2 = state.players[1]
            
            player1_score = black_score if player1.color == "black" else white_score
            player2_score = white_score if player1.color == "black" else black_score
            
            return (player1_score, player2_score)
        
        return (0, 0)  # No pawn placed yet (shouldn't happen in a rollout)
    
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
    
    def train(self, training_data):
        """MCTS doesn't require traditional training."""
        pass
    
    def reset(self):
        """Nothing to reset for basic MCTS."""
        pass