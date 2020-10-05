#!/usr/bin/env python3
""" Script for a CLI Mastermind Game """

from os import name as os_name
from time import sleep
from random import randrange, sample
from subprocess import call
from copy import deepcopy


def screen_clear():
    """Clears the screen """
    call('clear' if os_name == 'posix' else 'cls')


class MasterMind:
    """ Encapsulates all code for a CLI MasterMind game """

    class Player:
        """ represents a player of the game """

        def __init__(self, name="Mastermind", cpu=False):
            self.name = name
            self.points = 0
            self.is_cpu = cpu
            self.guess_history = []

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
            p1 = self.Player(input("Player 1, what's your name? "))
            p2 = self.Player("the CPU", True)
        elif mode == "2":
            print("You've chosen Multiplayer Mode! Can you beat a human?\n")
            p1 = self.Player(input("Player 1, what's your name? "))
            p2 = self.Player(input("Player 2, what's your name? "))
        else:
            print("Unrecognized input. Please enter 1 or 2\n")
            return self.set_players()

        input("\nPress any key to continue ")
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

        current_round = 1
        while current_round <= rounds:
            # TOP INNING
            self.mastermind_round(p2, p1, current_round)
            current_round += 0.5
            # BOTTOM INNING
            self.mastermind_round(p1, p2)
            current_round += 0.5

            # INNING SUMMARY
            print('Rounds left: {}\n'.format(rounds) +
                  'Score:\n' +
                  '\t{}: {}\n'.format(p1.name, p1.points) +
                  '\t{}: {}\n'.format(p2.name, p2.points)
                  )
            input("\nPress any key to continue ")
            screen_clear()

        self.declare_winner(p1, p2)

    def mastermind_round(self, codebreaker, mastermind, round=None):
        """ a round of mastermind """

        if round is not None:
            print("Round {}!\n\n".format(round))

        if codebreaker.is_cpu is True:
            codebreaker.logic = deepcopy(self.a)

        print("{} is the Mastermind!".format(mastermind.name))

        solution = self.get_solution(mastermind)
        guesses_left = self.guesses_per_round
        black_pegs = 0
        white_pegs = 0
        guess = ""

        while guesses_left >= 1:

            print("Guesses left: {:d}\n".format(guesses_left))
            if codebreaker.is_cpu is True:
                codebreaker.guess_history.append(guess)
                guess = self.get_guess(black_pegs, white_pegs, codebreaker)
                sleep(0.2)
            else:
                guess = self.get_code(codebreaker)
            black_pegs, white_pegs = self.compare_codes(guess, solution)
            self.print_grid(guess, black_pegs, white_pegs)

            if black_pegs == self.code_length:
                codebreaker.points += 1
                codebreaker.guess_history = []
                print("{} has won the round!".format(codebreaker.name))
                sleep(1.5)
                screen_clear()
                self.grid = ""
                return

            print("{} is not {}'s code!\n".format(guess, mastermind.name))
            guesses_left -= 1
            mastermind.points += 1

        mastermind.points += 1
        screen_clear()
        print("{} is out of guesses!\n".format(codebreaker.name) +
              "{}'s code: {}\n\n".format(mastermind.name, solution) +
              "{} has won this round!".format(mastermind.name)
              )
        sleep(1.5)
        screen_clear()
        self.grid = ""
        codebreaker.guess_history = []

    def get_solution(self, player):
        """ generates the Mastermind's solution """

        prompt = (
            "{name}, enter your Mastermind code!\n"
            "   * Your code must be {} digits long.\n\n"
            "{name}'s Mastermind code: "
        ).format(self.code_length, self.max_digit, name=player.name)
        if player.is_cpu is True:
            solution = ""
            for i in range(self.code_length):
                solution += str(randrange(self.max_digit + 1))
            return solution

        solution = self.get_code(player, prompt)
        while solution is None:
            print('Invalid code!\n')
            solution = self.get_code(player, prompt)
        screen_clear()
        print('Your code has been saved!')
        sleep(1.5)
        screen_clear()
        return solution

    def get_guess(self, black_pegs, white_pegs, cpu):

        prev_guess = cpu.guess_history[-1]

        if len(prev_guess) == self.code_length:
            total_pegs = black_pegs + white_pegs

            if total_pegs == 0:
                for options in cpu.logic.values():
                    for digit in prev_guess:
                        if digit in options:
                            options.remove(digit)
            elif total_pegs == 4:
                for options in cpu.logic.values():
                    for digit in options:
                        if digit not in prev_guess:
                            options.remove(digit)

            if black_pegs == 0:
                for i in range(self.code_length):
                    if prev_guess[i] in cpu.logic[str(i)]:
                        cpu.logic[str(i)].remove(prev_guess[i])

                # print("Error! in get_guess")
                # print("8 seconds puhleaze...")
                # sleep(5)

        unchecked_nums = [str(i) for i in range(self.max_digit + 1)]
        for guess in cpu.guess_history:
            for digit in guess:
                if digit in unchecked_nums:
                    unchecked_nums.remove(digit)
        guess = ""
        for num in unchecked_nums:
            guess += num
            if len(guess) == 4:
                break
        while len(guess) < 4:
            guess += sample(cpu.logic[str(len(guess))], 1)[0]
        return guess

    def get_code(self, player, prompt=None):
        """ prompts the user for a code """

        if player.is_cpu is True:
            sleep(0.2)
            return self.get_solution(player)

        if prompt is None:
            prompt = "{}, enter a {}-digit code: "
        prompt = prompt.format(player.name, self.code_length)
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
                return self.get_code(player, prompt)

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
    single_game = False
    guesses_per_round = 30
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
    a = {}
    for i in range(code_length):
        a.update({str(i): [str(j) for j in range(max_digit + 1)]})


if __name__ == "__main__":
    MasterMind()
