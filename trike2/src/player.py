class Player:
    def __init__(self, color):
        self.color = color

    def choose_initial_position(self, board):
        while True:
            try:
                pos = input(f"{self.color.capitalize()} player, enter initial position as 'q r': ")
                q, r = map(int, pos.strip().split())
                if board.is_valid_position(q, r) and board.grid[(q, r)] is None:
                    return (q, r)
                else:
                    print("Invalid position. Try again.")
            except Exception:
                print("Invalid input. Try again.")

    def make_move(self, board, pawn):
        q_from, r_from = pawn.position
        while True:
            try:
                pos = input(f"{self.color.capitalize()} player, enter move destination as 'q r': ")
                q_to, r_to = map(int, pos.strip().split())
                if board.is_valid_move(q_from, r_from, q_to, r_to):
                    return (q_to, r_to)
                else:
                    print("Invalid move. Try again.")
            except Exception:
                print("Invalid input. Try again.")

    def offer_pie_rule(self):
        ans = input("Second player: Do you want to swap colors? (y/n): ").strip().lower()
        return ans == "y"