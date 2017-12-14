# Author:       Thng Zhe Yu Samuel
# Updated:      8 October 2017
# Course:       EE4483 AI & Data Mining
# Project:      Individual Project 2
# Description:  Tic Tac Toe with AI (heuristics)
# Work Time:    ~ 7 Hours
# Comments:     - Second Script from scratch, Proud of it.
#               - Using Python 2.
#               - Getting faster at the syntax.
#               - Used 2 heuristics, one best move, one defence.
################################################

""" TicTacToe Shifu.

This script is a demonstration of the Tic Tac Toe game,
with the AI powered by heuristics.

Classes:
    TicTacToe:
        Game of TicTacToe and it's relavent logic required for 2 players.
        Lines 58 - 208.

    TicTacToeShifu:
        AI logic to play a game of TicTacToe.
        Lines 211 - 392

Notable Functions:
    getDefenceMoves(game):
        Calculate heuristics for defence against human player.
        Lines 252 - 300

    getBestMoves(game):
        Calculate heuristics for position highest options to win.
        Lines 301 - 345

    play(game):
        AI logic to play a round based on heuristics value.
        Lines 346 - 392

    game():
        Game master logic. Controls flow of game.
        Lines 395 - 471

Main program loop starts at line 473.
"""


import random   # For some random decisions.
import os       # Clear screen.

# Turn on debug mode to view AI weights when running program.
AIdebug = False

# Default starting value, used to toggle player play again option.
playAgain = True


class TicTacToe:
    # Handles all Tic Tac Toe Gameboard
    def __init__(self, starterMark):
        # 0: Starter Player Mark, 1-9: Board Positions.
        self.board = [None] * 10
        self.board[0] = starterMark
        self.currentPlayer = starterMark

    # Returns board status (for AI to calculate).
    def getboard(self): return self.board

    # Returns true if currentPlayer is mark.
    def isTurn(self, mark): return self.currentPlayer == mark

    # Returns true if position is open to play.
    def isPlayable(self, position):
        return position in range(1, 10) and self.board[position] is None

    # Returns list of possible moves.
    def moves(self):
        return [p for p, _ in enumerate(self.board) if self.isPlayable(p)]

    # Returns list of positions occupied by mark.
    def positions(self, mark):
        return [p for p, bM in enumerate(self.board) if bM is mark]

    # Checks if mark is a winner.
    def isWinner(self, mark):
        # Returns true if win case detected for mark ("X" or "O").
        def testSequentialWin(mark, positions, offsets):
            # Sequential wins are each have 3 states, and same offsets.
            # Returns true if any sequential win states are met.
            sStatus = dict()
            for position in positions:
                sStatus.update({position: True})
                for offset in offsets:
                    if (self.board[position + offset] != mark):
                        sStatus[position] = False
            return True in sStatus.values()

        vWin = testSequentialWin(mark, [1, 2, 3], [0, 3, 6])  # Verticals
        hWin = testSequentialWin(mark, [1, 4, 7], [0, 1, 2])  # Horizontals
        dWin = testSequentialWin(mark, [5], [-2, 0, 2])  # [3,5,7]
        dWin = testSequentialWin(mark, [5], [-4, 0, 4]) or dWin  # [1,5,9]
        return (dWin or vWin or hWin)

    # Returns true if there is a winner.
    def hasWinner(self): return self.isWinner("X") or self.isWinner("O")

    # Returns true if board is full.
    def draw(self): return None not in self.board

    # Returns false if game ended..
    def canPlay(self): return (not self.hasWinner()) and (not self.draw())

    # Makes a move, only allow moves when is current player.
    def play(self, position, mark):

        # Changes the current player after moving.
        def swapMark(): self.currentPlayer = ("X", "O")[self.currentPlayer is "X"]

        if self.currentPlayer is mark:
            self.board[position] = mark
            swapMark()

    # [UI] Board Logic and layout. The fancy stuff here.
    def printUI(self, isAIFirst, playerMark):
        firstMsg = ("You are", "The AI is")[isAIFirst]
        var = dict()
        var.update({'mark': playerMark, 'start': firstMsg})
        for pos, mark in enumerate(self.board):
            if pos in range(1, 10):
                var.update({str(pos): (mark, " ")[mark is None]})
        message = """
    o------------------------------------o
    |  Welcome to Samuel's Tic Tac Toe!  |
    o------------------------------------o

    + -[BOARD]- +   ||   +[POSITIONS]+   Your mark: \"{mark}\"
    | {A} | {B} | {C} |   ||   | 1 | 2 | 3 |   {start} the first player.
    + - + - + - +   ||   + - + - + - +
    | {D} | {E} | {F} |   ||   | 4 | 5 | 6 |
    + - + - + - +   ||   + - + - + - +
    | {G} | {H} | {L} |   ||   | 7 | 8 | 9 |
    + - + - + - +   ||   + - + - + - +
    """.format(
            mark=var['mark'], start=var['start'],
            A=var['1'], B=var['2'], C=var['3'],
            D=var['4'], E=var['5'], F=var['6'],
            G=var['7'], H=var['8'], L=var['9'])
        print(message)


