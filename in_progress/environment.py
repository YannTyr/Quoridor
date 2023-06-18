import time
import pygame
import functools
import numpy as np
import gymnasium as gym
from gymnasium.spaces import Discrete, MultiDiscrete, Tuple
from gymnasium import spaces
import pettingzoo
from pettingzoo.utils import agent_selector, wrappers
from quoridor import Quoridor
NUM_ITERS = 1000


def env(render_mode=None, board_size=(9, 9), walls=2, players=2):
    print("'def env' started")
    internal_render_mode = render_mode if render_mode != "ansi" else "human"
    environment = QuoridorEnv(render_mode=internal_render_mode, board_size=board_size, walls=walls, players=players)
    # This wrapper is only for environments which print results to the terminal
    if render_mode == "ansi":
        environment = wrappers.CaptureStdoutWrapper(environment)
    # this wrapper helps error handling for discrete action spaces
    environment = wrappers.AssertOutOfBoundsWrapper(environment)
    # Provides a wide vareity of helpful user errors
    # Strongly recommended
    environment = wrappers.OrderEnforcingWrapper(environment)
    return environment


class QuoridorEnv(pettingzoo.AECEnv):
    print("'class QuoridorEnv' started")
    metadata = {"render_modes": ["human"], "name": "Quoridor_v0", "render_fps": 24}

    def __init__(self, render_mode=None, board_size=(9, 9), walls=12, players=2):
        super().__init__()  # ?
        self.window_size = 700  # The size of the PyGame window
        # self.board_size = board_size

        self.possible_agents = ["player_" + str(r) for r in range(players)]
        self.agent_name_mapping = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )
        self.width, self.height = board_size
        self.walls_number = walls
        self.game = Quoridor(height=self.height, width=self.width, walls_number=walls)

        self.actions_number = 16 + (self.width - 1) * (self.height - 1) * 2
        self._action_spaces = {agent: Discrete(self.actions_number) for agent in self.possible_agents}

        self._describe_action = {
            0: {"item": "pawn", "loc": np.array([0, -1])},  # up
            1: {"item": "pawn", "loc": np.array([0, -2])},  # up-double
            2: {"item": "pawn", "loc": np.array([1, -1])},  # up-right
            3: {"item": "pawn", "loc": np.array([-1, -1])},  # up-left

            4: {"item": "pawn", "loc": np.array([1, 0])},  # right
            5: {"item": "pawn", "loc": np.array([2, 0])},  # right-double
            6: {"item": "pawn", "loc": np.array([1, -1])},  # right-up
            7: {"item": "pawn", "loc": np.array([1, 1])},  # right-down

            8: {"item": "pawn", "loc": np.array([0, 1])},  # down
            9: {"item": "pawn", "loc": np.array([0, 2])},  # down-double
            10: {"item": "pawn", "loc": np.array([1, 1])},  # down-right
            11: {"item": "pawn", "loc": np.array([-1, 1])},  # down-left

            12: {"item": "pawn", "loc": np.array([-1, 0])},  # left
            13: {"item": "pawn", "loc": np.array([-2, 0])},  # left-double
            14: {"item": "pawn", "loc": np.array([-1, -1])},  # left-up
            15: {"item": "pawn", "loc": np.array([-1, 1])},  # left-down
        }
        i = 16
        for item in ["h_wall", "v_wall"]:
            for row in range(self.height - 1):
                for col in range(self.width - 1):
                    self._describe_action[i] = {
                        "item": item,
                        "loc": np.array([col, row])
                    }
                    i += 1

        self.observation_spaces = {
            name: spaces.Dict(
                {
                    # "observation": spaces.Box(
                    #     low=0, high=1, shape=(self.width, self.height, 9), dtype=bool
                    # ),
                    "observation": spaces.Box(
                        low=0, high=walls, shape=(self.width, self.height, 9), dtype=np.int8
                    ),
                    "action_mask": spaces.Box(
                        low=0, high=1, shape=(16 + self.width * self.height,), dtype=np.int8
                    ),
                }
            )
            for name in self.possible_agents
        }

        self.render_mode = render_mode
        self.window = None
        self.clock = None

    def reset(self, seed=None, return_info=False, options=None):
        print("'def reset' started")
        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self.state = {agent: None for agent in self.agents}
        # self.observations = {agent: None for agent in self.agents}
        self.num_moves = 0

        self.locations = {"player_0": np.array([self.width // 2, 0]),
                          "player_1": np.array([self.width // 2, self.height - 1])}
        self.win_side = {"player_0": self.height - 1,
                         "player_1": 0}
        # self._player_1_location = np.array([self.width // 2, 0])
        # self._player_2_location = np.array([self.width // 2, self.height - 1])

        # Observations:
        self.observation = np.zeros((self.width, self.height, 9), dtype="int8")
        # Player_0 and Player_1 locations respectively:
        self.observation[0, 0, self.width // 2] = 1
        self.observation[1, self.height - 1, self.width // 2] = 1
        # Player_0 and Player_1 walls number:
        self.observation[2] = self.observation[3] = np.full((self.width, self.height), self.walls_number)
        # All ones for convolution (?)
        self.observation[4] = np.ones((self.width, self.height))
        # Channels from 5 to 8 are wall neighborhood indication for north, east, south and west directions respectively.
        # print(self.observation)

        self.action_masks = {
            # agent: np.zeros(16, "int8") for agent in self.agents
            agent: np.zeros(self.actions_number, "int8") for agent in self.agents
        }
        self.tmp_illigal = []
        # Allow wall placement
        for agent in self.agents:
            for i in range(16, self.actions_number):
                self.action_masks[agent][i] = 1
        # Allow legal moves
        for i in [8, 4, 12]:  # down, right, left
            self.action_masks["player_0"][i] = 1
        for i in [0, 4, 12]:  # up, right, left
            self.action_masks["player_1"][i] = 1

        self.observations = {
            agent: {"observation": self.observation, "action_mask": self.action_masks[agent]}
            for agent in self.agents
        }
        # print(self.observations)

        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

        # Initialize an empty board
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(
                    {"player": "None",
                     "wall_origin": False,
                     # "wall_up": False,
                     "wall_down": False,
                     # "wall_left": False,
                     "wall_right": False}
                )
            self.board.append(row)

        # Set pawn on start positions
        self.board[-1][self.width//2]["player"] = self.agents[0]
        self.board[0][self.width//2]["player"] = self.agents[1]

        # Set pawn on start positions
        self.board[-1][self.width//2]["player"] = self.agents[0]
        self.board[0][self.width//2]["player"] = self.agents[1]
        self.walls_left = {agent: self.walls_number for agent in self.agents}
        self.walls = {
            agent: [
                {
                    "i": i,
                    "placed": False,
                    "loc": np.array([-1, -1]),
                    "orientation": "h_wall",
                    "active": False,
                    "player": agent,
                    "rect": None
                }
                for i in range(self.walls_number)
            ]
            for agent in self.agents
        }
        print("self.observations[player_0] = ", self.observations["player_0"])
        print("'def reset' ended")
        return self.observations
        # return self.observe("player_0")

    def step(self, action):
        if (
                self.terminations[self.agent_selection]
                or self.truncations[self.agent_selection]
        ):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next live agent
            print("The EndGame")
            self._was_dead_step(action)
            return

        agent = self.agent_selection
        print("agent check_0 = ", agent)

        # the agent which stepped last had its _cumulative_rewards accounted for
        # (because it was returned by last()), so the _cumulative_rewards for this
        # agent should start again at 0
        self._cumulative_rewards[agent] = 0

        # stores action of current agent
        self.state[self.agent_selection] = action

        # Describe action
        item = self._describe_action[action]["item"]
        if item == "pawn":
            direction = self._describe_action[action]["loc"]
            old_j, old_i = self.locations[agent]
            self.locations[agent] = np.array(self.locations[agent] + direction)
            # Update board model
            new_j, new_i = self.locations[agent]
            self.board[new_i][new_j]["player"] = agent
            self.board[old_i][old_j]["player"] = "None"
        elif item == "h_wall" or item == "v_wall":
            if item == "v_wall":
                cell_number = int(action - 16 - (self.actions_number - 16) / 2)
            else:
                cell_number = int(action - 16)
            i, j = cell_number // (self.width - 1), cell_number % (self.width - 1)
            for wall in self.walls[agent]:
                if not wall["placed"]:
                    self.walls_left[agent] -= 1
                    wall["orientation"] = item
                    wall["loc"] = np.array([j, i])
                    wall["placed"] = True
                    self.board[i][j]["wall_origin"] = True
                    if item == "h_wall":
                        self.board[i][j]["wall_down"] = True
                        self.board[i][j+1]["wall_down"] = True
                        # Update action mask
                        for a in self.agents:
                            self.action_masks[a][action] = 0
                            if j != 0:
                                self.action_masks[a][action - 1] = 0
                            if j != self.width-2:
                                self.action_masks[a][action + 1] = 0
                            self.action_masks[a][action + (self.actions_number - 16) // 2] = 0
                    else:
                        self.board[i][j]["wall_right"] = True
                        self.board[i+1][j]["wall_right"] = True
                        # Update action mask
                        for a in self.agents:
                            self.action_masks[a][action] = 0
                            if i != 0:
                                self.action_masks[a][action - (self.width - 1)] = 0
                            if i != self.height-2:
                                self.action_masks[a][action + (self.width - 1)] = 0
                            self.action_masks[a][action - (self.actions_number - 16) // 2] = 0
                    break

        # Action masking
        for a in self.agents:
            j, i = self.locations[a]
            # Check up moves
            self.action_masks[a][0:4] = 0
            if i-1 >= 0 and not self.board[i-1][j]["wall_down"]:
                # up if there is no pawn
                if self.board[i-1][j]["player"] == "None":
                    self.action_masks[a][0] = 1
                else:
                    # double up move if there are no edge or wall
                    if i-2 >= 0 and not self.board[i-2][j]["wall_down"]:
                        self.action_masks[a][1] = 1
                    else:
                        # up-right move if there are no edge or wall
                        if j+1 < self.width and not self.board[i-1][j]["wall_right"]:
                            self.action_masks[a][2] = 1
                        # up-left move if there are no edge or wall
                        if j-1 >= 0 and not self.board[i-1][j-1]["wall_right"]:
                            self.action_masks[a][3] = 1
            # Check right moves
            self.action_masks[a][4:8] = 0
            if j+1 < self.width and not self.board[i][j]["wall_right"]:
                # right if there is no pawn
                if self.board[i][j+1]["player"] == "None":
                    self.action_masks[a][4] = 1
                else:
                    # double right move if there are no edge or wall
                    if j+2 < self.height and not self.board[i][j+1]["wall_right"]:
                        self.action_masks[a][5] = 1
                    else:
                        # right-up move if there are no edge or wall
                        if i-1 >= 0 and not self.board[i-1][j+1]["wall_down"]:
                            self.action_masks[a][6] = 1
                        # right-down move if there are no edge or wall
                        if i+1 < self.height and not self.board[i][j+1]["wall_down"]:
                            self.action_masks[a][7] = 1
            # Check down moves
            self.action_masks[a][8:12] = 0
            if i+1 < self.height and not self.board[i][j]["wall_down"]:
                if self.board[i+1][j]["player"] == "None":
                    self.action_masks[a][8] = 1
                else:
                    if i-2 >= 0 and not self.board[i-2][j]["wall_down"]:
                        self.action_masks[a][9] = 1
                    else:
                        if j+1 < self.width and not self.board[i+1][j]["wall_right"]:
                            self.action_masks[a][10] = 1
                        if j-1 >= 0 and not self.board[i+1][j-1]["wall_right"]:
                            self.action_masks[a][11] = 1
            # Check left moves
            self.action_masks[a][12:16] = 0
            if j-1 >= 0 and not self.board[i][j-1]["wall_right"]:
                if self.board[i][j-1]["player"] == "None":
                    self.action_masks[a][12] = 1
                else:
                    if j-2 >= 0 and not self.board[i][j-2]["wall_right"]:
                        self.action_masks[a][13] = 1
                    else:
                        if i-1 >= 0 and not self.board[i-1][j-1]["wall_down"]:
                            self.action_masks[a][14] = 1
                        if i+1 < self.height and not self.board[i][j-1]["wall_down"]:
                            self.action_masks[a][15] = 1

            # Check legal walls placement
            if self.walls_left[a] == 0:
                self.action_masks[a][16:self.actions_number] = 0
            else:
                for n, virt_action in enumerate(self.action_masks[a][16:]):
                    if virt_action == 1 or n in self.tmp_illigal:
                        virt_board = self.board.copy()
                        if virt_action - 16 >= (self.actions_number - 16) // 2:  # vertical wall
                            virt_cell_number = virt_action - 16 - (self.actions_number - 16) // 2
                            i, j = virt_cell_number // (self.width - 1), virt_cell_number % (self.width - 1)
                            virt_board[i][j]["wall_right"] = True
                            virt_board[i + 1][j]["wall_right"] = True
                        else:  # horizontal wall
                            virt_cell_number = virt_action - 16
                            i, j = virt_cell_number // (self.width - 1), virt_cell_number % (self.width - 1)
                            virt_board[i][j]["wall_down"] = True
                            virt_board[i][j + 1]["wall_down"] = True
                        virt_board[i][j]["wall_origin"] = True
                        paths_is_clear = []
                        for player in self.agents:
                            if self.path_finder(virt_board, player):
                                paths_is_clear.append(True)
                        if paths_is_clear == [True for _ in self.agents]:
                            self.action_masks[a][i] = 1
                            if i in self.tmp_illigal:
                                self.tmp_illigal.remove(i)
                        else:
                            self.action_masks[a][i] = 0
                            self.tmp_illigal.append(i)

        # # collect reward if it is the last agent to act
        # if self._agent_selector.is_last():
        # rewards for all agents are placed in the .rewards dictionary
        # self.rewards[self.agents[0]], self.rewards[self.agents[1]] = REWARD_MAP[
        #     (self.state[self.agents[0]], self.state[self.agents[1]])
        # ]

        # +1 if current agent won and -1 for other agent(s)
        for a in self.agents:
            if np.array_equal(self.locations[a][1], self.win_side[a]):
                for player in self.agents:
                    self.rewards[player] = -1
                self.rewards[a] = 1
                self.terminations[a] = True
                print(self.agents[0], self.rewards[self.agents[0]])
                print(self.agents[1], self.rewards[self.agents[1]])

        self.num_moves += 1
        # The truncations dictionary must be updated for all players.
        self.truncations = {
            a: self.num_moves >= NUM_ITERS for a in self.agents
        }

        # # observe the current state
        # for i in self.agents:
        #     self.observations[i] = self.state[
        #         self.agents[1 - self.agent_name_mapping[i]]
        #     ]

        # Update observations
        agent_number = 0 if agent == "player_0" else 1
        if item == "pawn":
            self.observation[agent_number, old_i, old_j] = 0
            self.observation[agent_number, new_i, new_j] = 1
            # time.sleep(20)
        else:
            self.observation[2 + agent_number] = np.full((self.width, self.height), self.walls_left[agent])
            i, j = cell_number // (self.width - 1), cell_number % (self.width - 1)
            if item == "h_wall":
                self.observation[5, i+1, j] = 1
                self.observation[5, i+1, j+1] = 1
                self.observation[7, i, j] = 1
                self.observation[7, i, j+1] = 1
            else:
                self.observation[6, i, j] = 1
                self.observation[6, i+1, j] = 1
                self.observation[8, i, j+1] = 1
                self.observation[8, i+1, j+1] = 1
        # print(self.observation)
        # print("\n")

        self.observations = {
            "player_0": {
                "observation": self.observation,
                # "action_mask": self.action_mask_player_0,
                "action_mask": self.action_masks["player_0"],
            },
            "player_1": {
                "observation": self.observation,
                # "action_mask": self.action_mask_player_1,
                "action_mask": self.action_masks["player_1"],
            },
        }

        # else:
        #     # necessary so that observe() returns a reasonable observation at all times.
        #     self.state[self.agents[1 - self.agent_name_mapping[agent]]] = None
        #     # no rewards are allocated until both players give an action
        #     self._clear_rewards()

        # selects the next agent.
        self.agent_selection = self._agent_selector.next()
        # Adds .rewards to ._cumulative_rewards
        self._accumulate_rewards()

        if self.render_mode == "human":
            self.render()

    def render(self):
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode."
            )
            return

        # if len(self.agents) == 2:
        #     string = "Current state: Agent1: {} , Agent2: {}".format(
        #         MOVES[self.state[self.agents[0]]], MOVES[self.state[self.agents[1]]]
        #     )
        # else:
        #     string = "Game over"
        # print(string)

        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))
        pix_square_size = (
            self.window_size / self.height
        )  # The size of a single grid square in pixels

        # Draw agents
        pygame.draw.rect(
            canvas,
            (255, 0, 0),
            pygame.Rect(
                pix_square_size * self.locations["player_0"],
                (pix_square_size, pix_square_size),
            ),
        )
        pygame.draw.circle(
            canvas,
            (0, 0, 255),
            (self.locations["player_1"] + 0.5) * pix_square_size,
            pix_square_size / 3,
        )

        # Add gridlines
        for x in range(self.width + 1):
            pygame.draw.line(
                canvas,
                0,
                (0, pix_square_size * x),
                (self.window_size, pix_square_size * x),
                width=12,
            )
        for x in range(self.height + 1):
            pygame.draw.line(
                canvas,
                0,
                (pix_square_size * x, 0),
                (pix_square_size * x, self.window_size),
                width=12,
            )

        # Add walls
        for agent in self.agents:
            for wall in self.walls[agent]:
                if wall["placed"]:
                    x, y = wall["loc"]
                    if wall["orientation"] == "v_wall":
                        pygame.draw.line(
                            canvas,
                            (210, 5, 5),
                            (pix_square_size * (x + 1), pix_square_size * y),
                            (pix_square_size * (x + 1), pix_square_size * (y + 2)),
                            width=12,
                        )
                    else:
                        pygame.draw.line(
                            canvas,
                            (210, 5, 5),
                            (pix_square_size * x, pix_square_size * (y + 1)),
                            (pix_square_size * (x + 2), pix_square_size * (y + 1)),
                            width=12,
                        )

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self._action_spaces[agent]

    def observe(self, agent: str):
        return {"observation": self.observation, "action_mask": self.action_masks[agent]}

    def path_finder(self, virt_board, agent):
        """Return True if path to other side of the board is clear (and victory is available)."""

        def available_cells(virt_board, pawn_loc):
            j, i = pawn_loc
            available_moves = []
            if i - 1 >= 0 and not virt_board[i - 1][j]["wall_down"]:
                available_moves.append(np.array([0, -1]))
            if j + 1 < self.width and not virt_board[i][j]["wall_right"]:
                available_moves.append(np.array([1, 0]))
            if i + 1 < self.height and not virt_board[i][j]["wall_down"]:
                available_moves.append(np.array([0, 1]))
            if j - 1 >= 0 and not virt_board[i][j - 1]["wall_right"]:
                available_moves.append(np.array([-1, 0]))
            available_cells = []
            for move in available_moves:
                available_cells.append(np.array(pawn_loc + move))
            return available_cells

        pawn_loc = self.locations[agent]
        frontier = [cell for cell in available_cells(virt_board, pawn_loc)]
        explored = []
        while True:
            if not frontier:
                return False
            cell = frontier[-1]  # imaginable pawn's location
            if np.array_equal(cell[1], self.win_side[agent]):
                return True
            explored.append(cell)
            frontier = frontier[:-1]
            for new_cell in available_cells(virt_board, cell):
                # if new_cell not in frontier and tuple(new_cell) not in explored:
                if frontier and not np.any(np.all(new_cell == frontier, axis=1)):
                    if not np.any(np.all(new_cell == explored, axis=1)):
                        frontier.append(new_cell)
