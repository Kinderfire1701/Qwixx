import sys
import time
from collections import defaultdict

from qwixx import QwixxGame
from agents import HumanPlayer, GreedyPlayer, HeuristicGreedyPlayer

if __name__ == "__main__":
    games = 1000
    run_time = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "--time":
            run_time = int(sys.argv[2])
            games = 100
        else:
            games = int(sys.argv[1])
    
    # Initialize the game
    game = QwixxGame("greedy", "heuristic_greedy")  # Replace with your Qwixx game initialization
    
    # Define the agents
    agents = [GreedyPlayer(), HeuristicGreedyPlayer()]  # Example agents
    
    # Track wins for each agent and total games played
    wins = {agent.__class__.__name__: 0 for agent in agents}
    total_games = 0
    
    start_time = time.time()
    
    while total_games < games or time.time() - start_time < run_time:
        # Simulate games
        if total_games % 100 == 0:
            print(f"Played {total_games} games. Wins so far: {wins}")
        batch_results = game.play()  # This will return scores for each player
        total_games += 1
        
        # Determine the winner based on scores
        winner_index = batch_results.index(max(batch_results))
        wins[agents[winner_index].__class__.__name__] += 1

    print("Wins:", wins)
    print("Total Games Played:", total_games)