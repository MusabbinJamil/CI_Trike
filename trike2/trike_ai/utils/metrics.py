def calculate_average_score(scores):
    if not scores:
        return 0
    return sum(scores) / len(scores)

def calculate_win_rate(wins, total_games):
    if total_games == 0:
        return 0
    return wins / total_games

def calculate_decision_time(decision_times):
    if not decision_times:
        return 0
    return sum(decision_times) / len(decision_times)

def calculate_performance_metrics(agent_results):
    metrics = {}
    for agent_name, results in agent_results.items():
        metrics[agent_name] = {
            'average_score': calculate_average_score(results['scores']),
            'win_rate': calculate_win_rate(results['wins'], results['total_games']),
            'average_decision_time': calculate_decision_time(results['decision_times']),
        }
    return metrics