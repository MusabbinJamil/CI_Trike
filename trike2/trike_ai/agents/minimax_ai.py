import copy
from trike_ai.agents.ai_base import AIBase

class MinimaxAI(AIBase):
    """
    AI agent using the Minimax algorithm with alpha-beta pruning.
    """
    
    def __init__(self, depth=3, name="Minimax AI"):
        """
        Initialize the Minimax AI agent.
        
        Args:
            depth (int): Maximum depth for the minimax search
            name (str): Name of the AI agent
        """
        self.depth = depth
        self.name = name
    
    def choose_move(self, game_state):
        """
        Choose the best move using minimax with alpha-beta pruning.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            tuple: (q, r) coordinates of the best move
        """
        valid_moves = self._get_valid_moves(game_state)
        if not valid_moves:
            return None
            
        # First move: choose center or near-center position if possible
        if game_state.pawn.position is None:
            board_size = len(game_state.board.grid) ** 0.5 // 2  # Approximate
            center_q, center_r = int(board_size), int(board_size)
            
            # Try to get a position close to center
            for q, r in sorted(valid_moves, 
                              key=lambda pos: abs(pos[0]-center_q) + abs(pos[1]-center_r)):
                if (q, r) in valid_moves:
                    return (q, r)
            
            # Fallback to any valid move
            return valid_moves[0]
            
        # Use minimax for subsequent moves
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        for move in valid_moves:
            # Create a deep copy of the game state to simulate the move
            next_state = self._simulate_move(game_state, move)
            
            # Get score from minimax algorithm
            score = self._minimax(next_state, self.depth-1, False, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = move
                
            alpha = max(alpha, best_score)
            
        return best_move
    
    def _minimax(self, game_state, depth, is_maximizing, alpha, beta):
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            game_state: Current game state
            depth (int): Current depth in the search tree
            is_maximizing (bool): Whether current player is maximizing
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            
        Returns:
            float: Evaluation score of the position
        """
        # Terminal conditions
        if depth == 0 or self._is_game_over(game_state):
            return self._evaluate_position(game_state)
            
        valid_moves = self._get_valid_moves(game_state)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                next_state = self._simulate_move(game_state, move)
                eval = self._minimax(next_state, depth-1, False, alpha, beta)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                next_state = self._simulate_move(game_state, move)
                eval = self._minimax(next_state, depth-1, True, alpha, beta)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval
    
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
    
    def _is_game_over(self, game_state):
        """Check if the game is over."""
        return game_state.pawn.position is not None and game_state.board.is_pawn_trapped()
    
    def _evaluate_position(self, game_state):
        """
        Evaluate the current board position.
        Returns higher scores for positions favorable to the current player.
        
        Args:
            game_state: Current game state
            
        Returns:
            float: Score of the position
        """
        # If game is over, evaluate final position
        if self._is_game_over(game_state):
            pawn_pos = game_state.pawn.position
            neighbors = game_state.board.get_neighbors(*pawn_pos)
            under = game_state.board.grid[pawn_pos]
            
            adj = [game_state.board.grid.get(n) for n in neighbors]
            
            current_player = game_state.players[game_state.current_player_index]
            opponent_index = (game_state.current_player_index + 1) % 2
            opponent = game_state.players[opponent_index]
            
            current_score = sum(1 for c in adj + [under] if c and c.color == current_player.color)
            opponent_score = sum(1 for c in adj + [under] if c and c.color == opponent.color)
            
            return current_score - opponent_score
            
        # If game is ongoing, evaluate current position
        # This is a simplistic heuristic - you may want to enhance this
        pawn_pos = game_state.pawn.position
        
        # If no pawn yet, return neutral score
        if pawn_pos is None:
            return 0
            
        current_player = game_state.players[game_state.current_player_index]
        
        # Count valid moves - more moves is generally better
        mobility = len(self._get_valid_moves(game_state)) * 0.1
        
        # Look at surrounding checkers
        neighbors = game_state.board.get_neighbors(*pawn_pos)
        under = game_state.board.grid[pawn_pos]
        adj = [game_state.board.grid.get(n) for n in neighbors]
        
        current_adjacent = sum(1 for c in adj if c and c.color == current_player.color)
        opponent_adjacent = sum(1 for c in adj if c and c.color != current_player.color)
        
        # Prefer positions with your own pieces around the pawn
        control_score = current_adjacent - opponent_adjacent
        
        # Combine factors
        return control_score + mobility
    
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
        """Minimax doesn't use traditional training."""
        pass
    
    def reset(self):
        """Reset is not needed for basic minimax."""
        pass