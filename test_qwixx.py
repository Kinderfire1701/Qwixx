import sys
import time
from collections import defaultdict

from qwixx import QwixxGame
from agents import HumanPlayer, GreedyPlayer, HeuristicGreedyPlayer, HeuristicSpacePlayer, QLearnPlayer

if __name__ == "__main__":
    print("""I'm attempting to determine an optimal strategy for the Game Qwixx. I investigate how two heuristics and Q-learning approach compare against a greedy agent.
My results (vs greedy):
Wins: {'GreedyPlayer': 31443, 'HeuristicSpacePlayer': 68557} -- 100000 games
Wins: {'GreedyPlayer': 15116, 'HeuristicGreedyPlayer': 84884} -- 100000 games
Wins: {'GreedyPlayer': 97, 'QLearnPlayer': 3} -- 100 games

Heuristics against eachother:
Wins: {'HeuristicSpacePlayer': 33331, 'HeuristicGreedyPlayer': 66669} -- 10000 games

Round Robin:
{'HeuristicSpacePlayer': 90, 'HeuristicGreedyPlayer': 850, 'GreedyPlayer': 60} -- 1000 games
          
As you can see, these results indicate that the heuristic greedy strategy performs the best out of the approaches, whereas the Heuristic space minimizing strategy still performs better than the greedy agent. The Q-learning agent does not seem to be effectively learning anything, and in fact performs very poorly! Complicating this approach was the learning time which prevented running a very large number of games. I attempted various hyperparameters and partitioning schemes but did not see many improvements. I suspect Q-learning, even with the linear approximator, suffers from a very large action space. Even limiting the state space significantly, the action space is still very large given the number of actions is determined by a dice roll.
""")
    games = 1000
    run_time = 0
    if len(sys.argv) > 1:
        if sys.argv[1] == "--time":
            run_time = int(sys.argv[2])
            games = 5
        else:
            games = int(sys.argv[1])
    
    # Initialize the game
    # options are "greedy", "human", "heuristic_greedy", "heuristic_space", "q_learn"
    game = QwixxGame("heuristic_space", "heuristic_greedy", "greedy") #Make changes here! 
    
    # Define the agents
    agents = [HeuristicSpacePlayer(), HeuristicGreedyPlayer(), GreedyPlayer()] #make changes here! Options are the imports
    
    # Track wins for each agent and total games played
    wins = {agent.__class__.__name__: 0 for agent in agents}
    total_games = 0
    
    start_time = time.time()
    
    while total_games < games or time.time() - start_time < run_time:
        # Simulate games
        if total_games % 1000 == 0:
            print(f"Played {total_games} games. Wins so far: {wins}")
        batch_results = game.play()  # This will return scores for each player
        total_games += 1
        
        # Determine the winner based on scores
        winner_index = batch_results.index(max(batch_results))
        wins[agents[winner_index].__class__.__name__] += 1

    print("Wins:", wins)
    print("Total Games Played:", total_games)