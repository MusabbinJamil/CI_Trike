import tkinter as tk
from tkinter import messagebox
from game.state import GameState
from gui.board_view import BoardView

class GameWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Trike Game")
        self.root.geometry("800x600")
        
        self.game_state = GameState()
        self.game_state.setup_game()
        
        self.create_widgets()
        self.update_status()
        
    def create_widgets(self):
        # Main frameR
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top info frame
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Player info and status
        self.player_label = tk.Label(self.info_frame, text="Current Player: ")
        self.player_label.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(self.info_frame, text="")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        # Game board frame
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Create board view
        self.board_view = BoardView(
            self.board_frame, 
            self.game_state, 
            click_callback=self.on_board_click,
            width=800, 
            height=500,
            bg="light gray"
        )
        self.board_view.pack(fill=tk.BOTH, expand=True)
        
        # Bottom control frame
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Buttons
        self.new_game_button = tk.Button(
            self.control_frame, 
            text="New Game", 
            command=self.start_new_game
        )
        self.new_game_button.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.quit_button = tk.Button(
            self.control_frame, 
            text="Quit", 
            command=self.root.quit
        )
        self.quit_button.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Initialize board view
        self.board_view.render()
        
    def update_status(self):
        """Update the game status display"""
        player = self.game_state.current_player()
        if player:
            self.player_label.config(
                text=f"Current Player: {player.name}", 
                fg=player.color
            )
        
        if self.game_state.game_over:
            winner_text = "Game Over! "
            if self.game_state.winner:
                winning_players = [
                    self.game_state.players[winner_id].name 
                    for winner_id in self.game_state.winner
                ]
                winner_text += f"Winner(s): {', '.join(winning_players)}"
            else:
                winner_text += "It's a draw!"
            self.status_label.config(text=winner_text)
        else:
            self.status_label.config(text="")
            
    def on_board_click(self, axial_coords):
        """Handle clicks on the board"""
        print(f"\nClick at position: {axial_coords}")
        
        if self.game_state.game_over:
            print("Game is over - ignoring click")
            return
            
        if self.game_state.selected_piece_pos:
            print(f"Selected piece at: {self.game_state.selected_piece_pos}")
            # If we already have a piece selected, try to move it
            if self.game_state.make_move(self.game_state.selected_piece_pos, axial_coords):
                # Move successful
                print(f"Moved piece from {self.game_state.selected_piece_pos} to {axial_coords}")
                self.game_state.selected_piece_pos = None
                self.update_status()
                self.board_view.render()
                
                if self.game_state.game_over:
                    print("Game over detected after move")
                    self.show_game_over_message()
            elif self.game_state.board.get_piece_at(axial_coords) and \
                self.game_state.board.get_piece_at(axial_coords).player_id == \
                self.game_state.current_player().id:
                # If clicked on another own piece, select it instead
                print(f"Selecting different piece at {axial_coords}")
                self.game_state.select_piece(axial_coords)
                self.board_view.render()
            else:
                # Invalid move, deselect
                print("Invalid move - deselecting piece")
                self.game_state.selected_piece_pos = None
                self.board_view.render()
        else:
            # Try to select a piece
            print(f"Attempting to select piece at {axial_coords}")
            if self.game_state.select_piece(axial_coords):
                print("Piece selected successfully")
                self.board_view.render()
            else:
                print("No valid piece to select at this position")
                
    def show_game_over_message(self):
        """Show game over message"""
        winner_text = "Game Over! "
        if self.game_state.winner:
            winning_players = [
                self.game_state.players[winner_id].name 
                for winner_id in self.game_state.winner
            ]
            winner_text += f"Winner(s): {', '.join(winning_players)}"
        else:
            winner_text += "It's a draw!"
            
        messagebox.showinfo("Game Over", winner_text)
                
    def start_new_game(self):
        """Start a new game"""
        print("\n=== STARTING NEW GAME ===")
        self.game_state.reset()
        print(f"Game state reset - Current player: {self.game_state.current_player().name}")
        print(f"Number of pieces on board: {len(self.game_state.board.pieces)}")
        self.update_status()
        self.board_view.render()
        print("Board view rendered")
        
    def run(self):
        """Run the game window"""
        self.root.mainloop()