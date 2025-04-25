import random
from trike_ai.agents.ai_base import AIBase

class RandomAI(AIBase):
    """
    A simple AI that makes random valid moves.
    Good as a baseline agent for testing.
    """
    
    def __init__(self, name="Random AI"):
        self.name = name
    
    def choose_move(self, game_state):
        """
        Choose a random valid move from the current game state.
        
        Args:
            game_state: Current state of the game including board state, pawn position,
                       current player, and valid moves
        
        Returns:
            tuple: (q, r) coordinates of the chosen move
        """
        # Get all valid moves from the game state
        valid_moves = self._get_valid_moves(game_state)
        
        # Return a random valid move or None if no valid moves exist
        return random.choice(valid_moves) if valid_moves else None
    
    def _get_valid_moves(self, game_state):
        """
        Extract all valid moves from the game state.
        
        Args:
            game_state: Current game state
            
        Returns:
            list: List of valid (q, r) coordinate tuples
        """
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
        """Random AI doesn't learn, so this is a no-op."""
        pass
    
    def reset(self):
        """Random AI has no state to reset."""
        pass