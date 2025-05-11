import tkinter as tk
import tkinter.messagebox
import math
from src.game import Game
import tkinter.simpledialog
import json
import os
# Add these imports for AI support
from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI, HybridAI, DQNAI
import threading
import time

HEX_SIZE = 30

FONT_LARGE = ("Arial", 16)
FONT_BUTTON = ("Arial", 14)

class TrikeGUI:
    def __init__(self, game=None):
        self.game = game
    
        # Initialize root window
        self.root = tk.Tk()
        self.root.title("Trike")
        self.root.minsize(800, 600)

        # Theme definitions
        self.themes = {
            "Classic": {
                "bg": "white",
                "board": "gray",
                "valid_move": "purple",
                "pawn": "red",
                "pawn_outline": "black",
                "player1": "black",
                "player2": "white",
                "panel_bg": "lightyellow"
            },
            "Green & Purple": {
                "bg": "#e8f5e9",
                "board": "#81c784",
                "valid_move": "#7b1fa2",
                "pawn": "#f57f17",
                "pawn_outline": "#000000",
                "player1": "#388e3c",
                "player2": "#9c27b0",
                "panel_bg": "#c8e6c9"
            },
            "Black & White": {
                "bg": "#f5f5f5",
                "board": "#9e9e9e",
                "valid_move": "#616161",
                "pawn": "#ff5722",
                "pawn_outline": "#000000",
                "player1": "#212121",
                "player2": "#f5f5f5",
                "panel_bg": "#e0e0e0"
            },
            "Red & Blue": {
                "bg": "#e3f2fd",
                "board": "#90caf9",
                "valid_move": "#880e4f",
                "pawn": "#ffd600",
                "pawn_outline": "#000000",
                "player1": "#d32f2f",
                "player2": "#1565c0",
                "panel_bg": "#bbdefb"
            }
        }
        
        # Default theme
        self.current_theme = "Classic"

        # Player name and score tracking
        self.player_names = ["Player 1", "Player 2"]
        self.scores_file = "trike_scores.json"

        # Initialize AI players (will be set in start_game)
        self.ai_players = [None, None]
        
        # Initialize StringVar for player types (will be created in show_setup_panel)
        self.player1_type = tk.StringVar(value="Human")
        self.player2_type = tk.StringVar(value="Human")

        # Add winner_name attribute
        self.winner_name = None

        # Add auto_play and close_when_done attributes
        self.auto_play = False
        self.close_when_done = False
        
        # Create main container frame
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- Create all panels (initially hidden) ---
        # 1. Setup panel
        self.setup_panel = tk.Frame(self.main_container, bg="lightyellow")
        
        instructions = (
            "Trike Game Instructions:\n"
            "- Players take turns placing checkers and moving the pawn.\n"
            "- The pawn must move in a straight line to an empty hex.\n"
            "- The game ends when the pawn is trapped.\n"
            "- The winner is the player with the most checkers around the pawn.\n"
            "- Pie rule: After the first move, Player 2 can swap colors.\n"
        )
        
        tk.Label(
            self.setup_panel, 
            text=instructions, 
            justify=tk.LEFT, 
            font=FONT_LARGE,
            bg="lightyellow", 
            wraplength=500
        ).pack(padx=20, pady=20)
        
        size_frame = tk.Frame(self.setup_panel, bg="lightyellow")
        size_frame.pack(pady=20)
        
        tk.Label(
            size_frame, 
            text="Enter board size (7-19):", 
            font=FONT_LARGE,
            bg="lightyellow"
        ).pack(side=tk.LEFT)
        
        self.size_var = tk.StringVar()
        self.size_entry = tk.Entry(size_frame, textvariable=self.size_var, font=FONT_LARGE, width=5)
        self.size_entry.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            self.setup_panel, 
            text="Start Game", 
            command=self.start_game, 
            font=FONT_BUTTON, 
            width=15
        ).pack(pady=20)
        
        # 2. Game panel (board and game info)
        self.game_panel = tk.Frame(self.main_container)
        
        # Status label (always visible in game panel)
        self.status = tk.Label(self.game_panel, text="Trike Game", font=FONT_LARGE)
        self.status.pack(pady=10)
        
        # Game panel with scrollable canvas
        self.frame = tk.Frame(self.game_panel)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.h_scroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(
            self.frame, width=600, height=500,
            bg="white",
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)
        
        # 3. Game result panel
        self.result_panel = tk.Frame(self.main_container, bg="lightyellow")
        self.result_label = tk.Label(
            self.result_panel, 
            text="", 
            font=FONT_LARGE,
            bg="lightyellow",
            justify=tk.CENTER,
            wraplength=500
        )
        self.result_label.pack(padx=20, pady=20)
        
        # Button to return to setup from results
        tk.Button(
            self.result_panel,
            text="Play Again", 
            command=self.show_setup_panel, 
            font=FONT_BUTTON, 
            width=15
        ).pack(pady=(0, 20))
        
        # Button frame (always at bottom)
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        # Configure grid for equal expansion
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)
        self.button_frame.columnconfigure(3, weight=1)
        self.button_frame.columnconfigure(4, weight=1)  # Add column for scoreboard button
        
        btn_width = 12  # Set a fixed width for all buttons
        
        self.new_game_btn = tk.Button(
            self.button_frame, 
            text="New Game", 
            command=self.show_setup_panel, 
            width=btn_width, 
            font=FONT_BUTTON
        )
        self.new_game_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.reset_btn = tk.Button(
            self.button_frame, 
            text="Reset", 
            command=self.reset_game, 
            width=btn_width, 
            font=FONT_BUTTON
        )
        self.reset_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.instructions_btn = tk.Button(
            self.button_frame, 
            text="Instructions", 
            command=self.show_instructions, 
            width=btn_width, 
            font=FONT_BUTTON
        )
        self.instructions_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.scoreboard_btn = tk.Button(
            self.button_frame, 
            text="Scoreboard", 
            command=self.show_scoreboard, 
            width=btn_width, 
            font=FONT_BUTTON
        )
        self.scoreboard_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        self.quit_btn = tk.Button(
            self.button_frame, 
            text="Quit", 
            command=self.root.quit, 
            width=btn_width, 
            font=FONT_BUTTON
        )
        self.quit_btn.grid(row=0, column=4, padx=10, pady=10, sticky="ew")
        
        # Initialize variables
        self.selected = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.game_over = False
        self.valid_moves = set()
        
        # Show initial setup panel
        self.show_setup_panel()

    def hex_to_pixel(self, q, r):
        x = HEX_SIZE * (3/2 * q) + 50
        y = HEX_SIZE * (math.sqrt(3) * (r + q/2)) + 50
        return x, y

    def draw_hex(self, q, r, color="gray"):
        x, y = self.hex_to_pixel(q, r)
        points = []
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + HEX_SIZE * math.cos(angle)
            py = y + HEX_SIZE * math.sin(angle)
            points.extend([px, py])
        self.canvas.create_polygon(points, outline="black", fill=color, width=2)
        
        # Add pattern for valid moves (not just color)
        if color == "purple":
            # Add diagonal lines pattern for valid moves
            self.canvas.create_line(x-15, y-15, x+15, y+15, width=2)
            self.canvas.create_line(x-15, y+15, x+15, y-15, width=2)
        
        # Get checker if present
        checker = self.game.board.grid.get((q, r))
        
        # Draw pawn with stronger visual distinction
        if self.game.pawn.position == (q, r):
            # Use high contrast and pattern for the pawn
            self.canvas.create_oval(x-14, y-14, x+14, y+14, fill="red", outline="black", width=3)
            
            # Draw the center showing the checker color
            if checker:
                center_color = "black" if checker.color == "black" else "white"
                center_outline = "white" if checker.color == "black" else "black"
                self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=center_color, outline=center_outline, width=1)
            else:
                # Use yellow if no checker is present
                self.canvas.create_oval(x-6, y-6, x+6, y+6, fill="yellow", outline="black", width=1)
            
            # Add star shape markers to make pawn unmistakable
            for i in range(4):
                angle = math.pi/2 * i + math.pi/4
                px = x + 18 * math.cos(angle)
                py = y + 18 * math.sin(angle)
                self.canvas.create_text(px, py, text="*", font=("Arial", 14, "bold"))
        # Draw checker if no pawn is present
        elif checker:
            fill = "black" if checker.color == "black" else "white"
            outline = "white" if checker.color == "black" else "black"
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=fill, outline=outline, width=2)
    
    def draw_board(self):
        print("Redrawing board...")
        self.canvas.delete("all")
        self.update_valid_moves()
        for (q, r) in self.game.board.grid:
            color = "purple" if (q, r) in self.valid_moves else "gray"
            self.draw_hex(q, r, color=color)
        if not (self.game_over):
            player1 = f"{self.get_player_display_name(0)} ({self.game.players[0].color.capitalize()})"
            player2 = f"{self.get_player_display_name(1)} ({self.game.players[1].color.capitalize()})"
            current_idx = self.game.current_player_index
            current = f"{self.get_player_display_name(current_idx)} ({self.game.players[current_idx].color.capitalize()})"
            self.status.config(
                text=f"{player1} vs {player2}    |    {current}'s turn"
            )

    def on_click(self, event):
        if self.game_over:
            print("Game is over. No more moves allowed.")
            return
        # Convert screen (event) coordinates to canvas coordinates
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        print(f"Click at pixel: ({canvas_x}, {canvas_y})")
        for (q, r) in self.game.board.grid:
            x, y = self.hex_to_pixel(q, r)
            if (canvas_x - x)**2 + (canvas_y - y)**2 < HEX_SIZE**2:
                print(f"Hex clicked: ({q}, {r})")
                self.handle_move(q, r)
                break

    def handle_move(self, q, r):
        if self.game_over:
            print("Game is over. No more moves allowed.")
            return
        
        print(f"Attempting move to: ({q}, {r})")
        if self.game.pawn.position is None:
            if self.game.board.grid[(q, r)] is None:
                print(f"First move by {self.game.players[self.game.current_player_index].color}")
                self.game.board.place_checker(q, r, self.game.players[self.game.current_player_index])
                self.game.pawn.position = (q, r)
                self.game.board.pawn_position = (q, r)
                self.game.first_move_done = True
                self.draw_board()
                if self.game.pie_rule_available:
                    print("Offering pie rule to second player.")
                    
                    # If player 2 is human, offer pie rule
                    if self.ai_players[1] is None:
                        swap_msg = (
                            f"Do you want to swap colors with Player 1 "
                            f"({self.game.players[0].color.capitalize()})?"
                        )
                        if tkinter.messagebox.askyesno("Pie Rule", swap_msg):
                            print("Pie rule used: players swapped.")
                            self.game.players.reverse()
                            self.game.current_player_index = 1
                        else:
                            print("Pie rule declined.")
                            # Advance to Player 2 if pie rule declined
                            self.game.current_player_index = 1
                    else:
                        # AI player 2 decides on pie rule (50% chance)
                        import random
                        if random.random() > 0.5:
                            print("AI used pie rule: players swapped.")
                            self.game.players.reverse()
                            self.game.current_player_index = 1
                            self.status.config(text=f"{self.player_names[1]} (AI) used the pie rule!")
                            self.root.update()
                            time.sleep(1)  # Show the message briefly
                        else:
                            print("AI declined pie rule.")
                            self.game.current_player_index = 1
                    
                    self.game.pie_rule_available = False
                    self.check_ai_turn()
                    return
        
        if self.game.board.is_pawn_trapped():
            print("Pawn is trapped. Game over.")
            self.show_score()
            self.game_over = True
            
        else:
            q_from, r_from = self.game.pawn.position
            print(f"Current pawn position: ({q_from}, {r_from})")
            # Use backend's is_valid_move
            if self.game.board.is_valid_move(q_from, r_from, q, r):
                print(f"Valid move by {self.game.players[self.game.current_player_index].color} to ({q}, {r})")
                self.game.board.place_checker(q, r, self.game.players[self.game.current_player_index])
                self.game.pawn.position = (q, r)
                self.game.board.pawn_position = (q, r)
                if self.game.board.is_pawn_trapped():
                    print("Pawn is trapped. Game over.")
                    self.show_score()
                else:
                    self.game.current_player_index = (self.game.current_player_index + 1) % 2
                    print(f"Next turn: {self.game.players[self.game.current_player_index].color}")
                    self.draw_board()
                    # Check if it's an AI's turn now
                    self.check_ai_turn()
                self.draw_board()
            else:
                print(f"Invalid move attempted to ({q}, {r})")
    
    def update_valid_moves(self):
        self.valid_moves.clear()
        if self.game.pawn.position is None:
            return
        q_from, r_from = self.game.pawn.position
        for (q, r) in self.game.board.grid:
            if self.game.board.is_valid_move(q_from, r_from, q, r):
                self.valid_moves.add((q, r))
    
    def update_player_name_from_ai(self, player_type, player_index):
        """Update player name field based on selected AI type"""
        if player_type != "Human":
            if player_index == 0:
                self.player1_name.set(player_type)
            else:
                self.player2_name.set(player_type)
    
    def show_setup_panel(self):
        # Hide other panels
        self.game_panel.pack_forget()
        self.result_panel.pack_forget()
        
        # Show setup panel
        self.setup_panel.pack(fill=tk.BOTH, expand=True)
        
        # Clear any existing name fields (to avoid duplicates on reset)
        for widget in self.setup_panel.winfo_children():
            if hasattr(widget, 'player_name_frame') or hasattr(widget, 'theme_frame') or hasattr(widget, 'ai_frame'):
                widget.destroy()
        
        # Add player name input fields
        player_name_frame = tk.Frame(self.setup_panel, bg=self.themes[self.current_theme]["panel_bg"])
        player_name_frame.player_name_frame = True  # Mark for identification
        player_name_frame.pack(pady=10)
        
        # Player 1 name field
        tk.Label(
            player_name_frame,
            text="Player 1 Name:",
            font=FONT_LARGE,
            bg=self.themes[self.current_theme]["panel_bg"]
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        
        self.player1_name = tk.StringVar(value="Player 1")
        tk.Entry(
            player_name_frame,
            textvariable=self.player1_name,
            font=FONT_LARGE,
            width=15
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Player 2 name field
        tk.Label(
            player_name_frame,
            text="Player 2 Name:",
            font=FONT_LARGE,
            bg=self.themes[self.current_theme]["panel_bg"]
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.player2_name = tk.StringVar(value="Player 2")
        tk.Entry(
            player_name_frame, 
            textvariable=self.player2_name,
            font=FONT_LARGE,
            width=15
        ).grid(row=1, column=1, padx=5, pady=5)
        
        # Add AI selection options
        ai_frame = tk.Frame(self.setup_panel, bg=self.themes[self.current_theme]["panel_bg"])
        ai_frame.ai_frame = True  # Mark for identification
        ai_frame.pack(pady=10)
        
        # Player 1 AI selection with callback
        tk.Label(
            ai_frame,
            text="Player 1 Type:",
            font=FONT_LARGE,
            bg=self.themes[self.current_theme]["panel_bg"]
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        
        self.player1_type = tk.StringVar(value="Human")
        player1_options = tk.OptionMenu(
            ai_frame,
            self.player1_type,
            "Human", "RandomAI", "MinimaxAI-Easy", "MinimaxAI-Hard", "MCTSAI", "HybridAI", "DQNAI",
            command=lambda selection: self.update_player_name_from_ai(selection, 0)
        )
        player1_options.config(font=FONT_LARGE, width=15)
        player1_options.grid(row=0, column=1, padx=5, pady=5)
        
        # Player 2 AI selection with callback
        tk.Label(
            ai_frame,
            text="Player 2 Type:",
            font=FONT_LARGE,
            bg=self.themes[self.current_theme]["panel_bg"]
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        
        self.player2_type = tk.StringVar(value="Human")
        player2_options = tk.OptionMenu(
            ai_frame,
            self.player2_type,
            "Human", "RandomAI", "MinimaxAI-Easy", "MinimaxAI-Hard", "MCTSAI", "HybridAI", "DQNAI",
            command=lambda selection: self.update_player_name_from_ai(selection, 1)
        )
        player2_options.config(font=FONT_LARGE, width=15)
        player2_options.grid(row=1, column=1, padx=5, pady=5)
    
    def show_game_panel(self):
        # Hide other panels
        self.setup_panel.pack_forget()
        self.result_panel.pack_forget()
        
        # Show game panel
        self.game_panel.pack(fill=tk.BOTH, expand=True)
        self.root.unbind("<Return>")
        
        # If auto_play is enabled, start the loop
        if self.auto_play:
            self.root.after(100, self.check_auto_play)
    
    def show_result_panel(self, result_text):
        # Hide other panels
        self.setup_panel.pack_forget()
        self.game_panel.pack_forget()

        # Set the winner name for the evolutionary optimizer to access
        if "wins" in result_text:
            self.winner_name = result_text.split(" wins")[0]
        else:
            self.winner_name = "Draw"
    
        
        # Update and show result panel
        self.result_label.config(text=result_text)
        self.result_panel.pack(fill=tk.BOTH, expand=True)
    
    def show_result_popup(self, result_text):
        """Display game results as a popup dialog instead of replacing the game panel"""
        # Create result window
        result_window = tk.Toplevel(self.root)
        result_window.title("Game Over")
        result_window.geometry("400x350")
        result_window.configure(bg="lightyellow")
        
        # Make window modal (must interact with it before returning to main window)
        result_window.grab_set()
        result_window.transient(self.root)
        
        # Center the window on screen
        result_window.update_idletasks()
        width = result_window.winfo_width()
        height = result_window.winfo_height()
        x = (result_window.winfo_screenwidth() // 2) - (width // 2)
        y = (result_window.winfo_screenheight() // 2) - (height // 2)
        result_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Result text
        tk.Label(
            result_window,
            text=result_text,
            font=FONT_LARGE,
            bg="lightyellow",
            justify=tk.CENTER,
            wraplength=350
        ).pack(padx=20, pady=20, expand=True)
        
        # Button frame to contain both buttons
        button_frame = tk.Frame(result_window, bg="lightyellow")
        button_frame.pack(pady=10)
        
        # Play Again button
        tk.Button(
            button_frame,
            text="Play Again",
            command=lambda: [result_window.destroy(), self.show_setup_panel()],
            font=FONT_BUTTON,
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Close button (just close popup, keep game board visible)
        tk.Button(
            button_frame,
            text="Close",
            command=result_window.destroy,
            font=FONT_BUTTON,
            width=15
        ).pack(side=tk.LEFT, padx=10, pady=10)

    def create_ai(self, ai_type, player_name):
        """Create an AI player based on the selected type"""
        try:
            if ai_type == "RandomAI":
                return RandomAI(name=player_name)
            elif ai_type == "MinimaxAI-Easy":
                return MinimaxAI(depth=2, name=player_name)
            elif ai_type == "MinimaxAI-Hard":
                return MinimaxAI(depth=3, name=player_name)
            elif ai_type == "MCTSAI":
                return MCTSAI(iterations=1000, name=player_name)
            elif ai_type == "HybridAI": 
                return HybridAI(name=player_name)
            elif ai_type == "DQNAI":
                dqn = DQNAI(name=player_name)
                dqn.load_model("models/DQN_Agent.pt")  # Load trained model
                dqn.epsilon = 0.05  # Set low epsilon for mostly exploitation
                return dqn
            else:
                return None
        except Exception as e:
            print(f"Error creating AI: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def start_game(self):
        try:
            size = int(self.size_var.get())
            if 7 <= size <= 19:
                from src.game import Game
                self.game = Game(size)
                self.game_over = False
                
                # Save player names
                self.player_names = [self.player1_name.get(), self.player2_name.get()]
                # If names are empty, use defaults
                if not self.player_names[0].strip():
                    self.player_names[0] = "Player 1"
                if not self.player_names[1].strip():
                    self.player_names[1] = "Player 2"
                
                # Create AI players if selected
                self.ai_players = [None, None]
                
                # Player 1 AI
                p1_type = self.player1_type.get()
                if p1_type == "RandomAI":
                    self.ai_players[0] = RandomAI(name=self.player_names[0])
                elif p1_type == "MinimaxAI-Easy":
                    self.ai_players[0] = MinimaxAI(depth=2, name=self.player_names[0])
                elif p1_type == "MinimaxAI-Hard":
                    self.ai_players[0] = MinimaxAI(depth=3, name=self.player_names[0])
                elif p1_type == "MCTSAI":
                    self.ai_players[0] = MCTSAI(iterations=1000, name=self.player_names[0])
                elif p1_type == "HybridAI":
                    self.ai_players[0] = HybridAI(name=self.player_names[0])
                elif p1_type == "DQNAI":
                    self.ai_players[0] = DQNAI(name=self.player_names[0])
                    self.ai_players[0].load_model("models/DQN_Agent.pt")

                # Player 2 AI
                p2_type = self.player2_type.get()
                if p2_type == "RandomAI":
                    self.ai_players[1] = RandomAI(name=self.player_names[1])
                elif p2_type == "MinimaxAI-Easy":
                    self.ai_players[1] = MinimaxAI(depth=2, name=self.player_names[1])
                elif p2_type == "MinimaxAI-Hard": 
                    self.ai_players[1] = MinimaxAI(depth=3, name=self.player_names[1])
                elif p2_type == "MCTSAI":
                    self.ai_players[1] = MCTSAI(iterations=1000, name=self.player_names[1])
                elif p2_type == "HybridAI":
                    self.ai_players[1] = HybridAI(name=self.player_names[1])
                elif p2_type == "DQNAI":
                    self.ai_players[1] = DQNAI(name=self.player_names[1])
                    self.ai_players[1].load_model("models/DQN_Agent.pt")

                # Update canvas dimensions
                width = int(HEX_SIZE * 1.5 * size + HEX_SIZE * 2)
                height = int(HEX_SIZE * math.sqrt(3) * size + HEX_SIZE * 2)
                self.canvas.config(
                    width=min(width, 800),
                    height=min(height, 500),
                    scrollregion=(0, 0, width, height)
                )
                
                self.status.config(text="Trike Game")
                self.draw_board()
                self.show_game_panel()
                
                # Start AI's turn if current player is AI
                self.check_ai_turn()
            else:
                tk.messagebox.showerror("Invalid Size", "Please enter a number between 7 and 19.")
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter a valid integer.")

    def load_scores(self):
        """Load scores from local JSON file"""
        if not os.path.exists(self.scores_file):
            return {}
        
        try:
            with open(self.scores_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_score(self, winner_name):
        """Save the winner's score to the local JSON file"""
        if winner_name == "Draw":
            return
            
        scores = self.load_scores()
        scores[winner_name] = scores.get(winner_name, 0) + 1
        
        with open(self.scores_file, 'w') as file:
            json.dump(scores, file, indent=4)
    
    def show_score(self):
        print("Calculating final score...")
        pawn_pos = self.game.pawn.position
        neighbors = self.game.board.get_neighbors(*pawn_pos)
        under = self.game.board.grid[pawn_pos]
        adj = [self.game.board.grid.get(n) for n in neighbors]
        black_score = sum(1 for c in adj + [under] if c and c.color == "black")
        white_score = sum(1 for c in adj + [under] if c and c.color == "white")
        print(f"Black score: {black_score}, White score: {white_score}")
        
        # Figure out which player is which color
        black_player = self.player_names[0] if self.game.players[0].color == "black" else self.player_names[1]
        white_player = self.player_names[0] if self.game.players[0].color == "white" else self.player_names[1]
        
        if black_score > white_score:
            winner = "Black"
            winner_name = black_player
            winner_msg = f"{black_player} (Black)"
        elif white_score > black_score:
            winner = "White"
            winner_name = white_player
            winner_msg = f"{white_player} (White)"
        else:
            winner = "Draw"
            winner_name = "Draw"
            winner_msg = "It's a draw!"

        print(f"Winner: {winner}")
        self.status.config(text=f"Game Over! {black_player} (Black): {black_score}, {white_player} (White): {white_score}. Winner: {winner_msg}")
        self.draw_board()
        self.root.update_idletasks()

        # Save the winner's score
        if winner != "Draw":
            self.save_score(winner_name)

        # Create result message with more emphasis on the winner
        if winner == "Draw":
            msg = (
                f"Game Over!\n\n"
                f"{black_player} (Black): {black_score}\n"
                f"{white_player} (White): {white_score}\n\n"
                f"The game is a draw!\n\n"
                f"Thank you for playing Trike!"
            )
        else:
            msg = (
                f"Game Over!\n\n"
                f"{black_player} (Black): {black_score}\n"
                f"{white_player} (White): {white_score}\n\n"
                f"WINNER: {winner_name}\n"
                f"Congratulations, {winner_msg}!\n\n"
                f"Thank you for playing Trike!"
            )
        
        # Show result as a popup instead of replacing the game panel
        self.show_result_popup(msg)
        self.game_over = True

        # Close the window if close_when_done is enabled
        if self.close_when_done:
            self.root.quit()
    
    def show_scoreboard(self):
        """Display the scoreboard in a new window"""
        scores = self.load_scores()
        
        # Create scoreboard window
        scoreboard = tk.Toplevel(self.root)
        scoreboard.title("Trike Scoreboard")
        scoreboard.geometry("400x500")
        
        # Heading
        tk.Label(
            scoreboard,
            text="Trike Scoreboard",
            font=("Arial", 20, "bold")
        ).pack(pady=20)
        
        # Create frame for scores
        score_frame = tk.Frame(scoreboard)
        score_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Headers
        tk.Label(
            score_frame,
            text="Player",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        tk.Label(
            score_frame,
            text="Wins",
            font=("Arial", 16, "bold")
        ).grid(row=0, column=1, padx=20, pady=10)
        
        # No scores message
        if not scores:
            tk.Label(
                score_frame,
                text="No games played yet!",
                font=("Arial", 14)
            ).grid(row=1, column=0, columnspan=2, pady=20)
        else:
            # Sort scores by number of wins (descending)
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            
            # Display each player's score
            for i, (player, wins) in enumerate(sorted_scores):
                tk.Label(
                    score_frame,
                    text=player,
                    font=("Arial", 14)
                ).grid(row=i+1, column=0, padx=20, pady=5, sticky="w")
                
                tk.Label(
                    score_frame,
                    text=str(wins),
                    font=("Arial", 14)
                ).grid(row=i+1, column=1, padx=20, pady=5)
        
        # Close button
        tk.Button(
            scoreboard,
            text="Close",
            command=scoreboard.destroy,
            font=FONT_BUTTON
        ).pack(pady=20)
    
    def show_instructions(self):
        # Instead of creating a new window, temporarily show instructions in main view
        current_state = None
        if self.setup_panel.winfo_ismapped():
            current_state = "setup"
        elif self.game_panel.winfo_ismapped():
            current_state = "game"
        elif self.result_panel.winfo_ismapped():
            current_state = "result"
        
        instructions = (
            "Trike Game Instructions:\n\n"
            "- Players take turns placing checkers and moving the pawn.\n"
            "- The pawn must move in a straight line to an empty hex.\n"
            "- The game ends when the pawn is trapped.\n"
            "- The winner is the player with the most checkers around the pawn.\n"
            "- Pie rule: After the first move, Player 2 can swap colors.\n"
        )
        
        # Show instructions in result panel temporarily
        self.show_result_panel(instructions)
        
        # Change the button to return to previous state
        for widget in self.result_panel.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(text="Back")
                if current_state == "setup":
                    widget.config(command=self.show_setup_panel)
                elif current_state == "game":
                    widget.config(command=lambda: self.show_game_panel())
                elif current_state == "result":
                    widget.config(command=lambda: self.show_result_panel(self.result_label.cget("text")))
                break
    
    def reset_game(self):
        if self.game:
            self.game.reset()
            self.game_over = False
            self.status.config(text="Trike Game")
            self.draw_board()
            self.show_game_panel()
    
    def new_game(self):
        self.show_setup_panel()
        
    def run(self):
        self.root.mainloop()
    
    def update_theme(self, selected_theme=None):
        """Update the UI with the selected theme colors"""
        if selected_theme:
            self.current_theme = selected_theme
        
        # Update setup panel background
        self.setup_panel.config(bg=self.themes[self.current_theme]["panel_bg"])
        
        # Update all child widgets in setup panel
        for widget in self.setup_panel.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=self.themes[self.current_theme]["panel_bg"])
                for child in widget.winfo_children():
                    if isinstance(child, (tk.Label, tk.Frame)):
                        child.config(bg=self.themes[self.current_theme]["panel_bg"])
        
        # Update result panel background
        self.result_panel.config(bg=self.themes[self.current_theme]["panel_bg"])
        for widget in self.result_panel.winfo_children():
            if isinstance(widget, tk.Label):
                widget.config(bg=self.themes[self.current_theme]["panel_bg"])
        
        # Update canvas
        self.canvas.config(bg=self.themes[self.current_theme]["bg"])
        
        # Redraw board if game is in progress
        if self.game:
            self.draw_board()
    
    def check_ai_turn(self):
        """Check if current player is AI and make a move if so"""
        if self.game_over:
            return
            
        current_idx = self.game.current_player_index
        if self.ai_players[current_idx] is not None:
            # Show thinking message
            self.status.config(text=f"{self.player_names[current_idx]} (AI) is thinking...")
            self.root.update()
            
            # Use a thread to prevent GUI freezing
            threading.Thread(target=self.make_ai_move).start()

    def make_ai_move(self):
        """Have the AI make a move"""
        current_idx = self.game.current_player_index
        ai = self.ai_players[current_idx]
        
        # Short delay to show AI is "thinking"
        time.sleep(0.5)
        
        # Create a game state copy for the AI
        game_copy = self.game
        
        try:
            if self.game.pawn.position is None:
                # First move of the game - just pick a random valid position
                import random
                valid_positions = [pos for pos, checker in self.game.board.grid.items() if checker is None]
                q, r = random.choice(valid_positions)
            else:
                # Use choose_move if it exists (this is the standard method name in many AI implementations)
                if hasattr(ai, "choose_move"):
                    q, r = ai.choose_move(game_copy)
                # Try select_move as a second option
                elif hasattr(ai, "select_move"):
                    q, r = ai.select_move(game_copy)
                # Use get_best_move as a fallback
                elif hasattr(ai, "get_best_move"):
                    q, r = ai.get_best_move(game_copy)
                # Last resort - pick a random valid move
                else:
                    valid_moves = []
                    q_from, r_from = self.game.pawn.position
                    for (q_to, r_to) in self.game.board.grid:
                        if self.game.board.is_valid_move(q_from, r_from, q_to, r_to):
                            valid_moves.append((q_to, r_to))
                    
                    if valid_moves:
                        q, r = random.choice(valid_moves)
                    else:
                        self.status.config(text="AI couldn't find a valid move")
                        return
            
            # Execute the AI's move through the regular move handler
            self.root.after(0, lambda: self.handle_move(q, r))
        
        except Exception as e:
            print(f"AI move error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.status.config(text=f"AI error: {str(e)}")

    def get_player_display_name(self, player_idx):
        """Get a display name for the player that indicates if they are AI"""
        base_name = self.player_names[player_idx]
        if self.ai_players[player_idx] is not None:
            ai_type = self.player1_type.get() if player_idx == 0 else self.player2_type.get()
            return f"{base_name} ({ai_type})"
        return base_name

    def check_auto_play(self):
        if self.auto_play and self.game and not self.game.is_game_over():
            self.check_ai_turn()
            # Schedule next check after a short delay
            self.root.after(100, self.check_auto_play)
        elif self.auto_play and self.game and self.game.is_game_over() and self.close_when_done:
            # Save the scores before closing
            winner = self.game.get_winner()
            if winner is not None:
                self.winner_name = self.get_player_display_name(winner)
                self.save_score(self.winner_name)
            # Close the window after a short delay
            self.root.after(1000, self.root.destroy)

if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Trike Game with AI options.")
    parser.add_argument("--board_size", type=int, default=7, help="Size of the game board (7-19).")
    parser.add_argument("--player1_name", type=str, default="Player 1", help="Name of Player 1.")
    parser.add_argument("--player1_ai", type=str, choices=["Human", "RandomAI", "MinimaxAI", "MCTSAI", "HybridAI"], default="Human", help="AI type for Player 1.")
    parser.add_argument("--player1_minimax_weight", type=int, default=25, help="Weight for MinimaxAI for Player 1 (HybridAI only).")
    parser.add_argument("--player1_mcts_weight", type=int, default=45, help="Weight for MCTSAI for Player 1 (HybridAI only).")
    parser.add_argument("--player1_random_weight", type=int, default=30, help="Weight for RandomAI for Player 1 (HybridAI only).")
    parser.add_argument("--player2_name", type=str, default="Player 2", help="Name of Player 2.")
    parser.add_argument("--player2_ai", type=str, choices=["Human", "RandomAI", "MinimaxAI", "MCTSAI", "HybridAI"], default="Human", help="AI type for Player 2.")
    parser.add_argument("--player2_minimax_weight", type=int, default=25, help="Weight for MinimaxAI for Player 2 (HybridAI only).")
    parser.add_argument("--player2_mcts_weight", type=int, default=45, help="Weight for MCTSAI for Player 2 (HybridAI only).")
    parser.add_argument("--player2_random_weight", type=int, default=30, help="Weight for RandomAI for Player 2 (HybridAI only).")
    parser.add_argument("--auto_play", type=str, choices=["True", "False"], default="False", 
                        help="Automatically play the game without user interaction")
    parser.add_argument("--close_when_done", type=str, choices=["True", "False"], default="False",
                        help="Automatically close the window when game is finished")
    args = parser.parse_args()

    # Initialize the game
    game = Game(args.board_size)
    gui = TrikeGUI(game)

    # Set player names
    gui.player_names = [args.player1_name, args.player2_name]

    # Create AI players based on arguments
    if args.player1_ai != "Human":
        if args.player1_ai == "HybridAI":
            gui.ai_players[0] = HybridAI(
                name=args.player1_name,
                minimax_weight=args.player1_minimax_weight,
                mcts_weight=args.player1_mcts_weight,
                random_weight=args.player1_random_weight,
            )
        elif args.player1_ai == "MinimaxAI":
            gui.ai_players[0] = MinimaxAI(depth=3, name=args.player1_name)
        elif args.player1_ai == "MCTSAI":
            gui.ai_players[0] = MCTSAI(iterations=1000, name=args.player1_name)
        elif args.player1_ai == "RandomAI":
            gui.ai_players[0] = RandomAI(name=args.player1_name)

    if args.player2_ai != "Human":
        if args.player2_ai == "HybridAI":
            gui.ai_players[1] = HybridAI(
                name=args.player2_name,
                minimax_weight=args.player2_minimax_weight,
                mcts_weight=args.player2_mcts_weight,
                random_weight=args.player2_random_weight,
            )
        elif args.player2_ai == "MinimaxAI":
            gui.ai_players[1] = MinimaxAI(depth=3, name=args.player2_name)
        elif args.player2_ai == "MCTSAI":
            gui.ai_players[1] = MCTSAI(iterations=1000, name=args.player2_name)
        elif args.player2_ai == "RandomAI":
            gui.ai_players[1] = RandomAI(name=args.player2_name)

    # Set auto_play and close_when_done attributes
    gui.auto_play = args.auto_play == "True"
    gui.close_when_done = args.close_when_done == "True"

    # Run the game
    gui.run()

    # Return the winner's name
    print(f"The winner is: {gui.winner_name}")