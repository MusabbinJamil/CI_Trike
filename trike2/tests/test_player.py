import unittest
from src.player import Player
from src.checker import Checker

class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player1 = Player(color='white')
        self.player2 = Player(color='black')

    def test_initialization(self):
        self.assertEqual(self.player1.color, 'white')
        self.assertEqual(self.player2.color, 'black')

    def test_make_move(self):
        # Assuming the Player class has a method make_move
        # and the game board is set up correctly
        move_result = self.player1.make_move((0, 0), (1, 1))  # Example move
        self.assertTrue(move_result)

    def test_swap_sides(self):
        # Assuming the Player class has a method to swap sides
        original_color = self.player1.color
        self.player1.swap_sides()
        self.assertNotEqual(self.player1.color, original_color)

    def test_pie_rule(self):
        # Assuming the Player class has a method to implement the pie rule
        self.player1.place_checker((0, 0))  # Example placement
        self.assertTrue(self.player2.can_swap_sides())

    def test_score_calculation(self):
        # Assuming the Player class has a method to calculate score
        self.player1.place_checker((0, 1))
        self.player1.place_checker((1, 1))
        score = self.player1.calculate_score()
        self.assertEqual(score, 2)  # Example score calculation

if __name__ == '__main__':
    unittest.main()