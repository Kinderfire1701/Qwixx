import random
import itertools
from dice import Dice
from agents import HumanPlayer, GreedyPlayer, HeuristicGreedyPlayer, HeuristicSpacePlayer, QLearnPlayer

class QwixxGame:
    def __init__(self, player1_type, player2_type):
        self.players = self.initialize_players(player1_type, player2_type)
        self.score_sheets = {player: {'Red': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                                       'Yellow': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                                       'Green': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                                       'Blue': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                                       'Penalties': 0} for player in self.players}
        self.active_player_index = 0
        self.dice = [Dice('Red'), Dice('Yellow'), Dice('Green'), Dice('Blue'), Dice('White'), Dice('White')]
        self.game_over = False
        self.to_lock = []
        if player1_type == "human" or player2_type == "human":
            self.print_info = True
        else:
            self.print_info = False

    def initialize_players(self, player1_type, player2_type):
            players = []
            if player1_type == "human":
                players.append(HumanPlayer())
            elif player1_type == "greedy":
                players.append(GreedyPlayer())
            elif player1_type == "heuristic_greedy":
                players.append(HeuristicGreedyPlayer())
            elif player1_type == "heuristic_space":
                players.append(HeuristicSpacePlayer())
            elif player1_type == "Q_learn":
                players.append(QLearnPlayer())

            if player2_type == "human":
                players.append(HumanPlayer())
            elif player2_type == "greedy":
                players.append(GreedyPlayer())
            elif player2_type == "heuristic_greedy":
                players.append(HeuristicGreedyPlayer())
            elif player2_type == "heuristic_space":
                players.append(HeuristicSpacePlayer())
            elif player2_type == "Q_learn":
                players.append(QLearnPlayer())

            return players

    def print_score_sheets(self):
        print("Current Score Sheets:")
        for player, scores in self.score_sheets.items():
            print(f"{player.__class__.__name__}:")
            for color, values in scores.items():
                if color != 'Penalties':
                    last_number = values['last_number']
                    x_count = values['x_count']
                    print(f"  {color}: Last Number: {last_number}, X Count: {x_count}")
                else:
                    penalties = values
                    print(f"  {color}: {penalties}")
            print()

    def roll_dice(self):
        for die in self.dice:
            die.roll()


    def check_valid_move(self, phase, row, dice1, dice2):
        if phase == 1:
            if dice1.color != 'White' or dice2.color != 'White':
                return False
            if row['order'] == 'locked':
                return False
            sum_dice = dice1.value + dice2.value
            if row['x_count'] < 5:
                if row['order'] == 'increasing':
                    if row['last_number'] < sum_dice:
                        if sum_dice != 12:
                            return True
                elif row['order'] == 'decreasing':
                    if row['last_number'] > sum_dice:
                        if sum_dice != 2:
                            return True
            else:
                if row['order'] == 'increasing':
                    if row['last_number'] < sum_dice:
                            return True
                elif row['order'] == 'decreasing':
                    if row['last_number'] > sum_dice:
                            return True
        elif phase == 2:
            if (dice1.color != 'White' and dice2.color != 'White') or (dice1.color == 'White' and dice2.color == 'White'):
                return False
            if row['order'] == 'locked':
                return False
            sum_dice = dice1.value + dice2.value
            if row['x_count'] < 5:
                if row['order'] == 'increasing':
                    if row['last_number'] < sum_dice:
                        if sum_dice != 12:
                            return True
                elif row['order'] == 'decreasing':
                    if row['last_number'] > sum_dice:
                        if sum_dice != 2:
                            return True
            else:
                if row['order'] == 'increasing':
                    if row['last_number'] < sum_dice:
                            return True
                elif row['order'] == 'decreasing':
                    if row['last_number'] > sum_dice:
                            return True
        return False

    def play_round(self):
        player = self.players[self.active_player_index]
        self.roll_dice()
        if self.print_info:
            print(f"{player.__class__.__name__}'s turn:")
            print("Rolling dice...")
        
            # Print dice color and score
            if self.print_info:
                print("Dice:")
                for die in self.dice:
                    print(f"  {die.color}: {die.value}")

        active_player = self.players[self.active_player_index]

        # Active Player
        self.active_player_move(active_player)
        if self.game_over == True:
            return

        # inactive players
        for other_player in self.players:
            if other_player != active_player:
                self.inactive_player_move(other_player)
                if self.game_over == True:
                    return

        # Change active player
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

        #update all players scoresheets to reflect locked rows
        self.lock()

        # Check end conditions
        if self.check_end_conditions():
            self.game_over = True

    def check_end_conditions(self):
        # Check if any player has 4 penalties
        for player in self.players:
            if self.score_sheets[player]['Penalties'] >= 4:
                if self.print_info:
                    print(f"{player.__class__.__name__} has 4 penalties. Game over!")
                return True

        # Check if two rows are locked
        locked_rows = 0
        for color in ['Red', 'Yellow', 'Green', 'Blue']:
            if self.score_sheets[self.players[0]][color]['order'] == 'locked':
                locked_rows += 1
        if locked_rows >= 2:
            if self.print_info:
                print("Two rows are locked. Game over!")
            return True

        return False
    
    def lock(self):
        for color in self.to_lock:
            for player in self.players:
                self.score_sheets[player][color]['order'] = 'locked'
        self.to_lock = []
    
    def inactive_player_move(self,player):
        white_dice_1 = next(die for die in self.dice if die.color == 'White')
        white_dice_2 = next(die for die in self.dice if die.color == 'White' and die != white_dice_1)

        # Generate possible moves
        possible_moves = []

        # Iterate through each color
        for color in ['Red', 'Yellow', 'Green', 'Blue']:
            if self.check_valid_move(1, self.score_sheets[player][color], white_dice_1, white_dice_2):
                possible_moves.append((white_dice_1.value + white_dice_2.value, color))

        possible_moves.append('Pass')
        if isinstance(player, HumanPlayer):
            possible_moves.append('Q')

        # Prompt the choice method of each player
        move_choice = player.choose_move(possible_moves)        

        chosen_move = possible_moves[move_choice - 1]

        if chosen_move == 'Q':
            self.game_over = True
            return
        else:
            self.update_score_sheet(player, chosen_move)
        return
    
    def active_player_move(self,player):
        white_dice_1 = next(die for die in self.dice if die.color == 'White')
        white_dice_2 = next(die for die in self.dice if die.color == 'White' and die != white_dice_1)

        # Generate possible moves
        possible_moves_white = []
        possible_moves_colored = []

        # Iterate through each color
        for color in ['Red', 'Yellow', 'Green', 'Blue']:
            if self.check_valid_move(1, self.score_sheets[player][color], white_dice_1, white_dice_2):
                possible_moves_white.append((white_dice_1.value + white_dice_2.value, color))

        for color in ['Red', 'Yellow', 'Green', 'Blue']:
            for white_die in [white_dice_1, white_dice_2]:
                for colored_die in [die for die in self.dice if die.color == color]:
                    if self.check_valid_move(2, self.score_sheets[player][color], white_die, colored_die):
                        possible_moves_colored.append((white_die.value + colored_die.value, color))

        possible_moves = list(itertools.product(possible_moves_white, possible_moves_colored))
        possible_moves = possible_moves + possible_moves_white + possible_moves_colored

        #remove duplicates
        nondup_possible_moves = list(set(possible_moves))
        possible_moves = []

        #remove trivially similar moves (12 in green and 12 in green), for example
        for move in nondup_possible_moves:
            if type(move[0]) == int:
                possible_moves.append(move)
            else:
                if move[0] != move[1]:
                    possible_moves.append(move)
            
        possible_moves.append('Penalty')
        if isinstance(player, HumanPlayer):
            possible_moves.append('Q')

        # Prompt the choice method of each player
        move_choice = player.choose_move(possible_moves)        

        chosen_move = possible_moves[move_choice - 1]

        if chosen_move == 'Q':
            self.game_over = True
            return
        else:
            self.update_score_sheet(player, chosen_move)
        return

    def update_score_sheet(self, player, chosen_move):
        if chosen_move == 'Penalty':
            self.score_sheets[player]['Penalties'] += 1
            return
        if chosen_move == 'Pass':
            return
        if type(chosen_move[0]) == int:
            self.add_number(player,chosen_move)
        else:
            self.add_number(player, chosen_move[0])
            self.add_number(player, chosen_move[1])
            return
        
    def add_number(self, player, move):
            row = self.score_sheets[player][move[1]]
            if row['order'] == 'increasing' and move[0] == 12:
                row['last_number'] = move[0]
                row['x_count'] += 2
                self.to_lock.append(move[1])
            elif row['order'] == 'decreasing' and move[0] == 2:
                row['last_number'] = move[0]
                row['x_count'] += 2
                self.to_lock.append(move[1])
            else:
                row['last_number'] = move[0]
                row['x_count'] += 1
        
    def play(self):
        if self.print_info:
            print("Welcome to Qwixx!")

        while not self.game_over:
            if self.print_info:
                self.print_score_sheets()
            self.play_round()

        if self.print_info:
            print("Game Over!")
            self.print_score_sheets()

        #return scores
        scores = []
        for player in self.players:
            score = self.calculate_score(player)
            scores.append(score)
            if self.print_info:
                print(f"player {player} score == {score}")

        return scores

    def calculate_score(self, player):
        score_sheet = self.score_sheets[player]
        total_score = 0
        for color, values in score_sheet.items():
            if color != 'Penalties':
                x_count = values['x_count']
                row_score = (x_count * (x_count + 1)) // 2
                total_score += row_score
        # Deduct 5 points for each penalty
        total_score -= 5 * score_sheet['Penalties']
        return total_score

# Start the game
game = QwixxGame("greedy","greedy")

scores = game.play()
print(scores)