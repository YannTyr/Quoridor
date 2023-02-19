import random


class DumbAI:
    """
    A primitive test AI.
    """

    # Init does not work(
    # def __int__(self, width=9, height=9):
    #     print("__int__")
    #     from runner import game
    #     self.distances = [[0 for _ in range(game.WIDTH)] for _ in range(game.HEIGHT)]
    #     print(self.distances)

    def move(self, board, pawns_loc, player):
        """Return object to be moved and its coordinates."""
        from runner import game
        item = "pawn"
        # Get all possible moves and choose which of them that is closer to finish
        available_moves = game.available_moves(board, pawns_loc[player])
        distances = self.map_dist(board, player)
        available_moves.sort(key=lambda cell: distances[cell[0]][cell[1]])
        i, j = available_moves[0]
        return item, i, j

    def map_dist(self, board, player):
        """Mapping distances from every cell to the win side of the board."""
        from runner import game

        # Matrix for distances
        distances = [[None for j in range(game.width)] for i in range(game.height)]

        # Add cells with known distances (first/last row) and add them to the frontier
        if player == 1:
            win_side = 0
        elif player == 2:
            win_side = game.height - 1
        frontier = []
        for j in range(game.width):
            distances[win_side][j] = 0
            frontier.append((win_side, j))

        explored = []
        new_frontier = frontier
        while frontier:
            # print("frontier: ", frontier)
            # print("explored: ", explored)
            frontier = new_frontier
            for cell in frontier.copy():
                i, j = cell[0], cell[1]
                dist = distances[i][j]
                for new_cell in game.available_moves(board, cell, ai=True):
                    if new_cell not in frontier and new_cell not in explored:
                        i, j = new_cell[0], new_cell[1]
                        if dist == None: dist = 0
                        distances[i][j] = dist + 1
                        frontier.append(new_cell)
                        explored.append(new_cell)
                frontier.remove(cell)
                explored.append(cell)
                new_frontier = frontier

        print(*distances, sep="\n", end="\n")
        return distances
