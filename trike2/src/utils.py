def is_valid_move(board, current_position, target_position):
    # Check if the target position is within the board boundaries
    if not board.is_within_bounds(target_position):
        return False
    
    # Check if the target position is empty
    if not board.is_empty(target_position):
        return False
    
    # Check if the path to the target position is clear
    if not board.is_path_clear(current_position, target_position):
        return False
    
    return True

def calculate_adjacent_checkers(board, pawn_position):
    adjacent_checkers = 0
    for direction in board.get_adjacent_directions():
        adjacent_position = board.get_position_in_direction(pawn_position, direction)
        if board.is_within_bounds(adjacent_position) and not board.is_empty(adjacent_position):
            checker = board.get_checker_at(adjacent_position)
            if checker.color == board.current_player.color:
                adjacent_checkers += 1
    return adjacent_checkers

def calculate_score(board, color, pawn_position):
    """
    Calculate the score for a player:
    - 1 point for each checker of their color adjacent to or underneath the pawn.
    """
    q, r = pawn_position
    score = 0
    # Underneath the pawn
    checker = board.grid.get((q, r))
    if checker is not None and getattr(checker, "color", None) == color:
        score += 1
    # Adjacent checkers
    for dq, dr in board.HEX_DIRECTIONS:
        pos = (q + dq, r + dr)
        checker = board.grid.get(pos)
        if checker is not None and getattr(checker, "color", None) == color:
            score += 1
    return score