# Logic for the AI
class TicTacToeShifu:
    """Contains logic for the AI.

    Houses 3 main functions.
    getDefenceMoves(game) calculates heuristics for Defence.
    getBestMoves(game) calculates heuristics for Best moves.
    play(game) uses the above two functions to make the best choice
    for a given game and plays a round.

    Args:
    shifuMark (str): The AI's Mark ("X" or "O").

    Attributes:
        shifuMark (str): Mark for the AI.
        oppMark (str): Opponent(Usually Human)'s mark.

    """
    # Handles all AI Moves

    def __init__(self, shifuMark):
        # Assign marker to the AI.
        self.shifuMark = shifuMark
        self.oppMark = ("X", "O")[self.shifuMark == "X"]
        self.winningSets = [[1, 2, 3], [4, 5, 6], [7, 8, 9],  # Horizontals
                            [1, 4, 7], [2, 5, 8], [3, 6, 9],  # Verticals
                            [1, 5, 9], [3, 5, 7]]             # Diagonals

        # [Chance to Loose]
        # Borderline is 5.372<something> for defence weight multiplier.
        # AI will never lose if it starts first. (50%)
        # But it may lose at a 1% rate if human starts first.
        # Making it fun if you got a 5% chance to win.
        # This formula decides if it wins or looses.
        # chanceToLoose = 0.1
        # randWgt = range(5372, int(5372 + (1 / chanceToLoose)) + 1)
        # Weights, Use 5.373 as defIncrement value for best results.
        self.defIncrement = 5.373  # random.choice(randWgt) / 1000.0
        self.bestIncrement = 1

    def getDefenceMoves(self, game):
        """Calculates defence heuristics to block human from winning.
        Args:
        game (TicTacToe): Game for the AI to calculate heuristics for.

        Returns:
            dict: Returns dictionary (key: positions, value: defence weight).
        """
        # Get heuristics for defence.
        Moves = game.moves()
        Board = game.getboard()

        def isOppWinning(Set):
            # Check if opponent is advancing in a given moveset.
            for position in Set:
                if Board[position] == self.oppMark:
                    return True
            return False

        def incrementDefenceMul(posDict, Set):
            # Conditional weights for defence
            hDict = posDict
            currPos = game.positions(self.oppMark)
            incrementVal = 1
            for position in Set:
                if position in currPos:
                    incrementVal *= self.defIncrement
            for position in Set:
                if position in hDict.keys():
                    hDict[position] += incrementVal
            return hDict

        # Actual defence heuristics calculation
        hMuls = dict()
        for position in Moves:
            # Create default heuristic values for all possible moves.
            hMuls.update({position: 1})

        for winningSet in self.winningSets:
            # Check each winning set.
            if isOppWinning(winningSet):
                # If opponent winning, not in defence heuristics.
                hMuls = incrementDefenceMul(hMuls, winningSet)
        # Return heuristics.
        return hMuls

    def getBestMoves(self, game):
        """Calculates heuristics for positions with highest variations to win.
        Args:
        game (TicTacToe): Game for the AI to calculate heuristics for.

        Returns:
            dict: Returns dictionary (key: positions, value: option weight).
        """
        # Useful status registers
        Moves = game.moves()
        Board = game.getboard()

        def isPossibleWin(Set):
            # Returns false if the set cannot be used to win.
            # Assume possible then eliminate based on opponent placement.
            for position in Set:
                if Board[position] == self.oppMark:
                    return False
            return True

        def incrementHeuristics(Dict, Set):
            # Similar to defence heuristics.
            tempDict = Dict
            currPos = game.positions(self.shifuMark)
            incrementVal = 1
            for position in Set:
                if position in currPos:
                    incrementVal += self.bestIncrement
            for position in Set:
                if position in tempDict.keys():
                    tempDict[position] += incrementVal
            return tempDict

        # Initialize dictionary {Position : Heuristic Value}.
        hVals = dict()

        for position in Moves:
            hVals.update({position: 1})

        for winningSet in self.winningSets:
            if isPossibleWin(winningSet):
                hVals = incrementHeuristics(hVals, winningSet)

        return hVals

    def play(self, game):
        """Performs a move on the given game.
        Args:
        game (TicTacToe): Game for the AI to play on.

        Returns:
            bool: True if AI successfully moved, False otherwise.
        """
        # Calculate heuristics.
        hBest = self.getBestMoves(game)
        hDef = self.getDefenceMoves(game)

        heuristics = dict()
        for key, value in hBest.items():
            heuristics.update({key: (value * hDef[key])})

        if AIdebug:
            print("\n\n==== AI Debug Log ====")
            print("AI Chance to loose:" + str(self.defIncrement <= 5.3723))
            print("Best: " + str(hBest))
            print("Def: " + str(hDef))
            print("Combined: " + str(heuristics))
        # Get position of highest ranked move.
        # hTop = max(heuristics, key=heuristics.get)

        # Prune Heuristics
        if len(heuristics) > 0:
            hMax = heuristics[max(heuristics, key=heuristics.get)]
            # Filter highest weighted heuristics.
            maxHeuristics = dict()
            for key, value in heuristics.items():
                if value >= hMax:
                    maxHeuristics.update({key: value})
            hTop = random.choice(list(maxHeuristics))
        elif len(game.moves()) > 0:
            hTop = random.choice(game.moves())
        else:
            return False

        # Ensure the decision is playable and it's shifu's turn.
        if game.isPlayable(hTop) and game.isTurn(self.shifuMark):
            # If so, play the move with the highest chance of winning.
            if AIdebug:
                print("Final Move: " + str(hTop))
                print("==== End Log ====")
            game.play(hTop, self.shifuMark)
            return True


