class GameEnvironment:
    def __init__(self, game):
        self.game = game
        self.reset()

    def reset(self):
        self.game_over = False
        self.game.reset()
        return self.game.get_state()

    def apply_move(self, move):
        if self.game_over:
            raise Exception("Game is over. Cannot apply move.")
        valid = self.game.apply_move(move)
        if self.game.is_over():
            self.game_over = True
        return valid

    def get_valid_moves(self):
        return self.game.get_valid_moves()

    def is_game_over(self):
        return self.game_over

    def get_winner(self):
        if not self.game_over:
            raise Exception("Game is not over yet.")
        return self.game.get_winner()