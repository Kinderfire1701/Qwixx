import random
import itertools
from dice import Dice
from agents import HumanPlayer, GreedyPlayer, HeuristicGreedyPlayer, HeuristicSpacePlayer, QLearnPlayer

class QwixxGame:
    def __init__(self, *player_types):
        self.players = self.initialize_players(*player_types)
        self.active_player_index = 0
        self.dice = [Dice('Red'), Dice('Yellow'), Dice('Green'), Dice('Blue'), Dice('White'), Dice('White')]
        self.game_over = False
        if any(player_type.lower() == "human" for player_type in player_types):
            self.print_info = True
        else:
            self.print_info = False
        self.player_types = player_types
    
    def refresh(self):
        self.players = self.initialize_players(*self.player_types)
        self.active_player_index = 0
        self.dice = [Dice('Red'), Dice('Yellow'), Dice('Green'), Dice('Blue'), Dice('White'), Dice('White')]
        self.game_over = False

    def initialize_players(self, *player_types):
        players = []
        for player_type in player_types:
            if player_type.lower() == "human":
                players.append(HumanPlayer())
            elif player_type.lower() == "greedy":
                players.append(GreedyPlayer())
            elif player_type.lower() == "heuristic_greedy":
                players.append(HeuristicGreedyPlayer())
            elif player_type.lower() == "heuristic_space":
                players.append(HeuristicSpacePlayer())
            elif player_type.lower() == "q_learn":
                players.append(QLearnPlayer(self))
        return players

    def print_score_sheets(self):
        print("Current Score Sheets:")
        for player in self.players:
            print(f"{player.__class__.__name__}:")
            for color, values in player.score_sheet.items():
                if color != 'Penalties':
                    last_number = values['last_number']
                    x_count = values['x_count']
                    if values['order'] == 'locked':
                        print(f"  {color}: Last Number: {last_number}, X Count: {x_count}, Locked")
                    else:
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
        self.move(active_player)
        if self.game_over == True:
            return

        # inactive players
        for other_player in self.players:
            if other_player != active_player:
                self.move(other_player)
                if self.game_over == True:
                    return

        # Change active player
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

        #update all players scoresheets to reflect locked rows
        self.lock()

        # Check end conditions
        if self.check_end_conditions():
            self.game_over = True

    def take_action(self,player,action):
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
        #print("Active player:")
        #print(player.__class__.__name__, ' =?= ', active_player.__class__.__name__)
        if player.__class__.__name__ == active_player.__class__.__name__:
            player.update_score_sheet(action)
        else:
            self.move(active_player)
        if self.game_over == True:
            return

        # inactive players
        for other_player in self.players:
            if other_player != active_player:
                #print("Inactive player player:")
                #print(player.__class__.__name__, ' =?= ', other_player.__class__.__name__)
                if player.__class__.__name__ == other_player.__class__.__name__:
                    player.update_score_sheet(action)
                else:
                    self.move(other_player)
                if self.game_over == True:
                    return

        # Change active player
        self.active_player_index = (self.active_player_index + 1) % len(self.players)

        #update all players scoresheets to reflect locked rows
        self.lock()

        # Check end conditions
        if self.check_end_conditions():
            self.game_over = True

        #return new state
        return self.get_state_representation()

    def get_possible_moves(self, player):
        if self.players[self.active_player_index] == player:
            white_dice_1 = next(die for die in self.dice if die.color == 'White')
            white_dice_2 = next(die for die in self.dice if die.color == 'White' and die != white_dice_1)

            # Generate possible moves
            possible_moves_white = []
            possible_moves_colored = []

            # Iterate through each color
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if self.check_valid_move(1, player.score_sheet[color], white_dice_1, white_dice_2):
                    possible_moves_white.append((white_dice_1.value + white_dice_2.value, color))

            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                for white_die in [white_dice_1, white_dice_2]:
                    for colored_die in [die for die in self.dice if die.color == color]:
                        if self.check_valid_move(2, player.score_sheet[color], white_die, colored_die):
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
            
            return possible_moves
        else:
            white_dice_1 = next(die for die in self.dice if die.color == 'White')
            white_dice_2 = next(die for die in self.dice if die.color == 'White' and die != white_dice_1)

            # Generate possible moves
            possible_moves = []

            # Iterate through each color
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if self.check_valid_move(1, player.score_sheet[color], white_dice_1, white_dice_2):
                    possible_moves.append((white_dice_1.value + white_dice_2.value, color))

            possible_moves.append('Pass')
            if isinstance(player, HumanPlayer):
                possible_moves.append('Q')

            return possible_moves

    def check_end_conditions(self, state=None):
        if state == None:
            # Check if any player has 4 penalties
            for player in self.players:
                if player.score_sheet['Penalties'] >= 4:
                    if self.print_info:
                        print(f"{player.__class__.__name__} has 4 penalties. Game over!")
                    return True

            # Check if two rows are locked
            locked_rows = 0
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if self.players[0].score_sheet[color]['order'] == 'locked':
                    locked_rows += 1
            if locked_rows >= 2:
                if self.print_info:
                    print("Two rows are locked. Game over!")
                return True

            return False
        else:
            for score_sheet in state['player_scores']:
                if score_sheet['Penalties'] >= 4:
                    if self.print_info:
                        print(f"{player.__class__.__name__} has 4 penalties. Game over!")
                    return True
                
            locked_rows = 0
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if state['player_scores'][0][color]['order'] == 'locked':
                    locked_rows += 1
            if locked_rows >= 2:
                if self.print_info:
                    print("Two rows are locked. Game over!")
                return True

            return False
    
    def lock(self):
        to_lock = []
        for player in self.players:
            for color in ['Red', 'Yellow', 'Green', 'Blue']:
                if player.score_sheet[color]['order'] == 'locked':
                    to_lock.append(color)
        for player in self.players:
            for color in to_lock:
                player.score_sheet[color]['order'] = 'locked'
    
    def move(self,player):
        possible_moves = self.get_possible_moves(player)

        # Prompt the choice method of each player
        if player.__class__.__name__ == "QLearnPlayer":
            state = self.get_state_representation()
            move_choice = player.choose_move(possible_moves, state)
        else:
            move_choice = player.choose_move(possible_moves)        

        chosen_move = possible_moves[move_choice]
        if self.print_info:
            print(f"{player.__class__.__name__} chose:", chosen_move)     

        if chosen_move == 'Q':
            self.game_over = True
            return
        else:
            player.update_score_sheet(chosen_move)
        return
        
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

        #reset the game
        self.refresh()

        return scores

    def calculate_score(self, player):
        return player.calculate_score()
    
    def get_state_representation(self):
        active_player = self.players[self.active_player_index]
        player_scores = [player.score_sheet for player in self.players]
        dice_values = [die.value for die in self.dice]
        
        # Construct state representation
        state_representations = {
            "active_player": active_player,
            "player_scores": player_scores,
            "dice_values": dice_values
        }

        return state_representations
    
    def win(self, player):
        scores = []
        for player in self.players:
            score = self.calculate_score(player)
            scores.append(score)
        winner_index = scores.index(max(scores))
        if self.players[winner_index].__class__.__name__ == player.__class__.__name__:
            return True
        else:
            return False