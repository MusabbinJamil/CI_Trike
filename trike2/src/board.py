class Board:
    HEX_DIRECTIONS = [
        (1, 0), (1, -1), (0, -1),
        (-1, 0), (-1, 1), (0, 1)
    ]

    def __init__(self, size):
        self.size = size
        self.grid = self.create_grid()
        self.pawn_position = None

    def create_grid(self):
        # Only valid hexes within a triangle of given side length
        grid = {}
        for q in range(self.size):
            for r in range(self.size - q):
                grid[(q, r)] = None
        return grid

    def is_valid_position(self, q, r):
        return (q, r) in self.grid

    def place_checker(self, q, r, checker):
        if self.is_valid_position(q, r) and self.grid[(q, r)] is None:
            self.grid[(q, r)] = checker
            return True
        return False

    def is_valid_move(self, q_from, r_from, q_to, r_to):
        if not self.is_valid_position(q_to, r_to):
            return False
        if self.grid[(q_to, r_to)] is not None:
            return False
        # Check straight line and no jumping
        dq = q_to - q_from
        dr = r_to - r_from
        for direction in self.HEX_DIRECTIONS:
            for dist in range(1, self.size):
                if (direction[0]*dist, direction[1]*dist) == (dq, dr):
                    # Check all intermediate hexes are empty
                    for step in range(1, dist):
                        mid = (q_from + direction[0]*step, r_from + direction[1]*step)
                        if self.grid.get(mid) is not None:
                            return False
                    return True
        return False

    def move_pawn(self, q_from, r_from, q_to, r_to):
        if self.is_valid_move(q_from, r_from, q_to, r_to):
            self.pawn_position = (q_to, r_to)
            return True
        return False

    def get_adjacent_checkers(self, q, r):
        adjacent = []
        for dq, dr in self.HEX_DIRECTIONS:
            pos = (q + dq, r + dr)
            if self.is_valid_position(*pos) and self.grid[pos] is not None:
                adjacent.append(self.grid[pos])
        return adjacent

    def is_pawn_trapped(self):
        if self.pawn_position is None:
            return False
        q, r = self.pawn_position
        for dq, dr in self.HEX_DIRECTIONS:
            pos = (q + dq, r + dr)
            if self.is_valid_position(*pos) and self.grid[pos] is None:
                return False
        return True
    
    def get_neighbors(self, q, r):
        # Hex grid directions (pointy-topped)
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        neighbors = []
        for dq, dr in directions:
            neighbor = (q + dq, r + dr)
            if neighbor in self.grid:
                neighbors.append(neighbor)
        return neighbors

    def reset(self):
        # Clear all checkers from the board
        for pos in self.grid:
            self.grid[pos] = None
        # Reset pawn position if you store it here
        if hasattr(self, 'pawn_position'):
            self.pawn_position = None