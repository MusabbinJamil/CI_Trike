import tkinter as tk
import math

class BoardView(tk.Canvas):
    def __init__(self, master, game_state, click_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.game_state = game_state
        self.click_callback = click_callback
        
        # Visual settings - adjust cell size based on board size
        board_size = game_state.board_size
        # Smaller cell size for larger boards
        self.cell_size = min(40, 200 // (board_size * 2))  
        self.piece_size = int(self.cell_size * 0.8)
        self.selected_piece_color = "yellow"
        
        # Coordinates mapping
        self.axial_to_pixel = {}
        self.pixel_to_axial = {}
        
        # Bind click events
        self.bind("<Button-1>", self.on_click)
        
        # Initialize the view
        self.initialize()
        
    def initialize(self):
        """Set up the board canvas"""
        self.width = self.winfo_reqwidth()
        self.height = self.winfo_reqheight()
        
        # Calculate center point with more bottom padding to position the triangular grid
        # Move the center point down to make more room at the top
        self.center_x = self.width // 2
        self.center_y = (self.height // 2) + 50  # Add vertical offset to move board down
        
        # Create mapping between axial coordinates and pixel positions
        self.create_coordinate_mapping()
        
    def create_coordinate_mapping(self):
        """Create mapping between axial coordinates and pixel positions"""
        size = self.game_state.board_size
        self.axial_to_pixel = {}
        self.pixel_to_axial = {}
        
        # Conversion factors from axial to pixel coordinates
        # For equilateral triangles in a hexagonal grid
        sqrt3 = math.sqrt(3)
        
        # Clear previous mappings
        self.axial_to_pixel.clear()
        
        for q in range(-size, size+1):
            r_start = max(-size, -q-size)
            r_end = min(size, -q+size)
            for r in range(r_start, r_end+1):
                # Convert axial to pixel
                x = self.center_x + self.cell_size * 3/2 * q
                y = self.center_y + self.cell_size * sqrt3 * (r + q/2)
                
                self.axial_to_pixel[(q, r)] = (int(x), int(y))
        
    def pixel_to_axial_coords(self, x, y):
        """Convert pixel coordinates to the nearest axial coordinates"""
        # Find the closest cell center
        min_dist = float('inf')
        closest = None
        
        for axial, (px, py) in self.axial_to_pixel.items():
            dist = (x - px)**2 + (y - py)**2
            if dist < min_dist:
                min_dist = dist
                closest = axial
                
        return closest
        
    def render(self):
        """Render the current game state on the canvas"""
        print("\n--- Rendering board view ---")
        self.delete("all")  # Clear previous rendering
        
        # Refresh the coordinate mapping before redrawing
        self.create_coordinate_mapping()
        print(f"Created coordinate mapping for {len(self.axial_to_pixel)} cells")
        
        # Draw the triangular cells
        self.draw_board_cells()
        
        # Draw the pieces
        pieces_drawn = self.draw_pieces()
        print(f"Drew {pieces_drawn} pieces on the board")
        
        # Draw highlighting for selected piece
        if self.game_state.selected_piece_pos:
            self.highlight_selected_piece()
            print(f"Highlighted selected piece at {self.game_state.selected_piece_pos}")
        print("Board rendering complete")
            
    def draw_board_cells(self):
        """Draw all cells of the triangular board"""
        for axial, (x, y) in self.axial_to_pixel.items():
            # Draw hexagon for each cell
            self.draw_hexagon(x, y)
            
    def draw_hexagon(self, x, y):
        """Draw a hexagon at the given center point"""
        size = self.cell_size
        points = []
        
        for i in range(6):
            angle = math.pi / 3 * i
            px = x + size * math.cos(angle)
            py = y + size * math.sin(angle)
            points.extend([px, py])
            
        self.create_polygon(points, outline="black", fill="white", width=1, tags="cell")
        
    def draw_pieces(self):
        """Draw all game pieces on the board"""
        piece_count = 0
        for position, piece in self.game_state.board.pieces.items():
            if position in self.axial_to_pixel:
                x, y = self.axial_to_pixel[position]
                
                # Draw a circular piece
                self.create_oval(
                    x - self.piece_size//2, y - self.piece_size//2,
                    x + self.piece_size//2, y + self.piece_size//2,
                    fill=piece.color, outline="black", width=1,
                    tags=f"piece_{piece.player_id}"
                )
                piece_count += 1
        return piece_count
                
    def highlight_selected_piece(self):
        """Highlight the selected piece"""
        if self.game_state.selected_piece_pos in self.axial_to_pixel:
            x, y = self.axial_to_pixel[self.game_state.selected_piece_pos]
            
            # Draw selection indicator
            self.create_oval(
                x - self.piece_size//2 - 3, y - self.piece_size//2 - 3,
                x + self.piece_size//2 + 3, y + self.piece_size//2 + 3,
                outline=self.selected_piece_color, width=2,
                tags="selection"
            )
            
            # Highlight possible moves
            piece = self.game_state.board.get_piece_at(self.game_state.selected_piece_pos)
            if piece:
                possible_moves = piece.get_possible_moves(self.game_state.board)
                for move in possible_moves:
                    if move in self.axial_to_pixel:
                        mx, my = self.axial_to_pixel[move]
                        self.create_oval(
                            mx - 5, my - 5, mx + 5, my + 5,
                            fill="green", outline="black",
                            tags="possible_move"
                        )
                
    def on_click(self, event):
        """Handle click events on the board"""
        x, y = event.x, event.y
        axial = self.pixel_to_axial_coords(x, y)
        
        if self.click_callback and axial:
            self.click_callback(axial)
            
    def update(self):
        """Update the board view"""
        self.render()