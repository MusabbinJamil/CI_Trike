from trike_ai.agents import RandomAI, MinimaxAI, MCTSAI, DQNAI
from runner import run_ai_match  # Use your working runner.py
import traceback

def test_single_match():
    """Test a single match to diagnose issues"""
    print("Testing single match...")
    
    # Create simple agents
    agent1 = RandomAI(name="TestRandom1")
    agent2 = RandomAI(name="TestRandom2")
    
    print(f"Agent 1: {agent1}")
    print(f"Agent 2: {agent2}")
    print(f"Agent 1 name: {agent1.name}")
    print(f"Agent 2 name: {agent2.name}")
    
    try:
        print("\nAttempting match...")
        result = run_ai_match(agent1, agent2, board_size=7, verbose=True)
        print(f"\nResult: {result}")
        print(f"Result type: {type(result)}")
        
        if isinstance(result, tuple) and len(result) == 2:
            winner, scores = result
            print(f"Winner: {winner}")
            print(f"Scores: {scores}")
        else:
            print(f"Unexpected result format: {result}")
            
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_single_match()