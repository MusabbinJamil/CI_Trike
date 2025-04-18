class Pawn:
    def __init__(self, position=None):
        self.position = position

    def move(self, new_position, board):
        if self.is_valid_move(new_position, board):
            board.place_checker(new_position, self)
            self.position = new_position
            return True
        return False

    def is_valid_move(self, new_position, board):
        # Check if the new position is within bounds and not occupied
        if not board.is_within_bounds(new_position):
            return False
        if board.is_occupied(new_position):
            return False
        
        # Check if the move is in a straight line
        return self.is_straight_line_move(new_position)

    def is_straight_line_move(self, new_position):
        # Implement logic to check if the move is straight
        return True  # Placeholder for actual implementation

    def can_move(self, board):
        # Check if there are valid moves available
        for direction in board.get_possible_directions(self.position):
            if self.is_valid_move(direction, board):
                return True
        return False