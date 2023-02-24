import copy
import random


class TestAI:
    """
    A primitive test AI.
    Looks for an optimal move in terms of the shortest distance for self.
    Can not use walls.
    """

    # Init does not work(
    # def __int__(self, width=9, height=9):
    #     print("__int__")
    #     from runner import game
    #     self.distances = [[0 for _ in range(game.WIDTH)] for _ in range(game.HEIGHT)]
    #     print(self.distances)

    def move(self, board, pawns_loc, walls, player):
        """Return object to be moved and its coordinates."""
        from runner import game
        item = "pawn"
        # Get all possible moves and choose which of them that is closer to finish
        available_moves = game.available_moves(board, pawns_loc[player])
        distances = self.map_dist(board, player)
        available_moves.sort(key=lambda cell: distances[cell[0]][cell[1]])
        i, j = available_moves[0]
        return item, None, i, j

    def map_dist(self, board, player):
        """Mapping distances from every cell to the win side of the board."""
        from runner import game

        # Matrix for distances
        max_value = game.width * game.height
        distances = [[max_value for j in range(game.width)] for i in range(game.height)]

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
                        distances[i][j] = dist + 1
                        frontier.append(new_cell)
                        explored.append(new_cell)
                frontier.remove(cell)
                explored.append(cell)
                new_frontier = frontier

        # print(*distances, sep="\n", end="\n")
        # print(type(distances[4][4]))
        return distances


class PrimitiveAI(TestAI):
    """
    Looks for an optimal move in terms of the shortest distance (to the finish line)
    with respect to opponent's shortest distance.
    Can use walls.
    """
    def move(self, board, pawns_loc, walls, player):
        """Return object to be moved and its coordinates."""
        print(*board, sep="\n")
        from runner import game
        if player == 1:
            opponent = 2
        else:
            opponent = 1
        self_i, self_j = pawns_loc[player]
        oppo_i, oppo_j = pawns_loc[opponent]
        rated_moves = []
        available_moves = game.available_moves(board, pawns_loc[player])
        self_distances = self.map_dist(board, player)
        oppo_distances = self.map_dist(board, opponent)

        available_moves.sort(key=lambda cell: self_distances[cell[0]][cell[1]])
        i, j = available_moves[0]
        delta = self_distances[i][j] - oppo_distances[oppo_i][oppo_j]
        best_pawn_move = ("pawn", (i, j), None, delta)
        rated_moves.append(best_pawn_move)

        if not all(wall["placed"] for wall in walls[player]):
            available_walls = game.available_walls(board, pawns_loc, player)
            for wall in available_walls:
                i, j = wall["loc"]
                orientation = wall["orientation"]
                state = copy.deepcopy(board)
                state[i][j]["wall_origin"] = True
                state[i][j]["orientation"] = orientation
                if orientation == "horizontal":
                    state[i][j]["wall_down"] = True
                    state[i][j + 1]["wall_down"] = True
                else:
                    state[i][j]["wall_right"] = True
                    state[i + 1][j]["wall_right"] = True
                self_dist = self.map_dist(state, player)
                opp_dist = self.map_dist(state, opponent)
                delta = self_dist[self_i][self_j] - opp_dist[oppo_i][oppo_j]
                rated_moves.append(("wall", (i, j), orientation, delta))

        # rated_moves.sort(key=lambda item_loc_rate: item_loc_rate[2])
        best_move = sorted(rated_moves, key=lambda item_loc_rate: item_loc_rate[-1])[0]
        item = best_move[0]
        i, j = best_move[1]
        orientation = best_move[2]

        print(*self.map_dist(board, player), sep="\n", end="\n")

        return item, orientation, i, j
