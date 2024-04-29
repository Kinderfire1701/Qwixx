from abc import ABC, abstractmethod

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