import unittest
from src.game.rules import Rules

class TestRules(unittest.TestCase):

    def setUp(self):
        self.rules = Rules()

    def test_valid_move(self):
        # Test a valid move scenario
        self.assertTrue(self.rules.is_valid_move(start_position, end_position))

    def test_invalid_move(self):
        # Test an invalid move scenario
        self.assertFalse(self.rules.is_valid_move(start_position, invalid_end_position))

    def test_capture_move(self):
        # Test a capture move scenario
        self.assertTrue(self.rules.is_capture_move(start_position, capture_position))

    def test_game_over(self):
        # Test game over condition
        self.assertTrue(self.rules.is_game_over())

if __name__ == '__main__':
    unittest.main()