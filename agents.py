from abc import ABC, abstractmethod
import random
import copy
import time

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
            row['order'] = 'locked'
        elif row['order'] == 'decreasing' and move[0] == 2:
            row['last_number'] = move[0]
            row['x_count'] += 2
            row['order'] = 'locked'
        else:
            row['last_number'] = move[0]
            row['x_count'] += 1

class HumanPlayer(Agent):
    def choose_move(self, possible_moves):
        while True:
            print("Possible moves:")
            for index, move in enumerate(possible_moves):
                if move == 'Penalty':
                    print(f"{index}: Take a penalty")
                elif move == 'Q':
                    print(f"{index}: Quit the game")
                elif move == 'Pass':
                    print(f"{index}: Pass")
                elif type(move[0]) == int:
                    print(f"{index}: {move[0]} in {move[1]}")
                else:
                    print(f"{index}: {move[0][0]} in {move[0][1]} and {move[1][0]} in {move[1][1]}")
            
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

        #restore score sheet to original state
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

        #restore score sheet to original state
        self.score_sheet = copy.deepcopy(original_score_sheet)
        
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
            #override for locking
            if self.score_sheet[color]['order'] == 'increasing' and number == 12:
                return True
            elif self.score_sheet[color]['order'] == 'decreasing' and number == 2:
                return True
            #regular constraints
            if last_number >= 5 and last_number <= 8:
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

        #restore score sheet to original state
        self.score_sheet = copy.deepcopy(original_score_sheet)
        
        # Return the index of the move with the highest score
        return best_move_index

class HeuristicSpacePlayer(Agent):
    def choose_move(self, possible_moves):
            least_distance = float('inf')
            best_move_index = None
            
            # Iterate through all possible moves
            for i, move in enumerate(possible_moves):
                if move == 'Pass':
                    distance = 1
                elif move == 'Penalty':
                    distance = 13
                else:
                    distance = self.get_dist(move)
                if distance < least_distance:
                    least_distance = distance
                    best_move_index = i
                            
            # Return the index of the move with the lowest spaces used
            return best_move_index

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

class QLearnPlayer(Agent):
    def __init__(self, game):
        self.game = game

    def q_learn(self, time_limit, gamma=0.95, epsilon=0.09, alpha_initial=0.175, alpha_decay=0.995):
        def epsilon_greedy_policy(state):
            if random.random() < epsilon:
                # Exploration: choose a random action
                return random.randint(0, self.game.action_space_size() - 1)
            else:
                # Exploitation: choose the action with the highest Q-value
                return max(range(self.game.action_space_size()), key=lambda a: q_values.get((state, a), 0))

        q_values = {}
        a_values = {}

        # Q-learning loop
        start_time = time.time()
        elapsed_time = 0
        while elapsed_time < time_limit:
            state = self.game.get_initial_state()
            while not self.game.is_terminal(state):
                action = epsilon_greedy_policy(state)
                next_state, reward = self.game.take_action(state, action)

                if self.game.is_terminal(next_state):
                    max_q_prime = 0
                else:
                    max_q_prime = max(q_values.get((next_state, a), 0) for a in range(self.game.action_space_size()))

                q_values[(state, action)] = q_values.get((state, action), 0) + a_values.get((state, action), alpha_initial) * (
                        reward + gamma * max_q_prime - q_values.get((state, action), 0))
                state = next_state
                a_values[(state, action)] = a_values.get((state, action), alpha_initial) * alpha_decay

            # Update elapsed time
            elapsed_time = time.time() - start_time

        # Pick the best policy
        def policy(state):
            max_q_value = float("-inf")
            best_action = None

            for action in range(self.game.action_space_size()):
                q_value = q_values.get((state, action), 0)
                if q_value > max_q_value:
                    max_q_value = q_value
                    best_action = action

            return best_action

        return policy

    def choose_move(self, possible_moves):
        # Implement Q-learning
        policy = self.q_learn(time_limit=10)  # Set time limit as needed

        # Convert state to a format suitable for Q-learning
        state = self.game.get_state_representation()

        # Choose action based on learned policy
        action = policy(state)

        return action