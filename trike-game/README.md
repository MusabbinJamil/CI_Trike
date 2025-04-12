# Trike Game

## Overview
Trike is a GUI-based game inspired by the classic board game. The objective is to navigate your pieces strategically on the board while adhering to the game rules. This project aims to provide an engaging and interactive experience for players.

## Project Structure
The project is organized into several directories and files:

- **src/**: Contains the main source code for the game.
  - **main.py**: Entry point of the game.
  - **game/**: Contains the core game logic.
    - **board.py**: Manages the game board's state.
    - **pieces.py**: Defines the game pieces and their behaviors.
    - **rules.py**: Implements the game rules.
    - **state.py**: Manages the current state of the game.
  - **gui/**: Contains the graphical user interface components.
    - **board_view.py**: Renders the game board.
    - **game_window.py**: Sets up the main game window.
    - **menu.py**: Handles the game menu.
  - **assets/**: Contains resources such as fonts, images, and sounds.
  - **utils/**: Contains utility functions to assist with various tasks.

- **tests/**: Contains unit tests for the game logic.
  - **test_board.py**: Tests for the Board class.
  - **test_rules.py**: Tests for the Rules class.

- **requirements.txt**: Lists the dependencies required for the project.

## Setup Instructions
1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required dependencies using:
   ```
   pip install -r requirements.txt
   ```
4. Run the game by executing:
   ```
   python src/main.py
   ```

## Gameplay Rules
- Players take turns to move their pieces on the board.
- The objective is to strategically position your pieces to win the game.
- Follow the rules defined in the `rules.py` file for valid moves.

## Contribution Guidelines
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Submit a pull request detailing your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.