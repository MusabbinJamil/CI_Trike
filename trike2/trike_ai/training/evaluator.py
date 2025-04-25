class Evaluator:
    def __init__(self, agents, environment):
        self.agents = agents
        self.environment = environment

    def evaluate(self, num_games=100):
        results = {agent.__class__.__name__: 0 for agent in self.agents}
        
        for _ in range(num_games):
            winner = self.play_game()
            if winner:
                results[winner.__class__.__name__] += 1
        
        return results

    def play_game(self):
        self.environment.reset()
        current_agent_index = 0
        
        while not self.environment.is_game_over():
            current_agent = self.agents[current_agent_index]
            move = current_agent.choose_move(self.environment)
            self.environment.apply_move(move)
            current_agent_index = (current_agent_index + 1) % len(self.agents)
        
        return self.environment.get_winner()

    def get_win_rates(self, results):
        total_games = sum(results.values())
        return {agent: wins / total_games for agent, wins in results.items()} if total_games > 0 else results