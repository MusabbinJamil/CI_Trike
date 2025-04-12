class Rules:
    def __init__(self, board):
        self.board = board
        
    def validate_move(self, player_id, from_position, to_position):
        """Validate if the move is legal according to Trike rules"""
        piece = self.board.get_piece_at(from_position)
        
        # Check if piece exists and belongs to the current player
        if not piece or piece.player_id != player_id:
            return False
            
        # Get all possible moves for this piece
        possible_moves = piece.get_possible_moves(self.board)
        
        # Check if the target position is in the possible moves
        return to_position in possible_moves
        
    def execute_move(self, from_position, to_position):
        """Execute a move and handle captures"""
        piece = self.board.get_piece_at(from_position)
        if not piece:
            return False
            
        # Calculate if this is a jump move
        q1, r1 = from_position[:2]
        q2, r2 = to_position[:2]
        dq, dr = q2 - q1, r2 - r1
        
        # If distance is 2 squares, it's a jump
        if abs(dq) == 2 or abs(dr) == 2 or abs(dq + dr) == 2:
            # Calculate the jumped position
            jumped_pos = (q1 + dq//2, r1 + dr//2)
            jumped_piece = self.board.get_piece_at(jumped_pos)
            
            # Remove the jumped piece (capture)
            if jumped_piece:
                del self.board.pieces[jumped_pos]
        
        # Move the piece
        return self.board.move_piece(from_position, to_position)
        
    def is_game_over(self, state):
        """Check if the game is over"""
        # Game is over when one player has no more pieces
        # or cannot make any valid moves
        players_with_moves = set()
        
        for position, piece in self.board.pieces.items():
            possible_moves = piece.get_possible_moves(self.board)
            if possible_moves:
                players_with_moves.add(piece.player_id)
                
        # If any player has no possible moves, the game is over
        if len(players_with_moves) < len(state.players):
            return True
            
        # Count pieces for each player
        player_pieces = {}
        for player in state.players:
            player_pieces[player.id] = 0
            
        for piece in self.board.pieces.values():
            if piece.player_id in player_pieces:
                player_pieces[piece.player_id] += 1
                
        # If any player has no pieces, the game is over
        return any(count == 0 for count in player_pieces.values())
        
    def get_winner(self, state):
        """Determine the winner based on piece count"""
        player_pieces = {}
        for player in state.players:
            player_pieces[player.id] = 0
            
        for piece in self.board.pieces.values():
            if piece.player_id in player_pieces:
                player_pieces[piece.player_id] += 1
                
        # Player with most pieces wins
        if player_pieces:
            max_pieces = max(player_pieces.values())
            winners = [player_id for player_id, count in player_pieces.items() 
                      if count == max_pieces]
            return winners
        return []