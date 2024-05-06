from abc import ABC, abstractmethod
import random

class Agent(ABC):
    @abstractmethod
    def choose_move(self, possible_moves):
        pass

class HumanPlayer(Agent):
    def choose_move(self, possible_moves):
        while True:
            print("Possible moves:")
            for index, move in enumerate(possible_moves):
                if move == 'Penalty':
                    print(f"{index+1}: Take a penalty")
                elif move == 'Q':
                    print(f"{index+1}: Quit the game")
                elif move == 'Pass':
                    print(f"{index+1}: Pass")
                elif type(move[0]) == int:
                    print(f"{index+1}: {move[0]} in {move[1]}")
                else:
                    print(f"{index+1}: {move[0][0]} in {move[0][1]} and {move[1][0]} in {move[1][1]}")
            
            move_choice = input("Choose a move (enter the corresponding number): ").upper()

            try:
                move_choice = int(move_choice)
                if move_choice < 1 or move_choice > len(possible_moves):
                    raise ValueError
                return move_choice
            except ValueError:
                print("Invalid input. Please try again.")

class GreedyPlayer(Agent):
    def choose_move(self, possible_moves):
        return 1  # Always chooses the first possible move

class HeuristicGreedyPlayer(Agent):
    def choose_move(self, possible_moves):
        # Choose the move that gives the highest immediate reward (number of X's)
        best_move = max(possible_moves, key=lambda move: move[0] if type(move[0]) == int else sum(move[0]))
        return possible_moves.index(best_move) + 1

class HeuristicSpacePlayer(Agent):
    def choose_move(self, possible_moves):
        # Choose the move that maximizes space on the score sheet
        # (e.g., if adding to a row with few X's opens up more possibilities)
        best_move = max(possible_moves, key=lambda move: self.calculate_space_gain(move))
        return possible_moves.index(best_move) + 1

    def calculate_space_gain(self, move):
        if type(move[0]) == int:  # Single move
            return move[0]
        else:  # Double move
            return sum(move[0]) + sum(move[1])

class QLearnPlayer(Agent):
    def __init__(self):
        self.q_table = {}

    def choose_move(self, possible_moves):
        # Randomly explore or exploit based on epsilon-greedy strategy
        epsilon = 0.2  # Exploration rate
        if random.random() < epsilon:
            return random.randint(1, len(possible_moves))
        else:
            # Choose the move with the highest Q-value
            best_move = max(possible_moves, key=lambda move: self.get_q_value(move))
            return possible_moves.index(best_move) + 1

    def get_q_value(self, move):
        # If move not in Q-table, initialize it with a default value
        if move not in self.q_table:
            self.q_table[move] = 0
        return self.q_table[move]

    def update_q_value(self, move, reward, learning_rate=0.1, discount_factor=0.9):
        # Update Q-value based on Q-learning update rule
        if move not in self.q_table:
            self.q_table[move] = 0
        self.q_table[move] += learning_rate * (reward + discount_factor * max(self.q_table.values()) - self.q_table[move])
