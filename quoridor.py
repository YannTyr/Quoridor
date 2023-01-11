import random
import itertools

class Quoridor:
    """
    Game representation.
    """

    def __init__(self, height=9, width=9, walls=10, players=2):

        # Set initial size and number of walls
        self.height = height
        self.width = width
        self.walls = walls
        self.players = players

        # Initialize an empty board
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(
                    {"player": 0,
                     "wall_up": False,
                     "wall_down": False,
                     "wall_left": False,
                     "wall_right": False}
                )
            self.board.append(row)

        # Set players on start positions
        self.board[0][self.width//2]["player"] = 1
        self.board[-1][self.width//2]["player"] = 2
        if players == 4:
            self.board[self.height // 2][0]["player"] = 3
            self.board[self.height // 2][-1]["player"] = 4

    def player(self, turn):
        """Returns player who has the next turn on a board."""
        if turn % 2 == 0:
            return 1
        else:
            return 2

    def won(self, player):
        """Check if the player reached the other side of the board."""
        if player in [1, 3]:
            win_side = [-1]  # down for player 1, right for player 3
        else:
            win_side = [0]  # up for player 2, left for player 4

        if player in [1, 2]:
            for j in range(self.width):
                if self.board[win_side][j]["player"] == player:
                    return True
        else:
            for i in range(self.height):
                if self.board[i][win_side]["player"] == player:
                    return True



