#!/usr/bin/env python3
""" Script for a CLI Mastermind Game """

from os import name as os_name
from time import sleep
from random import randrange
from subprocess import call


def screen_clear():
    """Clears the screen """
    call('clear' if os_name == 'posix' else 'cls')


class MasterMind:
    """ Encapsulates all code for a CLI MasterMind game """

    class Player:
        """ represents a player of the game """

        def __init__(self, name="Mastermind"):
            self.name = name
            self.points = 0

    def __init__(self):
        """ init """

        self.start_up()
        self.mastermind()

    def start_up(self):
        """ start up screen """
        screen_clear()
        print("Welcome to MasterMind!\n")
        sleep(1)
        print("Play with a friend or against the CPU!\n")
        input("Press any key to continue")
        screen_clear()

    def mastermind(self):
        """ mvp """
        p1, p2 = self.set_players()
        rounds = self.set_game_mode()

        if rounds:
            self.mastermind_game(rounds, p1, p2)
        else:
            self.mastermind_round(p1, p2)
            self.declare_winner(p1, p2)

        self.play_again_check()

    def set_players(self):
        """Gets player mode, either solo or multiplayer"""

        mode = input(self.choose_player_mode_string)
        screen_clear()

        if mode == "1":
            print("You've chosen Solo Mode! Can you beat a computer?\n")
        elif mode == "2":
            print("You've chosen Multiplayer Mode! Can you beat a human?\n")
            self.multiplayer = True
        else:
            print("Unrecognized input. Please enter 1 or 2\n")
            return self.set_players()

        p1_name = input("Player 1, what's your name? ")
        p1 = self.Player(p1_name)
        if self.multiplayer is True:
            p2_name = input("Player 2, what's your name? ")
        else:
            p2_name = "the CPU"
        p2 = self.Player(p2_name)

        input("Press any key to continue ")
        screen_clear()
        return p1, p2

    def set_game_mode(self):

        mode = input(self.choose_game_mode_string)
        rounds = 0

        if mode == "1":
            print("MasterMind Tournament selected!\n")
            rounds = input("How many innings? (1 - 10) ")
            try:
                rounds = int(rounds)
                if rounds > 10:
                    raise ValueError
            except ValueError:
                print("Unrecognized input.",
                      "Please enter a number between 1 and 10")
                return self.set_game_mode()
        elif mode == "2":
            print("Single round selected!\n")
            self.single_game = True
        else:
            print("Unrecognized input. Please enter 1 or 2\n")
            return self.set_game_mode()

        input("Press any key to continue ")
        screen_clear()
        return rounds

    def mastermind_game(self, rounds, p1, p2):
        """ a game of mastermind """

        current_round = 0
        while current_round <= rounds:
            print("Round {}!\n\n".format(current_round))
            print("{} is now the Mastermind!".format(p1.name))
            self.mastermind_round(p1, p2)
            sleep(3)
            screen_clear()
            self.grid = ""
            print("Round {}!\n\n".format(current_round))
            print("{} is now the Mastermind!".format(p2.name))
            self.mastermind_round(p2, p1)
            current_round += 1
            print('Rounds left: {}\n'.format(rounds) +
                  'Score:\n' +
                  '\t{}: {}\n'.format(p1.name, p1.points) +
                  '\t{}: {}\n'.format(p2.name, p2.points)
                  )
            sleep(3)
            screen_clear()
            self.grid = ""

        self.declare_winner(p1, p2)

    def mastermind_round(self, codebreaker, mastermind):
        """ a round of mastermind """

        solution = self.get_solution(mastermind)
        guesses_left = self.guesses_per_round

        while guesses_left > 1:

            print("Guesses left: {:d}\n".format(guesses_left))
            guess = self.get_code(codebreaker.name)
            black_pegs, white_pegs = self.compare_codes(guess, solution)
            self.print_grid(guess, black_pegs, white_pegs)

            if black_pegs == self.code_length:
                print("{} has won the round!".format(codebreaker.name))
                codebreaker.points += 1
                return

            print("{} is not {}'s code!\n".format(guess, mastermind.name))
            guesses_left -= 1
            mastermind.points += 1

        mastermind.points += 1
        screen_clear()
        print("{} is out of guesses!\n".format(codebreaker.name) +
              "{}'s code: {}\n\n".format(mastermind.name, solution) +
              "{} has won the round!".format(mastermind.name)
              )
        sleep(1)
        screen_clear()

    def get_solution(self, player):
        """ generates the Mastermind's solution """

        prompt = (
            "{name}, enter your Mastermind code!\n"
            "   * Your code must be {} digits long.\n\n"
            "{name}'s Mastermind code: "
        ).format(self.code_length, self.max_digit, name=player.name)
        if self.multiplayer is False:
            solution = ""
            for i in range(self.code_length):
                solution += str(randrange(self.max_digit + 1))
            return solution

        solution = self.get_code(prompt)
        while solution is None:
            print('Invalid code!\n')
            solution = self.get_code(prompt)
        screen_clear()
        print('Your code has been saved!')
        sleep(1.5)
        screen_clear()
        return solution

    def get_code(self, player):
        """ prompts the user for a code """

        prompt = "{}, enter a {}-digit code: ".format(player, self.code_length)
        code = input(prompt)
        try:
            code = code.split()[0]
        except:
            code = ""
        code_length = len(code)

        if code_length != self.code_length:
            print(
                "Invalid code! Your code must be",
                "{} digits long\n".format(self.code_length)
            )
            return self.get_code(player)

        for i in range(len(code)):
            try:
                if int(code[i]) > self.max_digit:
                    raise ValueError
            except ValueError:
                print(
                    "Invalid code! Only use digits between",
                    "0 and {}\n".format(self.max_digit)
                )
                return self.get_code(prompt)

        return code

    def compare_codes(self, guess, solution):
        """ compares the user's guess to the solution """

        white_pegs = 0
        black_pegs = 0
        positions = list(range(self.code_length))
        for i in range(self.code_length):
            for j in positions:
                if solution[i] == guess[j]:
                    if i == j:
                        black_pegs += 1
                        positions.remove(j)
                    elif i in positions and solution[i] == guess[i]:
                        black_pegs += 1
                        positions.remove(i)
                    else:
                        white_pegs += 1
                        positions.remove(j)
                    break
        return black_pegs, white_pegs

    def print_grid(self, string, black_pegs, white_pegs):
        """ prints the Mastermind board """

        first_row = ""
        for i in range(self.code_length):
            first_row += "|{}".format(string[i])
        first_row += "|"
        bottom_row = "\n" + "|-" * self.code_length + "|\n"
        bp = '\033[92m' + 'X' * black_pegs + '\033[0m'
        wp = 'X' * white_pegs
        if self.grid != "":
            self.grid += bottom_row
        self.grid += first_row + "  " + bp + wp
        print(self.grid)

    def declare_winner(self, player1, player2):

        if self.single_game is True:
            if player1.points:
                winner = player1
            else:
                winner = player2

        elif player1.points == player2.points:
            print("We have a tie!\n\n")
            sleep(2)
            print("We must settle this with a sudden death match!\n\n")
            sleep(2)
            response = input(
                "Who shall be the Mastermind?: " +
                "({} / {})".format(player1.name, player2.name)
            )
            if response == player1.name:
                mastermind = player1
                codebreaker = player2
            else:
                mastermind = player2
                codebreaker = player1
            print("Sudden death match time, here we go!")
            sleep(2)
            mastermind.points = codebreaker.points = 0
            self.single_game = True
            self.mastermind_round(codebreaker, mastermind)
            self.declare_winner(codebreaker, mastermind)

        elif player1.points > player2.points:
            winner = player1
        else:
            winner = player2

        print("{} has won the game!".format(winner.name))
        self.play_again_check()

    def play_again_check(self):
        """ Asks the user if they want to play again """

        response = input("Play again? (y/n): ").lower()
        if response in ["yes", "y", "Y"]:
            self.grid = ""
            self.multiplayer = False
            self.single_game = False
            self.mastermind()
        elif response in ["no", "n", "N"]:
            print("Thanks for playing! Goodbye\n")
            exit()
        else:
            print("Unknown response. Try again\n")
            self.play_again_check()

    grid = ""
    code_length = 4
    max_digit = 9
    allowed_digits = [str(x) for x in range(max_digit + 1)]
    multiplayer = False
    single_game = False
    guesses_per_round = 12
    choose_player_mode_string = (
        'How many players? Type:\n'
        '   1 for single player\n'
        '   2 for multi-player\n\n'
        'Enter response: ')
    choose_game_mode_string = (
        'Choose Game Mode! Type:\n'
        '   1 for MasterMind Tournament\n'
        '   2 for Single Round\n\n'
        'Enter response: '
    )


if __name__ == "__main__":
    MasterMind()
