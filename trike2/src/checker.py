class Checker:
    def __init__(self, color):
        if color not in ("black", "white"):
            raise ValueError("Checker color must be 'black' or 'white'.")
        self.color = color

    def place(self, board, position):
        if board.is_valid_position(position):
            board.place_checker(self, position)
        else:
            raise ValueError("Invalid position for placing checker.")