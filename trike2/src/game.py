from .board import Board
from .player import Player
from .pawn import Pawn
from .checker import Checker
from .utils import calculate_score

class Game:
    def __init__(self, board_size):
        self.board = Board(board_size)
        self.players = [Player("white"), Player("black")]
        self.current_player_index = 0
        self.pawn = Pawn()
        self.game_over = False
        self.pie_rule_used = False
        self.pie_rule_available = True
        self.first_move_done = False

    def start_game(self):
        self.setup_pawn()
        # Pie rule: offer swap to second player after first move
        self.offer_pie_rule()
        while not self.game_over:
            self.play_turn()

    def setup_pawn(self):
        # First player chooses initial position
        first_player = self.players[self.current_player_index]
        q, r = first_player.choose_initial_position(self.board)
        checker = Checker(first_player.color)
        self.board.place_checker(q, r, checker)
        self.pawn.position = (q, r)
        self.board.pawn_position = (q, r)

    def offer_pie_rule(self):
        # Second player may choose to swap colors
        second_player = self.players[1]
        swap = second_player.offer_pie_rule()
        if swap:
            self.players.reverse()
            self.current_player_index = 1
            self.pie_rule_used = True

    def play_turn(self):
        current_player = self.players[self.current_player_index]
        q_from, r_from = self.pawn.position
        move = current_player.make_move(self.board, self.pawn)
        q_to, r_to = move
        checker = Checker(current_player.color)
        if self.board.is_valid_move(q_from, r_from, q_to, r_to):
            self.board.place_checker(q_to, r_to, checker)
            self.pawn.position = (q_to, r_to)
            self.board.pawn_position = (q_to, r_to)
        else:
            print("Invalid move. Try again.")
            return

        if self.board.is_pawn_trapped():
            self.end_game()
        else:
            self.current_player_index = (self.current_player_index + 1) % 2

    def end_game(self):
        self.game_over = True
        self.calculate_scores()

    def calculate_scores(self):
        scores = {player.color: calculate_score(self.board, player.color, self.pawn.position) for player in self.players}
        winner = max(scores, key=scores.get)
        print(f"The winner is {winner} with a score of {scores[winner]}")
    
    def reset(self):
        # Reset the board and all game state to initial
        self.board.reset()  # You need to implement reset in your Board class
        self.pawn = Pawn()
        self.current_player_index = 0
        self.game_over = False
        self.pie_rule_used = False
        self.pie_rule_available = True
        self.first_move_done = False

if __name__ == "__main__":
    size = int(input("Enter board size (7-19): "))
    game = Game(size)
    game.start_game()