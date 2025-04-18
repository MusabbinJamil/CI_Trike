import tkinter as tk
import tkinter.messagebox
import math
from .game import Game
import tkinter.simpledialog

HEX_SIZE = 30  # pixels

class TrikeGUI:
    def __init__(self, game):
        self.game = game
        board_size = self.game.board.size

        width = int(HEX_SIZE * 1.5 * board_size + HEX_SIZE * 2)
        height = int(HEX_SIZE * math.sqrt(3) * board_size + HEX_SIZE * 2)

        self.root = tk.Tk()
        self.root.title("Trike")

        # --- Add scrollable canvas ---
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.h_scroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(
            self.frame, width=min(width, 1200), height=min(height, 900),
            bg="white",
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set,
            scrollregion=(0, 0, width, height)
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.h_scroll.config(command=self.canvas.xview)
        self.v_scroll.config(command=self.canvas.yview)
        # ----------------------------

        self.selected = None
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = tk.Label(self.root, text="Trike Game")
        self.status.pack()
        self.game_over = False

        # --- Button frame below canvas ---
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Configure grid for equal expansion
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        btn_width = 12  # Set a fixed width for all buttons

        self.new_game_btn = tk.Button(self.button_frame, text="New Game", command=self.new_game, width=btn_width)
        self.new_game_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.reset_btn = tk.Button(self.button_frame, text="Reset", command=self.reset_game, width=btn_width)
        self.reset_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.quit_btn = tk.Button(self.button_frame, text="Quit", command=self.root.quit, width=btn_width)
        self.quit_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.valid_moves = set()
        self.draw_board()

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
        # Draw checker if present
        checker = self.game.board.grid.get((q, r))
        if checker:
            fill = "black" if checker.color == "black" else "white"
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=fill, outline="black")
        # Draw pawn if present
        if self.game.pawn.position == (q, r):
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red", outline="red")

    def draw_board(self):
        print("Redrawing board...")
        self.canvas.delete("all")
        self.update_valid_moves()
        for (q, r) in self.game.board.grid:
            color = "purple" if (q, r) in self.valid_moves else "gray"
            self.draw_hex(q, r, color=color)
        if not (self.game_over):
            player1 = f"Player 1 ({self.game.players[0].color.capitalize()})"
            player2 = f"Player 2 ({self.game.players[1].color.capitalize()})"
            current = f"Player {self.game.current_player_index + 1} ({self.game.players[self.game.current_player_index].color.capitalize()})"
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
                    if tkinter.messagebox.askyesno("Pie Rule", "Do you want to swap colors?"):
                        print("Pie rule used: players swapped.")
                        self.game.players.reverse()
                        self.game.current_player_index = 1
                    else:
                        print("Pie rule declined.")
                    self.game.pie_rule_available = False
        
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
            else:
                print(f"Invalid move attempted to ({q}, {r})")

    
    def show_score(self):
        print("Calculating final score...")
        pawn_pos = self.game.pawn.position
        neighbors = self.game.board.get_neighbors(*pawn_pos)
        under = self.game.board.grid[pawn_pos]
        adj = [self.game.board.grid.get(n) for n in neighbors]
        black_score = sum(1 for c in adj + [under] if c and c.color == "black")
        white_score = sum(1 for c in adj + [under] if c and c.color == "white")
        print(f"Black score: {black_score}, White score: {white_score}")
        if black_score > white_score:
            winner = "Black"
        elif white_score > black_score:
            winner = "White"
        else:
            winner = "Draw"
        print(f"Winner: {winner}")
        self.status.config(text=f"Game Over! Black: {black_score}, White: {white_score}. Winner: {winner}")

        self.draw_board()
        self.root.update_idletasks()

        # Show info dialog only, don't hide buttons
        msg = f"Game over!\nBlack: {black_score}, White: {white_score}\nWinner: {winner}"
        tkinter.messagebox.showinfo("Game Over", msg)
        self.game_over = True

    def reset_game(self):
        # Reset the game state to initial
        self.game.reset()
        self.game_over = False
        self.status.config(text="Trike Game")
        self.draw_board()
    
    def new_game(self):
        # Re-run the start dialog and replace the game
        class StartDialog(tk.Toplevel):
            def __init__(self, parent):
                super().__init__(parent)
                self.title("Welcome to Trike")
                self.result = None
                instructions = (
                    "Trike Game Instructions:\n"
                    "- Players take turns placing checkers and moving the pawn.\n"
                    "- The pawn must move in a straight line to an empty hex.\n"
                    "- The game ends when the pawn is trapped.\n"
                    "- The winner is the player with the most checkers around the pawn.\n"
                    "- Pie rule: After the first move, Player 2 can swap colors.\n"
                )
                tk.Label(self, text=instructions, justify=tk.LEFT, anchor="nw", font=("Arial", 11), bg="lightyellow", width=60, wraplength=500).pack(padx=20, pady=10)
                tk.Label(self, text="Enter board size (7-19):", font=("Arial", 11)).pack(pady=(10,0))
                self.size_var = tk.StringVar()
                entry = tk.Entry(self, textvariable=self.size_var, font=("Arial", 11))
                entry.pack(pady=5)
                entry.focus()
                tk.Button(self, text="Start Game", command=self.on_start, font=("Arial", 11)).pack(pady=10)
                self.bind("<Return>", lambda e: self.on_start())
                self.grab_set()
                self.protocol("WM_DELETE_WINDOW", self.on_close)

            def on_start(self):
                try:
                    size = int(self.size_var.get())
                    if 7 <= size <= 19:
                        self.result = size
                        self.destroy()
                    else:
                        tk.messagebox.showerror("Invalid Size", "Please enter a number between 7 and 19.")
                except ValueError:
                    tk.messagebox.showerror("Invalid Input", "Please enter a valid integer.")

            def on_close(self):
                self.result = None
                self.destroy()

        dialog = StartDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.result:
            from .game import Game
            self.game = Game(dialog.result)
            self.game_over = False
            self.status.config(text="Trike Game")
            board_size = self.game.board.size
            width = int(HEX_SIZE * 1.5 * board_size + HEX_SIZE * 2)
            height = int(HEX_SIZE * math.sqrt(3) * board_size + HEX_SIZE * 2)
            # --- Update canvas and scrollregion ---
            self.canvas.config(width=min(width, 1200), height=min(height, 900))
            self.canvas.config(scrollregion=(0, 0, width, height))
            # --------------------------------------
            self.draw_board()

    def show_thanks_message(self):
        # No longer needed, but keep for compatibility
        self.status.config(text="Thanks for playing!")
        
    def is_valid_move(self, q_from, r_from, q_to, r_to):
        # Must move in a straight line (same direction)
        dq = q_to - q_from
        dr = r_to - r_from

        # No move or not in a straight line
        if dq == 0 and dr == 0:
            return False

        # Normalize direction
        directions = [
            (1, 0), (1, -1), (0, -1),
            (-1, 0), (-1, 1), (0, 1)
        ]
        for dir_q, dir_r in directions:
            steps = None
            if dir_q != 0:
                if dq % dir_q == 0 and dr == dir_r * (dq // dir_q):
                    steps = dq // dir_q
            elif dir_r != 0:
                if dr % dir_r == 0 and dq == dir_q * (dr // dir_r):
                    steps = dr // dir_r
            if steps is not None and steps > 0:
                # Check all intermediate spaces are empty
                for i in range(1, steps + 1):
                    pos = (q_from + dir_q * i, r_from + dir_r * i)
                    if pos not in self.grid or self.grid[pos] is not None:
                        return False
                return True
        return False
    
    def update_valid_moves(self):
        self.valid_moves.clear()
        if self.game.pawn.position is None:
            return
        q_from, r_from = self.game.pawn.position
        for (q, r) in self.game.board.grid:
            if self.game.board.is_valid_move(q_from, r_from, q, r):
                self.valid_moves.add((q, r))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":

    class StartDialog(tk.Toplevel):
        def __init__(self, parent):
            super().__init__(parent)
            self.title("Welcome to Trike")
            self.result = None
            instructions = (
                "Trike Game Instructions:\n"
                "- Players take turns placing checkers and moving the pawn.\n"
                "- The pawn must move in a straight line to an empty hex.\n"
                "- The game ends when the pawn is trapped.\n"
                "- The winner is the player with the most checkers around the pawn.\n"
                "- Pie rule: After the first move, Player 2 can swap colors.\n"
            )
            tk.Label(self, text=instructions, justify=tk.LEFT, anchor="nw", font=("Arial", 11), bg="lightyellow", width=60, wraplength=500).pack(padx=20, pady=10)
            tk.Label(self, text="Enter board size (7-19):", font=("Arial", 11)).pack(pady=(10,0))
            self.size_var = tk.StringVar()
            entry = tk.Entry(self, textvariable=self.size_var, font=("Arial", 11))
            entry.pack(pady=5)
            entry.focus()
            tk.Button(self, text="Start Game", command=self.on_start, font=("Arial", 11)).pack(pady=10)
            self.bind("<Return>", lambda e: self.on_start())
            self.grab_set()
            self.protocol("WM_DELETE_WINDOW", self.on_close)

        def on_start(self):
            try:
                size = int(self.size_var.get())
                if 7 <= size <= 19:
                    self.result = size
                    self.destroy()
                else:
                    tk.messagebox.showerror("Invalid Size", "Please enter a number between 7 and 19.")
            except ValueError:
                tk.messagebox.showerror("Invalid Input", "Please enter a valid integer.")

        def on_close(self):
            self.result = None
            self.destroy()

    root = tk.Tk()
    root.withdraw()  # Hide main window for now
    dialog = StartDialog(root)
    root.wait_window(dialog)
    if dialog.result:
        root.destroy()
        game = Game(dialog.result)
        gui = TrikeGUI(game)
        gui.run()
    else:
        root.destroy()