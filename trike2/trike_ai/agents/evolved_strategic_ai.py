import random
import copy
import numpy as np
from .ai_base import AIBase
from ..training.strategic_evaluator import StrategicEvaluator

class EvolvedStrategicAI(AIBase):
    """
    AI that uses evolved strategic parameters for different game phases and tactical situations.
    """
    
    def __init__(self, name="EvolvedStrategicAI", board_size=7, strategy_weights=None):
        # Fix: Call super().__init__() without arguments if AIBase doesn't accept parameters
        super().__init__()
        
        # Set attributes directly
        self.name = name
        self.board_size = board_size
        
        # Strategic weights for different situations (0-100 each)
        if strategy_weights is None:
            strategy_weights = self._generate_random_weights()
        
        self.strategy_weights = strategy_weights
        self.evaluator = StrategicEvaluator(board_size)
        
    def _generate_random_weights(self):
        """Generate random strategic weights for evolution."""
        return {
            # Early game strategies
            'center_control': random.randint(0, 100),
            'corner_avoidance': random.randint(0, 100),
            'side_preference': random.randint(0, 100),
            'corner_capture': random.randint(0, 100),
            
            # Middle game strategies
            'influence_maximization': random.randint(0, 100),
            'opponent_influence_reduction': random.randint(0, 100),
            'trap_avoidance': random.randint(0, 100),
            'region_separation_awareness': random.randint(0, 100),
            
            # Mid-late game strategies
            'pocket_identification': random.randint(0, 100),
            'enemy_pocket_filling': random.randint(0, 100),
            'own_pocket_avoidance': random.randint(0, 100),
            'stone_burial_strategy': random.randint(0, 100),
            
            # Late game strategies
            'corridor_control': random.randint(0, 100),
            'closing_avoidance': random.randint(0, 100),
            'endpoint_manipulation': random.randint(0, 100),
            
            # Trap strategies
            'set_trap': random.randint(0, 100),
            'extend_trap': random.randint(0, 100),
            'multiple_traps': random.randint(0, 100),
            'sacrifice_trap': random.randint(0, 100),
            'defuse_inside': random.randint(0, 100),
            'defuse_downstream': random.randint(0, 100),
            'lock_away_traps': random.randint(0, 100),
        }
    
    def choose_move(self, game_state):
        """Choose move based on evolved strategic weights."""
        valid_moves = self._get_valid_moves(game_state)
        if not valid_moves:
            return None
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        
        # Evaluate each move using strategic criteria
        move_scores = {}
        game_phase = self.evaluator.determine_game_phase(game_state)
        
        for move in valid_moves:
            score = self._evaluate_move(game_state, move, game_phase)
            move_scores[move] = score
        
        # Choose best move
        best_move = max(move_scores.keys(), key=lambda m: move_scores[m])
        return best_move
    
    def train(self, game_state):
        """
        Implement abstract train method from AIBase.
        EvolvedStrategicAI doesn't need training - it uses pre-evolved weights.
        This method is called by the base class but does nothing for this AI type.
        """
        # No training needed - weights are evolved externally
        pass
    
    def _evaluate_move(self, game_state, move, game_phase):
        """Evaluate a move based on strategic weights and game phase."""
        score = 0
        q, r = move
        
        # Early game evaluation
        if game_phase == "early":
            score += self._evaluate_early_game(game_state, move)
        
        # Middle game evaluation
        elif game_phase == "middle":
            score += self._evaluate_middle_game(game_state, move)
        
        # Mid-late game evaluation
        elif game_phase == "mid_late":
            score += self._evaluate_mid_late_game(game_state, move)
        
        # Late game evaluation
        elif game_phase == "late":
            score += self._evaluate_late_game(game_state, move)
        
        # Always evaluate trap strategies
        score += self._evaluate_trap_strategies(game_state, move)
        
        return score
    
    def _evaluate_early_game(self, game_state, move):
        """Evaluate early game strategies."""
        score = 0
        q, r = move
        size = game_state.board.size
        center_q, center_r = size // 2, size // 2
        
        # Center control
        distance_to_center = abs(q - center_q) + abs(r - center_r)
        if distance_to_center == 0:
            score += self.strategy_weights['center_control'] * 0.01
        
        # Corner avoidance
        if self.evaluator.is_corner(q, r, size):
            score -= self.strategy_weights['corner_avoidance'] * 0.01
        
        # Side preference (better than corner, worse than center)
        if self.evaluator.is_side(q, r, size):
            score += self.strategy_weights['side_preference'] * 0.005
        
        # Corner capture (one space from corner)
        if self.evaluator.is_corner_adjacent(q, r, size):
            score += self.strategy_weights['corner_capture'] * 0.008
        
        return score
    
    def _evaluate_middle_game(self, game_state, move):
        """Evaluate middle game strategies."""
        score = 0
        q, r = move
        
        # Influence maximization
        influence = self.evaluator.calculate_influence(game_state, move, self.get_color(game_state))
        score += influence * self.strategy_weights['influence_maximization'] * 0.01
        
        # Opponent influence reduction
        opponent_influence = self.evaluator.calculate_opponent_influence_reduction(game_state, move, self.get_color(game_state))
        score += opponent_influence * self.strategy_weights['opponent_influence_reduction'] * 0.01
        
        # Trap avoidance
        if self.evaluator.creates_immediate_trap(game_state, move):
            score -= self.strategy_weights['trap_avoidance'] * 0.02
        
        # Region separation awareness
        if self.evaluator.separates_regions(game_state, move):
            separation_score = self.evaluator.evaluate_region_separation(game_state, move, self.get_color(game_state))
            score += separation_score * self.strategy_weights['region_separation_awareness'] * 0.01
        
        return score
    
    def _evaluate_mid_late_game(self, game_state, move):
        """Evaluate mid-late game strategies."""
        score = 0
        q, r = move
        
        # Pocket identification and manipulation
        pockets = self.evaluator.identify_pockets(game_state)
        
        for pocket in pockets:
            if self.evaluator.is_move_in_pocket(move, pocket):
                if self.evaluator.is_enemy_pocket(pocket, self.get_color(game_state)):
                    # Fill enemy pockets
                    score += self.strategy_weights['enemy_pocket_filling'] * 0.015
                else:
                    # Avoid own pockets
                    score -= self.strategy_weights['own_pocket_avoidance'] * 0.015
        
        # Stone burial strategy
        burial_score = self.evaluator.evaluate_stone_burial(game_state, move, self.get_color(game_state))
        score += burial_score * self.strategy_weights['stone_burial_strategy'] * 0.01
        
        return score
    
    def _evaluate_late_game(self, game_state, move):
        """Evaluate late game strategies."""
        score = 0
        
        # Corridor control
        corridor_value = self.evaluator.evaluate_corridor_control(game_state, move)
        score += corridor_value * self.strategy_weights['corridor_control'] * 0.01
        
        # Closing avoidance
        if self.evaluator.closes_corridor(game_state, move):
            closing_penalty = self.evaluator.evaluate_closing_penalty(game_state, move, self.get_color(game_state))
            score -= closing_penalty * self.strategy_weights['closing_avoidance'] * 0.01
        
        # Endpoint manipulation
        endpoint_value = self.evaluator.evaluate_endpoint_control(game_state, move, self.get_color(game_state))
        score += endpoint_value * self.strategy_weights['endpoint_manipulation'] * 0.01
        
        return score
    
    def _evaluate_trap_strategies(self, game_state, move):
        """Evaluate trap-related strategies."""
        score = 0
        
        # Set trap
        if self.evaluator.sets_trap(game_state, move, self.get_color(game_state)):
            score += self.strategy_weights['set_trap'] * 0.02
        
        # Extend trap
        if self.evaluator.extends_trap(game_state, move, self.get_color(game_state)):
            score += self.strategy_weights['extend_trap'] * 0.015
        
        # Multiple traps with one move
        trap_count = self.evaluator.count_traps_created(game_state, move, self.get_color(game_state))
        if trap_count > 1:
            score += self.strategy_weights['multiple_traps'] * 0.025 * (trap_count - 1)
        
        # Sacrifice trap to eliminate bigger opponent trap
        sacrifice_value = self.evaluator.evaluate_trap_sacrifice(game_state, move, self.get_color(game_state))
        score += sacrifice_value * self.strategy_weights['sacrifice_trap'] * 0.01
        
        # Defuse by playing inside
        if self.evaluator.defuses_by_inside_play(game_state, move, self.get_color(game_state)):
            score += self.strategy_weights['defuse_inside'] * 0.018
        
        # Defuse by setting different trap downstream
        if self.evaluator.defuses_by_downstream_trap(game_state, move, self.get_color(game_state)):
            score += self.strategy_weights['defuse_downstream'] * 0.016
        
        # Lock away traps
        if self.evaluator.locks_away_traps(game_state, move, self.get_color(game_state)):
            score += self.strategy_weights['lock_away_traps'] * 0.017
        
        return score
    
    def _get_valid_moves(self, game_state):
        """Get valid moves from the game state."""
        if game_state.pawn.position is None:
            return [(q, r) for (q, r) in game_state.board.grid 
                   if game_state.board.grid[(q, r)] is None]
        
        valid_moves = []
        q_from, r_from = game_state.pawn.position
        
        for (q, r) in game_state.board.grid:
            if game_state.board.is_valid_move(q_from, r_from, q, r):
                valid_moves.append((q, r))
                
        return valid_moves
    
    def get_color(self, game_state):
        """Get this AI's color in the current game."""
        # Find which player this AI is
        for i, player in enumerate(game_state.players):
            if hasattr(player, 'ai') and player.ai == self:
                return player.color
        
        # Fallback - assume we're the current player
        current_player = game_state.players[game_state.current_player_index]
        return current_player.color
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'board_size': self.board_size,
            'strategy_weights': self.strategy_weights
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create instance from dictionary."""
        return cls(
            name=data.get('name', 'EvolvedStrategicAI'),
            board_size=data.get('board_size', 7),  # Default to 7 if not specified
            strategy_weights=data['strategy_weights']
        )
    
    def reset(self):
        """Reset for new game."""
        pass