# Game Master
def game():
    """"
    Basic GameMaster to control game flow.

    Returns:
        bool: True if player opted to play again, False otherwise.
    """

    # New Instance of tictactoe and shifu per game.
    starter = random.choice(["O", "X"])
    gameInstance = TicTacToe(starter)
    theShiFu = TicTacToeShifu(random.choice(["O", "X"]))
    isAIFirst = gameInstance.currentPlayer == theShiFu.shifuMark

    # Sequence of tasks for a human to play a round.
    def humanPlay():
        # Player - "O"
        choice = input("   Make a move " + str(gameInstance.moves()) + ":")
        while not gameInstance.isPlayable(choice):
            message = "   Please make a valid move "
            message = message + str(gameInstance.moves()) + ":"
            choice = input(message)
        gameInstance.play(choice, theShiFu.oppMark)

    # Sequence of tasks for AI to play a round.
    def AIPlay():
        theShiFu.play(gameInstance)

    def gameEnded():
        # Tasks to do when game has ended in win/lose/draw
        printBoard()
        # Report win / lose / draw
        if gameInstance.isWinner(theShiFu.oppMark):
            print("   Winner Winner Chicken Dinner!   :D\n")
        elif gameInstance.isWinner(theShiFu.shifuMark):
            print("   You Lose!   :(\n")
        elif gameInstance.draw():
            print("   It's a Draw!   :|\n")
        # Ask to repeat
        return raw_input("   Play again? (y/n): ").lower() == "y"

    # [UI] Clear Screen and Print Board.
    def printBoard():
        # Clear screen, Print sample, Print currentBoard.
        if not AIdebug:
            os.system('cls' if os.name == 'nt' else 'clear')
        gameInstance.printUI(isAIFirst, theShiFu.oppMark)

    # [UI] Greet goodbye.
    def sayGoodBye():
        # Say goodbye if not playing again.
        if playAgain is False:
            print("""
    o---------------------o
    | Thanks for playing! |
    o---------------------o
            """)

    # Rudimentary game loop.
    while gameInstance.canPlay():
        if isAIFirst:
            AIPlay()
            printBoard()
            if gameInstance.canPlay():
                humanPlay()
            else:
                break
        else:
            printBoard()
            humanPlay()
            if gameInstance.canPlay():
                AIPlay()
            else:
                break

    # End Game
    playAgain = gameEnded()
    sayGoodBye()
    return playAgain


# Repeats forever until player says no for game option.
while playAgain:
    playAgain = game()
