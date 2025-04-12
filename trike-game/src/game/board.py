class Board:
    def __init__(self, size=5):
        self.size = size
        self.pieces = {}  # Dictionary to hold pieces on the board
        # For triangular board, we'll use axial coordinates
        self.initialize_board()
        
    def initialize_board(self):
        """Initialize the triangular board"""
        self.cells = []
        # Generate all valid triangular grid coordinates
        for q in range(-self.size, self.size+1):
            r_start = max(-self.size, -q-self.size)
            r_end = min(self.size, -q+self.size)
            for r in range(r_start, r_end+1):
                self.cells.append((q, r, -q-r))  # Axial coordinates (q,r,s)
                
    def place_piece(self, piece, position):
        if self.is_valid_position(position):
            self.pieces[position] = piece
            piece.position = position
            return True
        return False

    def move_piece(self, from_position, to_position):
        piece = self.get_piece_at(from_position)
        if piece and self.is_valid_position(to_position) and to_position not in self.pieces:
            del self.pieces[from_position]
            self.pieces[to_position] = piece
            piece.position = to_position
            return True
        return False
            
    def is_valid_position(self, position):
        # For axial coordinates of triangular grid
        q, r = position[:2]
        s = -q-r  # third coordinate in axial system
        return (q, r, s) in self.cells

    def get_piece_at(self, position):
        return self.pieces.get(position, None)
        
    def get_adjacent_positions(self, position):
        """Get all adjacent positions to the given position"""
        q, r = position[:2]
        directions = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        adjacent = []
        for dq, dr in directions:
            adj_pos = (q+dq, r+dr)
            if self.is_valid_position(adj_pos):
                adjacent.append(adj_pos)
        return adjacent

    def reset_board(self):
        self.pieces.clear()  # Clear all pieces from the board

    def __str__(self):
        return f"Triangular Board(size={self.size})"