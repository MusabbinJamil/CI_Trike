import unittest
from src.game import Game
from src.player import Player

class TestGame(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(color='white')
        self.player2 = Player(color='black')
        self.game = Game(player1=self.player1, player2=self.player2, board_size=7)

    def test_initial_setup(self):
        self.assertEqual(self.game.current_player, self.player1)
        self.assertIsNotNone(self.game.board)

    def test_player_turns(self):
        self.game.start_game()
        self.game.make_move(self.player1, (0, 0))
        self.assertEqual(self.game.current_player, self.player2)
        self.game.make_move(self.player2, (1, 1))
        self.assertEqual(self.game.current_player, self.player1)

    def test_pie_rule_swap(self):
        self.game.start_game()
        self.game.make_move(self.player1, (0, 0))
        self.assertTrue(self.player2.can_swap)
        self.player2.swap()
        self.assertEqual(self.player2.color, 'white')
        self.assertEqual(self.player1.color, 'black')

    def test_score_calculation(self):
        self.game.start_game()
        self.game.make_move(self.player1, (0, 0))
        self.game.make_move(self.player2, (1, 1))
        self.game.make_move(self.player1, (0, 1))
        self.game.make_move(self.player2, (1, 0))
        self.game.end_game()
        self.assertEqual(self.game.calculate_score(self.player1), 2)
        self.assertEqual(self.game.calculate_score(self.player2), 1)

    def test_game_over_condition(self):
        self.game.start_game()
        self.game.make_move(self.player1, (0, 0))
        self.game.make_move(self.player2, (1, 1))
        self.game.make_move(self.player1, (0, 1))
        self.game.make_move(self.player2, (1, 0))
        self.game.make_move(self.player1, (0, 2))
        self.game.make_move(self.player2, (1, 2))
        self.game.make_move(self.player1, (0, 3))
        self.game.make_move(self.player2, (1, 3))
        self.game.make_move(self.player1, (0, 4))
        self.game.make_move(self.player2, (1, 4))
        self.game.make_move(self.player1, (0, 5))
        self.game.make_move(self.player2, (1, 5))
        self.game.make_move(self.player1, (0, 6))
        self.game.make_move(self.player2, (1, 6))
        self.assertTrue(self.game.is_game_over())

if __name__ == '__main__':
    unittest.main()