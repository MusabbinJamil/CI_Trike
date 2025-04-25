# Trike AI Project

## Overview
The Trike AI project is designed to facilitate the development and training of artificial intelligence agents to play the Trike game. This project includes various AI implementations, a training environment, and tools for evaluating and visualizing agent performance.

## Project Structure
```
trike_ai/
├── __init__.py
├── agents/
│   ├── __init__.py
│   ├── ai_base.py
│   ├── random_ai.py
│   ├── minimax_ai.py
│   └── mcts_ai.py
├── training/
│   ├── __init__.py
│   ├── environment.py
│   ├── evaluator.py
│   └── tournament.py
├── utils/
│   ├── __init__.py
│   ├── visualization.py
│   └── metrics.py
└── README.md
```

## Installation
To set up the project, clone the repository and install the required dependencies. You can use the following commands:

```bash
git clone <repository-url>
cd trike_ai
pip install -r requirements.txt
```

## Usage
To use the AI agents, you can import the desired agent class from the `agents` module. For example:

```python
from agents.random_ai import RandomAI
from agents.minimax_ai import MinimaxAI
```

You can then create instances of these classes and use their methods to choose moves or train them.

## Modules

### Agents
- **ai_base.py**: Contains the abstract class `AIBase` that defines the interface for all AI agents.
- **random_ai.py**: Implements a random move selection strategy.
- **minimax_ai.py**: Implements the Minimax algorithm for decision-making.
- **mcts_ai.py**: Implements the Monte Carlo Tree Search algorithm.

### Training
- **environment.py**: Manages the game state and provides methods for interacting with the game.
- **evaluator.py**: Evaluates the performance of AI agents based on various metrics.
- **tournament.py**: Organizes tournaments between different AI agents.

### Utils
- **visualization.py**: Provides functions for visualizing game states and agent performance.
- **metrics.py**: Contains functions for calculating performance metrics for AI agents.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.