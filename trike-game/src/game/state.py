from game.board import Board
from game.rules import Rules
from game.pieces import Stone

class Player:
    def __init__(self, id, name, color):
        self.id = id
        self.name = name
        self.color = color
        
class GameState:
    def __init__(self, board_size=5):
        self.board = None  # Will be initialized in setup_game
        self.rules = None  # Will be initialized in setup_game
        self.current_player_index = 0
        self.players = []
        self.game_over = False
        self.winner = None
        self.selected_piece_pos = None
        self.board_size = board_size
        
    def add_player(self, name, color):
        player_id = len(self.players)
        player = Player(player_id, name, color)
        self.players.append(player)

    def setup_game(self):
        # Create board and rules
        self.board = Board(self.board_size)
        self.rules = Rules(self.board)
        
        # Reset game state
        self.current_player_index = 0
        self.game_over = False
        self.winner = None
        
        if len(self.players) < 2:
            # Add default players if none provided
            if not self.players:
                self.add_player("Player 1", "blue")
            self.add_player("Player 2", "red")
            
        # Place initial pieces
        self.place_initial_pieces()
            
    def place_initial_pieces(self):
        """Place initial pieces on the board for all players"""
        # Clear the board first
        self.board.reset_board()
        print("Board cleared for new game")
        
        # For 2 players on a triangular board
        if len(self.players) == 2:
            # Player 1 pieces at the top
            player = self.players[0]
            size = self.board_size
            pieces_placed = 0
            
            # Place in the first row
            for q in range(-size+1, 1):
                pos = (q, -size)
                piece = Stone(player.color, player.id)
                if self.board.place_piece(piece, pos):
                    pieces_placed += 1
                    
            print(f"Placed {pieces_placed} pieces for Player 1 ({player.color})")
            
            # Player 2 pieces at the bottom
            player = self.players[1]
            pieces_placed = 0
            
            # Place in the bottom row
            for q in range(0, size):
                pos = (q, size-q)
                piece = Stone(player.color, player.id)
                if self.board.place_piece(piece, pos):
                    pieces_placed += 1
                    
            print(f"Placed {pieces_placed} pieces for Player 2 ({player.color})")
                
    def current_player(self):
        """Get the current player"""
        if 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None
        
    def next_turn(self):
        """Advance to the next player's turn"""
        if not self.game_over:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def make_move(self, from_position, to_position):
        """Attempt to make a move"""
        if self.game_over:
            return False
            
        current_player = self.current_player()
        if not current_player:
            return False
            
        # Validate and execute the move
        if self.rules.validate_move(current_player.id, from_position, to_position):
            success = self.rules.execute_move(from_position, to_position)
            if success:
                # Check if game is over after this move
                if self.rules.is_game_over(self):
                    self.game_over = True
                    self.winner = self.rules.get_winner(self)
                else:
                    self.next_turn()
                return True
        return False
        
    def select_piece(self, position):
        """Select a piece for movement"""
        piece = self.board.get_piece_at(position)
        if piece and piece.player_id == self.current_player().id:
            self.selected_piece_pos = position
            return True
        return False
        
    def reset(self):
        """Reset the game state"""
        print("\n--- Resetting game state ---")
        print("Creating new board and placing initial pieces...")
        self.setup_game()
        print(f"Game reset complete - {len(self.board.pieces)} pieces placed")
