import random
from trike_ai.agents.ai_base import AIBase
from trike_ai.agents.minimax_ai import MinimaxAI
from trike_ai.agents.mcts_ai import MCTSAI
from trike_ai.agents.random_ai import RandomAI

class HybridAI:
    """
    AI agent that randomly selects between MinimaxAI, MCTSAI, or RandomAI
    with customizable weights. Current default weights are:
    - MinimaxAI: 50%
    - MCTSAI: 40%
    - RandomAI: 10%
    These weights were learned thorugh evolutionary training.
    """ 
    def __init__(self, name="Hybrid AI", minimax_weight=20, mcts_weight=31, random_weight=49):
        """
        Initialize the Hybrid AI agent with customizable weights.
        
        Args:
            name (str): Name of the AI agent
            minimax_weight (int): Weight for selecting MinimaxAI
            mcts_weight (int): Weight for selecting MCTSAI
            random_weight (int): Weight for selecting RandomAI
        """
        self.name = name
        self.selected_agent = None
        self.weights = [minimax_weight, mcts_weight, random_weight]

    def choose_move(self, game_state):
        """
        Choose a move by delegating to a randomly selected AI strategy
        with weighted probabilities.
        
        Args:
            game_state: Current state of the game
            
        Returns:
            tuple: (q, r) coordinates of the chosen move
        """
        # Randomly select an AI strategy with weighted probabilities
        if self.selected_agent is None:
            total_weight = sum(self.weights)
            cumulative_weights = [sum(self.weights[:i+1]) for i in range(len(self.weights))]
            rand = random.uniform(0, total_weight)
            
            if rand <= cumulative_weights[0]:
                strategy = "MinimaxAI"
            elif rand <= cumulative_weights[1]:
                strategy = "MCTSAI"
            else:
                strategy = "RandomAI"
            
            if strategy == "MinimaxAI":
                self.selected_agent = MinimaxAI(depth=3, name="MinimaxAI")
            elif strategy == "MCTSAI":
                self.selected_agent = MCTSAI(iterations=500, name="MCTSAI")
            elif strategy == "RandomAI":
                self.selected_agent = RandomAI(name="RandomAI")
        
        # Delegate the move selection to the chosen AI
        return self.selected_agent.choose_move(game_state)

    def reset(self):
        """
        Reset the selected agent (if needed).
        """
        self.selected_agent = None