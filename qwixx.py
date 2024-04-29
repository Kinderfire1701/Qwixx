import random
import itertools
from dice import Dice
from agents import HumanPlayer

class QwixxGame:
    def __init__(self):
        self.players = [HumanPlayer(), HumanPlayer()]
        self.score_sheets = {player: {'Red': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                                       'Yellow': {'last_number': 0, 'order': 'increasing', 'x_count': 0},
                                       'Green': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                                       'Blue': {'last_number': 13, 'order': 'decreasing', 'x_count': 0},
                                       'Penalties': 0} for player in self.players}
        self.active_player_index = 0
        self.dice = [Dice('Red'), Dice('Yellow'), Dice('Green'), Dice('Blue'), Dice('White'), Dice('White')]
        self.game_over = False
        self.to_lock = []

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
        print(f"{player.__class__.__name__}'s turn:")
        print("Rolling dice...")
        self.roll_dice()
        
        # Print dice color and score
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
                print(f"{player.__class__.__name__} has 4 penalties. Game over!")
                return True

        # Check if two rows are locked
        locked_rows = 0
        for player in self.players:
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if self.score_sheets[player][color]['order'] == 'locked':
                    locked_rows += 1
        if locked_rows >= 2:
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
        print("Welcome to Qwixx!")

        while not self.game_over:
            self.print_score_sheets()
            self.play_round()

        print("Game Over!")
        self.print_score_sheets()

# Start the game
game = QwixxGame()

game.play()