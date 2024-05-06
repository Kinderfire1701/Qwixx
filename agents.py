from abc import ABC, abstractmethod
import random
import copy

class Agent:
    def __init__(self):
        self.score_sheet = {'Red': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                            'Yellow': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                            'Green': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                            'Blue': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                            'Penalties': 0}

    def choose_move(self, possible_moves):
        raise NotImplementedError

    def calculate_score(self):
        total_score = 0
        for color, values in self.score_sheet.items():
            if color != 'Penalties':
                x_count = values['x_count']
                row_score = (x_count * (x_count + 1)) // 2
                total_score += row_score
        # Deduct 5 points for each penalty
        total_score -= 5 * self.score_sheet['Penalties']
        return total_score
    
    def update_score_sheet(self, chosen_move):
        if chosen_move == 'Penalty':
            self.score_sheet['Penalties'] += 1
            return
        if chosen_move == 'Pass':
            return
        if type(chosen_move[0]) == int:
            self.add_number(chosen_move)
        else:
            self.add_number(chosen_move[0])
            self.add_number(chosen_move[1])
            return

    def add_number(self, move):
        row = self.score_sheet[move[1]]
        if row['order'] == 'increasing' and move[0] == 12:
            row['last_number'] = move[0]
            row['x_count'] += 2
        elif row['order'] == 'decreasing' and move[0] == 2:
            row['last_number'] = move[0]
            row['x_count'] += 2
        else:
            row['last_number'] = move[0]
            row['x_count'] += 1

class HumanPlayer(Agent):
    def choose_move(self, possible_moves):
        print("Available moves:")
        for i, move in enumerate(possible_moves, 1):
            print(f"{i}: {move}")
        choice = int(input("Choose your move: "))
        return choice

class GreedyPlayer(Agent):
    def choose_move(self, possible_moves):
        highest_score = float('-inf')
        best_move_index = None
        
        # Initialize an empty dictionary to store the original score sheet
        original_score_sheet = copy.deepcopy(self.score_sheet)
        
        # Iterate through all possible moves
        for i, move in enumerate(possible_moves):
            
            self.update_score_sheet(move)
            score_after_move = self.calculate_score()
            
            if score_after_move > highest_score:
                highest_score = score_after_move
                best_move_index = i
            
            self.score_sheet = copy.deepcopy(original_score_sheet)
        
        # Return the index of the move with the highest score
        return best_move_index


class HeuristicGreedyPlayer(Agent):
    def choose_move(self, possible_moves):
        # Initialize variables to track the best move and its score
        best_move_index = None
        best_score = float('-inf')
        best_distance = float('inf')

        original_score_sheet = copy.deepcopy(self.score_sheet)
        
        # Iterate through all possible moves
        for i, move in enumerate(possible_moves):
            #skip pass or penalty
            if move == 'Pass' or move == 'Penalty':
                continue

            # Check if the move satisfies the heuristic constraints
            distance = self.get_dist(move)
            if self.check_constraints(move):
                # Calculate score after making the move
                self.score_sheet = copy.deepcopy(original_score_sheet)
                self.update_score_sheet(move)
                score_after_move = self.calculate_score()
                
                # Check if the score after the move is better than the current best score
                if score_after_move > best_score or (score_after_move == best_score and distance < best_distance):
                    # Update the best move
                    best_move_index = i
                    best_score = score_after_move
                    best_distance = distance
        
        # If no move satisfies the constraint, resort to greedy choice
        if best_move_index is None:
            if 'Pass' in possible_moves:
                return possible_moves.index('Pass')
            else:
                return self.greedy_choice(possible_moves)
        
        return best_move_index
    
    def check_constraints(self,moves):
        if type(moves[0]) == int:
            #get info
            number, color = moves
            last_number = self.score_sheet[color]['last_number']
            distance = abs(number - last_number)

            #check constraints
            if last_number >= 5 and last_number <= 9:
                    if distance <= 2:
                        return True
            elif distance <= 3:
                return True
            else:
                return False
        else:
            for move in moves:
                #get info
                number, color = move
                last_number = self.score_sheet[color]['last_number']
                distance = abs(number - last_number)
                
                #check constraints
                if last_number >= 5 and last_number <= 9:
                        if distance <= 2:
                            continue
                elif distance <= 3:
                    continue
                else:
                    return False
            return True
        
    def get_dist(self,moves):
        if type(moves[0]) == int:
            #get info
            number, color = moves
            last_number = self.score_sheet[color]['last_number']

            #calculate distance
            distance = abs(number - last_number)
            return distance
        else:
            overall_dist = 0
            for move in moves:
                #get info
                number, color = move
                last_number = self.score_sheet[color]['last_number']

                #calculate distance
                distance = abs(number - last_number)
                overall_dist += distance
            return overall_dist
        
    def greedy_choice(self, possible_moves):
        highest_score = float('-inf')
        best_move_index = None
        
        # Initialize an empty dictionary to store the original score sheet
        original_score_sheet = copy.deepcopy(self.score_sheet)
        
        # Iterate through all possible moves
        for i, move in enumerate(possible_moves):
            
            self.update_score_sheet(move)
            score_after_move = self.calculate_score()
            
            if score_after_move > highest_score:
                highest_score = score_after_move
                best_move_index = i
            
            self.score_sheet = copy.deepcopy(original_score_sheet)
        
        # Return the index of the move with the highest score
        return best_move_index

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
