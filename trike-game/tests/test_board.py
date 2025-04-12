import unittest
from src.game.board import Board

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board()

    def test_initial_state(self):
        self.assertEqual(self.board.get_state(), "expected_initial_state")

    def test_piece_placement(self):
        self.board.place_piece("piece_type", (0, 0))
        self.assertEqual(self.board.get_piece_at((0, 0)), "piece_type")

    def test_invalid_move(self):
        result = self.board.move_piece((0, 0), (1, 1))
        self.assertFalse(result)

    def test_valid_move(self):
        self.board.place_piece("piece_type", (0, 0))
        result = self.board.move_piece((0, 0), (0, 1))
        self.assertTrue(result)
        self.assertEqual(self.board.get_piece_at((0, 1)), "piece_type")

if __name__ == '__main__':
    unittest.main()