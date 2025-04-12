class GamePiece:
    def __init__(self, name, color, player_id):
        self.name = name
        self.color = color
        self.player_id = player_id
        self.position = None

    def move(self, new_position):
        raise NotImplementedError("This method should be overridden by subclasses.")
        
    def __str__(self):
        return f"{self.color} {self.name} at {self.position}"

class Stone(GamePiece):
    """Basic piece for the Trike game"""
    def __init__(self, color, player_id):
        super().__init__("Stone", color, player_id)
        
    def move(self, new_position):
        old_position = self.position
        self.position = new_position
        return old_position, new_position
        
    def get_possible_moves(self, board):
        """Get all possible moves for this piece"""
        if not self.position:
            return []
            
        # Basic movement: can move to any adjacent empty cell
        possible_moves = []
        adjacent_positions = board.get_adjacent_positions(self.position)
        
        for pos in adjacent_positions:
            if not board.get_piece_at(pos):
                possible_moves.append(pos)
                
        # Jumping: can jump over adjacent pieces to an empty cell
        for adj_pos in adjacent_positions:
            adj_piece = board.get_piece_at(adj_pos)
            if adj_piece:
                # Calculate the position on the other side of the jumped piece
                q1, r1 = self.position[:2]
                q2, r2 = adj_pos[:2]
                # Direction of movement
                dq, dr = q2 - q1, r2 - r1
                # Position after the jump
                jump_pos = (q2 + dq, r2 + dr)
                
                if board.is_valid_position(jump_pos) and not board.get_piece_at(jump_pos):
                    possible_moves.append(jump_pos)
                    
        return possible_moves