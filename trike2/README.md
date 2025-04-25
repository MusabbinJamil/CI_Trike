# Trike Game

Trike is a combinatorial abstract strategy game designed for two players. The game revolves around setting traps, dismantling opponent traps, and maneuvering a shared piece into your own trap to win. 

## Game Overview

- **Players**: 2
- **Objective**: Maneuver the neutral pawn into your own trap while preventing your opponent from doing the same.
- **Game Board**: The game is played on an equilateral triangular hexagon-tessellated grid.
- **Components**: 
  - A neutral pawn
  - Black and white checkers

## Rules

1. Players take turns moving the neutral pawn around the board. Passing is not allowed.
2. The neutral pawn can move any number of empty points in any direction in a straight line, but cannot move onto or jump over occupied points.
3. When a player moves the pawn, they first place a checker of their own color onto the destination point, then move the pawn on top of it.
4. The game ends when the pawn is trapped.
5. At the end of the game, each player scores points for each checker of their own color adjacent to or underneath the pawn. The player with the highest score wins.
6. The pie rule allows the second player a one-time chance to swap sides after the first player places their checker and moves the pawn.

## Installation

To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Running the Game

Go to dist folder and open gui.exe

to create distribution run, execute:

```
pyinstaller --onefile gui.py
```
or this
```
pyinstaller --onefile --clean --paths=src src/gui.py
```

To start a game of Trike using the command-line interface, execute:

```
python -m src.game
```

To launch the graphical user interface (GUI), run:

```
python src/gui.py
```

## Running Tests

To run the unit tests for the project, use:

```
pytest
```

## Project Structure

```
trike
├── src
│   ├── board.py
│   ├── game.py
│   ├── player.py
│   ├── pawn.py
│   ├── checker.py
│   ├── utils.py
|   ├── gui.py
|   └── __main__.py
├── tests
│   ├── test_board.py
│   ├── test_game.py
│   └── test_player.py
├── requirements.txt
├── setup.py
└── README.md
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.