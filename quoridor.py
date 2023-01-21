import random
import itertools


class Quoridor:
    """
    Game representation.
    """

    def __init__(self, height=9, width=9, walls_number=10, players_number=2):

        # Set initial size and number of walls
        self.height = height
        self.width = width
        self.walls_number = walls_number
        self.players_number = players_number

        # Initialize an empty board
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(
                    {"player": 0,
                     "wall_origin": False,
                     # "wall_up": False,
                     "wall_down": False,
                     # "wall_left": False,
                     "wall_right": False}
                )
            self.board.append(row)

        # Initialize players' pawns (i, j) = (y, x)
        self.pawns_loc = {1: (self.height - 1, self.width // 2),
                          2: (0, self.width // 2)}

        # Set pawn on start positions
        self.board[-1][self.width//2]["player"] = 1
        self.board[0][self.width//2]["player"] = 2

        # # Double pawns if this game for 4 players
        # if players_number == 4:
        #     self.pawns_locations["3"] = (self.height // 2, 0)
        #     self.pawns_locations["4"] = (self.height // 2, self.width - 1)
        #     self.board[self.height // 2][0]["player"] = 3
        #     self.board[self.height // 2][-1]["player"] = 4

        self.walls = {
            player: [
                {
                    "loc": (None, None),
                    "orientation": "horizontal",
                    "placed": False,
                    "active": False,
                    "player": player,
                    "n": i,
                    "rect": None
                }
                for i in range(0, walls_number)
            ]
            for player in range(1, players_number + 1)
        }

    def player(self, turn):
        """Returns player who has the next turn on a board."""
        if turn % 2 == 0:
            return 1
        else:
            return 2

    def won(self, player, pawns_loc):
        """Check if the player reached the other side of the board."""
        # Define for player a win side of the board
        if player == 1 or player == 4:
            win_side = 0  # up for player 1, left for player 4
        elif player == 2:
            win_side = self.height - 1  # down for player 2
        else:
            win_side = self.width - 1  # right for player 3

        # Check if player is on the other side of the board
        if player == 1 or player == 2:
            if pawns_loc[player][0] == win_side:
                return True
        elif pawns_loc[player][1] == win_side:
            return True
        return False

    def available_moves(self, board, player, loc):
        """Return list with cells where pawn can move."""
        available_moves = []
        print("player: ", player)
        pawn_i = loc[player][0]
        pawn_j = loc[player][1]

        main_moves = [(pawn_i - 1, pawn_j),
                      (pawn_i + 1, pawn_j),
                      (pawn_i, pawn_j - 1),
                      (pawn_i, pawn_j + 1)]

        for move in main_moves:
            i, j = move
            if 0 <= i < self.height and 0 <= j < self.width:

                if board[i][j]["player"] == 0:
                    if not self.is_barrier(board, (pawn_i, pawn_j), (i, j)):
                        available_moves.append((i, j))

                # Add double moves
                else:
                    new_i = i + (i - pawn_i)
                    new_j = j + (j - pawn_j)
                    if 0 <= new_i < self.height and 0 <= new_j < self.width:
                        if not self.is_barrier(board, (pawn_i, pawn_j), (i, j)):

                            if not self.is_barrier(board, (i, j), (new_i, new_j)):
                                if board[new_i][new_j]["player"] == 0:
                                    available_moves.append((new_i, new_j))

                            # Add double side move
                            else:
                                if new_i == i:
                                    for new_i in [i - 1, i + 1]:
                                        if 0 <= new_i < self.height:
                                            if board[new_i][j]["player"] == 0:
                                                if not self.is_barrier(board, (i, j), (new_i, j)):
                                                    available_moves.append((new_i, j))
                                if new_j == j:
                                    for new_j in [j - 1, j + 1]:
                                        if 0 <= new_j < self.width:
                                            if board[i][new_j]["player"] == 0:
                                                if not self.is_barrier(board, (i, j), (i, new_j)):
                                                    available_moves.append((i, new_j))

        print("available_moves: ", available_moves)
        return available_moves

    def is_barrier(self, board, loc_a, loc_b):
        """Check if there is a barrier between two neighboring cells."""
        i, j = loc_a[0], loc_a[1]
        fin_i, fin_j = loc_b[0], loc_b[1]
        d_i, d_j = i - fin_i, j - fin_j
        if d_i == -1:
            if board[i][j]["wall_down"]:
                return True
        elif d_i == 1:
            if board[fin_i][fin_j]["wall_down"]:
                return True
        elif d_j == -1:
            if board[i][j]["wall_right"]:
                return True
        elif d_j == 1:
            if board[fin_i][fin_j]["wall_right"]:
                return True
        return False

    def path_finder(self, virt_board, player, pawns_loc):
        """Return True if path to other side of the board is clear (and victory is available)."""
        frontier = [cell for cell in self.available_moves(virt_board, player, pawns_loc)]
        print("frontier", frontier)
        explored = set()
        while True:
            print("frontier: ", frontier)
            if not frontier:
                print("path is NOT clear")
                return False

            cell = frontier[-1]
            pawn_loc = {player: cell}

            if self.won(player, pawn_loc):
                print("path is clear")
                return True

            explored.add(cell)

            frontier = frontier[:-1]
            for new_cell in self.available_moves(virt_board, player, pawn_loc):
                if new_cell not in frontier and new_cell not in explored:
                    frontier.append(new_cell)


