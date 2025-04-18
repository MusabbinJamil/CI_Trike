import unittest
from src.board import Board
from src.checker import Checker

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board(size=7)  # Initialize a board of size 7 for testing

    def test_place_checker(self):
        checker = Checker(color='white')
        self.board.place_checker(1, 1, checker)
        self.assertEqual(self.board.grid[1][1], checker)

    def test_invalid_place_checker(self):
        checker = Checker(color='black')
        self.board.place_checker(1, 1, checker)
        with self.assertRaises(ValueError):
            self.board.place_checker(1, 1, checker)  # Should raise an error for placing on occupied space

    def test_check_trap(self):
        # Set up a scenario where the pawn is trapped
        self.board.place_checker(0, 0, Checker(color='white'))
        self.board.place_checker(0, 1, Checker(color='white'))
        self.board.place_checker(1, 0, Checker(color='white'))
        self.board.pawn_position = (0, 0)  # Assume pawn is at (0, 0)
        self.assertTrue(self.board.is_trapped())

    def test_valid_move(self):
        checker = Checker(color='black')
        self.board.place_checker(1, 1, checker)
        self.board.pawn_position = (1, 1)
        self.assertTrue(self.board.is_valid_move(1, 1, 1, 2))  # Moving to an empty space

    def test_invalid_move_occupied(self):
        checker1 = Checker(color='black')
        checker2 = Checker(color='white')
        self.board.place_checker(1, 1, checker1)
        self.board.place_checker(1, 2, checker2)
        self.board.pawn_position = (1, 1)
        self.assertFalse(self.board.is_valid_move(1, 1, 1, 2))  # Cannot move to occupied space

if __name__ == '__main__':
    unittest.main()