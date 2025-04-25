from abc import ABC, abstractmethod

class AIBase(ABC):
    @abstractmethod
    def choose_move(self, game_state):
        """Choose a move based on the current game state."""
        pass

    @abstractmethod
    def train(self, training_data):
        """Train the AI agent using the provided training data."""
        pass

    @abstractmethod
    def reset(self):
        """Reset the agent's internal state for a new game."""
        pass