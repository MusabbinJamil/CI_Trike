import numpy as np
from collections import defaultdict, deque

class StrategicEvaluator:
    """
    Evaluates strategic aspects of Trike game positions.
    """
    
    def __init__(self, board_size):
        self.board_size = board_size
        self.center_q = board_size // 2
        self.center_r = board_size // 2
    
    def determine_game_phase(self, game_state):
        """Determine current game phase based on board state."""
        total_pieces = sum(1 for pos in game_state.board.grid if game_state.board.grid[pos])
        total_spaces = len(game_state.board.grid)
        
        fill_ratio = total_pieces / total_spaces
        
        if fill_ratio < 0.2:
            return "early"
        elif fill_ratio < 0.4:
            return "middle"
        elif fill_ratio < 0.7:
            return "mid_late"
        else:
            return "late"
    
    def is_corner(self, q, r, size):
        """Check if position is a corner."""
        corners = [(0, 0), (0, size-1), (size-1, 0)]
        return (q, r) in corners
    
    def is_side(self, q, r, size):
        """Check if position is on the side (but not corner)."""
        if self.is_corner(q, r, size):
            return False
        return q == 0 or r == 0 or q == size-1 or r == size-1
    
    def is_corner_adjacent(self, q, r, size):
        """Check if position is adjacent to a corner."""
        corners = [(0, 0), (0, size-1), (size-1, 0)]
        for cq, cr in corners:
            if abs(q - cq) + abs(r - cr) == 1:
                return True
        return False
    
    def calculate_influence(self, game_state, move, player_color):
        """Calculate how much influence this move gains."""
        q, r = move
        neighbors = game_state.board.get_neighbors(q, r)
        
        # Count controlled points (adjacent empty spaces and friendly pieces)
        controlled = 0
        for nq, nr in neighbors:
            if (nq, nr) in game_state.board.grid:
                neighbor_piece = game_state.board.grid[(nq, nr)]
                if neighbor_piece is None:  # Empty space
                    controlled += 1
                elif neighbor_piece.color == player_color:  # Friendly piece
                    controlled += 0.5
        
        return controlled
    
    def calculate_opponent_influence_reduction(self, game_state, move, player_color):
        """Calculate how much this move reduces opponent influence."""
        q, r = move
        neighbors = game_state.board.get_neighbors(q, r)
        
        reduction = 0
        opponent_color = "black" if player_color == "white" else "white"
        
        for nq, nr in neighbors:
            if (nq, nr) in game_state.board.grid:
                neighbor_piece = game_state.board.grid[(nq, nr)]
                if neighbor_piece and neighbor_piece.color == opponent_color:
                    # This move reduces influence of opponent piece
                    reduction += 1
        
        return reduction
    
    def creates_immediate_trap(self, game_state, move):
        """Check if this move creates an immediate losing trap."""
        # Simulate the move
        test_state = self._simulate_move(game_state, move)
        
        # Check if pawn would be trapped after this move
        if test_state.pawn.position:
            valid_moves = self._get_valid_moves_from_position(test_state, test_state.pawn.position)
            return len(valid_moves) == 0
        
        return False
    
    def separates_regions(self, game_state, move):
        """Check if this move separates the playing area into regions."""
        test_state = self._simulate_move(game_state, move)
        
        # Use flood fill to count connected regions
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        if not empty_spaces:
            return False
        
        regions = self._count_connected_regions(empty_spaces, test_state.board)
        return regions > 1
    
    def evaluate_region_separation(self, game_state, move, player_color):
        """Evaluate the value of region separation."""
        test_state = self._simulate_move(game_state, move)
        
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        regions = self._get_connected_regions(empty_spaces, test_state.board)
        
        # Evaluate each region
        total_score = 0
        for region in regions:
            region_score = self._evaluate_region_control(region, test_state, player_color)
            total_score += region_score
        
        return total_score
    
    def identify_pockets(self, game_state):
        """Identify potential trap pockets on the board."""
        pockets = []
        empty_spaces = {pos for pos in game_state.board.grid 
                       if game_state.board.grid[pos] is None}
        
        # Look for small connected regions (potential pockets)
        regions = self._get_connected_regions(empty_spaces, game_state.board)
        
        for region in regions:
            if len(region) <= 3:  # Small regions are potential pockets
                pocket_info = {
                    'positions': region,
                    'size': len(region),
                    'controlling_color': self._determine_pocket_controller(region, game_state)
                }
                pockets.append(pocket_info)
        
        return pockets
    
    def is_move_in_pocket(self, move, pocket):
        """Check if move is in a specific pocket."""
        return move in pocket['positions']
    
    def is_enemy_pocket(self, pocket, player_color):
        """Check if pocket is controlled by enemy."""
        return pocket['controlling_color'] and pocket['controlling_color'] != player_color
    
    def evaluate_stone_burial(self, game_state, move, player_color):
        """Evaluate how this move affects stone burial."""
        # Check if this move buries opponent stones or keeps own stones accessible
        q, r = move
        neighbors = game_state.board.get_neighbors(q, r)
        
        burial_score = 0
        opponent_color = "black" if player_color == "white" else "white"
        
        for nq, nr in neighbors:
            if (nq, nr) in game_state.board.grid:
                neighbor_piece = game_state.board.grid[(nq, nr)]
                if neighbor_piece:
                    # Check if this piece would become buried
                    neighbor_neighbors = game_state.board.get_neighbors(nq, nr)
                    occupied_neighbors = sum(1 for nnq, nnr in neighbor_neighbors 
                                           if (nnq, nnr) in game_state.board.grid and 
                                           game_state.board.grid[(nnq, nnr)] is not None)
                    
                    if occupied_neighbors >= len(neighbor_neighbors) - 1:  # Would be mostly buried
                        if neighbor_piece.color == opponent_color:
                            burial_score += 1  # Good to bury opponent
                        else:
                            burial_score -= 1  # Bad to bury own piece
        
        return burial_score
    
    def evaluate_corridor_control(self, game_state, move):
        """Evaluate control over movement corridors."""
        # Check how this move affects pawn movement options
        if game_state.pawn.position is None:
            return 0
        
        current_moves = len(self._get_valid_moves_from_position(game_state, game_state.pawn.position))
        
        test_state = self._simulate_move(game_state, move)
        future_moves = len(self._get_valid_moves_from_position(test_state, test_state.pawn.position))
        
        return current_moves - future_moves  # Preference for maintaining options
    
    def closes_corridor(self, game_state, move):
        """Check if this move closes off a corridor."""
        return self.separates_regions(game_state, move)
    
    def evaluate_closing_penalty(self, game_state, move, player_color):
        """Evaluate penalty for closing corridors."""
        # Closing is bad if it gives opponent choice of direction
        regions = self._get_regions_after_move(game_state, move)
        
        penalty = 0
        for region in regions:
            region_control = self._evaluate_region_control(region, game_state, player_color)
            if region_control < 0:  # Opponent-favoring region
                penalty += abs(region_control)
        
        return penalty
    
    def evaluate_endpoint_control(self, game_state, move, player_color):
        """Evaluate control over potential game endpoints."""
        # Look for positions where game might end
        test_state = self._simulate_move(game_state, move)
        
        endpoint_score = 0
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        for pos in empty_spaces:
            if self._could_be_endpoint(pos, test_state):
                control = self._evaluate_position_control(pos, test_state, player_color)
                endpoint_score += control
        
        return endpoint_score
    
    def sets_trap(self, game_state, move, player_color):
        """Check if this move sets a trap."""
        test_state = self._simulate_move(game_state, move)
        
        # Look for positions where pawn could get trapped favorably
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        for pos in empty_spaces:
            if self._is_potential_trap(pos, test_state, player_color):
                return True
        
        return False
    
    def extends_trap(self, game_state, move, player_color):
        """Check if this move extends an existing trap."""
        # Look for nearby friendly pieces that could form extended trap
        q, r = move
        neighbors = game_state.board.get_neighbors(q, r)
        
        friendly_neighbors = 0
        for nq, nr in neighbors:
            if (nq, nr) in game_state.board.grid:
                piece = game_state.board.grid[(nq, nr)]
                if piece and piece.color == player_color:
                    friendly_neighbors += 1
        
        return friendly_neighbors >= 2  # Extends if connecting to multiple friendly pieces
    
    def count_traps_created(self, game_state, move, player_color):
        """Count how many traps this move creates."""
        test_state = self._simulate_move(game_state, move)
        
        trap_count = 0
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        for pos in empty_spaces:
            if self._is_potential_trap(pos, test_state, player_color):
                trap_count += 1
        
        return trap_count
    
    def evaluate_trap_sacrifice(self, game_state, move, player_color):
        """Evaluate sacrificing own trap to eliminate bigger opponent trap."""
        # Check if this move eliminates opponent traps while giving up own
        opponent_color = "black" if player_color == "white" else "white"
        
        own_traps_lost = 0
        opponent_traps_eliminated = 0
        
        test_state = self._simulate_move(game_state, move)
        
        # Count trap changes
        for pos in game_state.board.grid:
            if game_state.board.grid[pos] is None:
                was_own_trap = self._is_potential_trap(pos, game_state, player_color)
                was_opponent_trap = self._is_potential_trap(pos, game_state, opponent_color)
                
                is_own_trap = self._is_potential_trap(pos, test_state, player_color)
                is_opponent_trap = self._is_potential_trap(pos, test_state, opponent_color)
                
                if was_own_trap and not is_own_trap:
                    own_traps_lost += 1
                if was_opponent_trap and not is_opponent_trap:
                    opponent_traps_eliminated += 1
        
        # Sacrifice is good if we eliminate more opponent traps than we lose
        return opponent_traps_eliminated - own_traps_lost
    
    def defuses_by_inside_play(self, game_state, move, player_color):
        """Check if move defuses trap by playing inside it."""
        # Check if move is in a position that was previously a trap
        opponent_color = "black" if player_color == "white" else "white"
        return self._is_potential_trap(move, game_state, opponent_color)
    
    def defuses_by_downstream_trap(self, game_state, move, player_color):
        """Check if move sets a downstream trap that defuses upstream threat."""
        # This is complex - simplified version checks if creating trap in less threatened area
        if self.sets_trap(game_state, move, player_color):
            # Check if there are opponent traps "upstream" (closer to current pawn position)
            if game_state.pawn.position:
                pawn_q, pawn_r = game_state.pawn.position
                move_q, move_r = move
                
                # Simplified: if move is further from pawn, it might be downstream
                pawn_distance = abs(pawn_q - move_q) + abs(pawn_r - move_r)
                return pawn_distance > 2
        
        return False
    
    def locks_away_traps(self, game_state, move, player_color):
        """Check if move locks away opponent traps from pawn."""
        # Check if move separates opponent traps from pawn
        if not self.separates_regions(game_state, move):
            return False
        
        test_state = self._simulate_move(game_state, move)
        
        # Find which region contains the pawn
        pawn_region = self._find_pawn_region(test_state)
        if not pawn_region:
            return False
        
        # Check if opponent traps are in other regions
        opponent_color = "black" if player_color == "white" else "white"
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        
        regions = self._get_connected_regions(empty_spaces, test_state.board)
        
        for region in regions:
            if region != pawn_region:
                for pos in region:
                    if self._is_potential_trap(pos, test_state, opponent_color):
                        return True
        
        return False
    
    # Helper methods
    def _simulate_move(self, game_state, move):
        """Simulate a move and return new game state."""
        import copy
        test_state = copy.deepcopy(game_state)
        
        q, r = move
        current_player = test_state.players[test_state.current_player_index]
        
        # Place checker and move pawn
        test_state.board.place_checker(q, r, current_player)
        test_state.pawn.position = (q, r)
        test_state.board.pawn_position = (q, r)
        
        return test_state
    
    def _get_valid_moves_from_position(self, game_state, position):
        """Get valid moves from a specific position."""
        if position is None:
            return []
        
        valid_moves = []
        q_from, r_from = position
        
        for (q, r) in game_state.board.grid:
            if game_state.board.is_valid_move(q_from, r_from, q, r):
                valid_moves.append((q, r))
        
        return valid_moves
    
    def _count_connected_regions(self, empty_spaces, board):
        """Count number of connected regions in empty spaces."""
        if not empty_spaces:
            return 0
        
        visited = set()
        regions = 0
        
        for pos in empty_spaces:
            if pos not in visited:
                self._flood_fill(pos, empty_spaces, visited, board)
                regions += 1
        
        return regions
    
    def _get_connected_regions(self, empty_spaces, board):
        """Get list of connected regions."""
        if not empty_spaces:
            return []
        
        visited = set()
        regions = []
        
        for pos in empty_spaces:
            if pos not in visited:
                region = set()
                self._flood_fill(pos, empty_spaces, visited, board, region)
                regions.append(region)
        
        return regions
    
    def _flood_fill(self, start_pos, empty_spaces, visited, board, region=None):
        """Flood fill to find connected region."""
        stack = [start_pos]
        
        while stack:
            pos = stack.pop()
            if pos in visited or pos not in empty_spaces:
                continue
            
            visited.add(pos)
            if region is not None:
                region.add(pos)
            
            # Add neighbors
            neighbors = board.get_neighbors(*pos)
            for neighbor in neighbors:
                if neighbor in empty_spaces and neighbor not in visited:
                    stack.append(neighbor)
    
    def _evaluate_region_control(self, region, game_state, player_color):
        """Evaluate who controls a region."""
        if not region:
            return 0
        
        player_influence = 0
        opponent_influence = 0
        opponent_color = "black" if player_color == "white" else "white"
        
        for pos in region:
            neighbors = game_state.board.get_neighbors(*pos)
            for neighbor in neighbors:
                if neighbor in game_state.board.grid:
                    piece = game_state.board.grid[neighbor]
                    if piece:
                        if piece.color == player_color:
                            player_influence += 1
                        else:
                            opponent_influence += 1
        
        return player_influence - opponent_influence
    
    def _determine_pocket_controller(self, region, game_state):
        """Determine which player controls a pocket."""
        if not region:
            return None
        
        color_counts = defaultdict(int)
        
        for pos in region:
            neighbors = game_state.board.get_neighbors(*pos)
            for neighbor in neighbors:
                if neighbor in game_state.board.grid:
                    piece = game_state.board.grid[neighbor]
                    if piece:
                        color_counts[piece.color] += 1
        
        if not color_counts:
            return None
        
        return max(color_counts.keys(), key=lambda c: color_counts[c])
    
    def _get_regions_after_move(self, game_state, move):
        """Get regions that would exist after a move."""
        test_state = self._simulate_move(game_state, move)
        empty_spaces = {pos for pos in test_state.board.grid 
                       if test_state.board.grid[pos] is None}
        return self._get_connected_regions(empty_spaces, test_state.board)
    
    def _could_be_endpoint(self, position, game_state):
        """Check if position could be a game endpoint."""
        # Simplified: positions with few neighbors are potential endpoints
        neighbors = game_state.board.get_neighbors(*position)
        empty_neighbors = sum(1 for n in neighbors 
                            if n in game_state.board.grid and 
                            game_state.board.grid[n] is None)
        return empty_neighbors <= 1
    
    def _evaluate_position_control(self, position, game_state, player_color):
        """Evaluate control over a specific position."""
        neighbors = game_state.board.get_neighbors(*position)
        
        player_neighbors = 0
        opponent_neighbors = 0
        opponent_color = "black" if player_color == "white" else "white"
        
        for neighbor in neighbors:
            if neighbor in game_state.board.grid:
                piece = game_state.board.grid[neighbor]
                if piece:
                    if piece.color == player_color:
                        player_neighbors += 1
                    else:
                        opponent_neighbors += 1
        
        return player_neighbors - opponent_neighbors
    
    def _is_potential_trap(self, position, game_state, player_color):
        """Check if position is a potential trap for the player."""
        neighbors = game_state.board.get_neighbors(*position)
        
        # Count friendly pieces around position
        friendly_count = 0
        total_neighbors = 0
        
        for neighbor in neighbors:
            if neighbor in game_state.board.grid:
                total_neighbors += 1
                piece = game_state.board.grid[neighbor]
                if piece and piece.color == player_color:
                    friendly_count += 1
        
        # Position is potential trap if majority of neighbors are friendly
        return friendly_count > total_neighbors / 2
    
    def _find_pawn_region(self, game_state):
        """Find which region contains the pawn."""
        if not game_state.pawn.position:
            return None
        
        empty_spaces = {pos for pos in game_state.board.grid 
                       if game_state.board.grid[pos] is None}
        empty_spaces.add(game_state.pawn.position)  # Include pawn position
        
        regions = self._get_connected_regions(empty_spaces, game_state.board)
        
        for region in regions:
            if game_state.pawn.position in region:
                return region
        
        return None