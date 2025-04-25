from matplotlib import pyplot as plt

def plot_win_rates(win_rates, agent_names):
    plt.figure(figsize=(10, 5))
    for agent_name, rates in win_rates.items():
        plt.plot(rates, label=agent_name)
    
    plt.title('Win Rates of AI Agents')
    plt.xlabel('Games Played')
    plt.ylabel('Win Rate')
    plt.ylim(0, 1)
    plt.legend()
    plt.grid()
    plt.show()

def visualize_game_state(game_state):
    # This function would visualize the current game state.
    # Implementation depends on the specifics of the game state representation.
    pass

def plot_performance_metrics(metrics):
    plt.figure(figsize=(10, 5))
    plt.bar(metrics.keys(), metrics.values())
    
    plt.title('Performance Metrics of AI Agents')
    plt.xlabel('Metrics')
    plt.ylabel('Values')
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.show()