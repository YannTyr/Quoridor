import pygame
import sys
import time
import copy

from quoridor import Quoridor

# Game settings
HEIGHT = 9
WIDTH = 9
PLAYERS_NUMBER = 2
WALLS_NUMBER = 10

# Colors
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GRAY = (80, 80, 80)
LIGHT_GRAY = (180, 180, 180)
WHITE = (255, 255, 255)
GREEN = (25, 180, 25)
RED = (180, 60, 60)

COLOR_BACKGROUND = (13, 2, 2)
COLOR_SQUARES = (18, 15, 15)
COLOR_BORDERS = (50, 50, 50)
COLOR_WALLS = (190, 190, 190)
COLOR_WALLS_A = (255, 255, 255)
COLOR_TEXT = (240, 240, 240)
COLOR_PLAYERS = {
    "1": (230, 220, 130),
    "1a": (250, 250, 160),
    "2": (200, 75, 75),
    "2a": (255, 90, 90)
}

players_names = {
    1: "Theseus",
    2: "Minotaur"
}


def main():

    # Create game
    pygame.init()
    size = width, height = 1200, 700
    # size = width, height = 1920, 1080
    # size = width, height = 1366, 768
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # Fonts
    SERIF = "assets/fonts/EBGaramond-VariableFont_wght.ttf"
    title_font = pygame.font.Font(SERIF, 90)
    subtitle_font = pygame.font.Font(SERIF, 45)
    instruction_font = pygame.font.Font(SERIF, 30)

    # Compute board size
    BOARD_PADDING = 20
    board_height_abt = ((3 / 4) * height) - (BOARD_PADDING * 2)
    board_width_abt = board_height_abt
    cell_size = int(min(board_width_abt / WIDTH, board_height_abt / HEIGHT))
    board_height = cell_size * HEIGHT
    board_width = board_height
    board_origin = ((width / 2 - board_width / 2), (height / 2 - board_height / 2))

    pawn_size = cell_size / 2.1
    #
    # wall_width = cell_size * 2/6 - 2
    # wall_height = cell_size * 10/6

    storage_width = cell_size * 2
    storage_height = board_height / 2
    storage_origin_1 = (board_origin[0] - storage_width - 50, board_origin[1] + cell_size * HEIGHT * 0.5 - cell_size/8)
    storage_origin_2 = (board_origin[0] + cell_size * WIDTH + 50, board_origin[1] + cell_size/8)

    # Create game and AI agent
    game = Quoridor(height=HEIGHT, width=WIDTH, walls_number=WALLS_NUMBER)
    # ai = QuoridorAI()

    # Show instructions initially
    instructions = True

    # Counter of turns
    turn = 0

    pawn_is_active = False
    highlight_pawn = False
    active_wall = None
    game_is_active = True

    while True:

        events = pygame.event.get()
        screen.fill(COLOR_BACKGROUND)

        # Show game instructions
        if instructions:
            # Check if game quit
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()
            # Show instruction
            instructions = draw_instructions(clock, screen, width, height, title_font, subtitle_font, instruction_font)
            continue  # Continue the loop

        if game_is_active:
            active_player = game.player(turn)

        # Draw the board
        cells = []
        for i in range(HEIGHT):
            row = []
            for j in range(WIDTH):
                # Draw rectangle for a cell
                rect = pygame.Rect(
                    board_origin[0] + j * cell_size,
                    board_origin[1] + i * cell_size,
                    cell_size, cell_size
                )
                pygame.draw.rect(screen, COLOR_SQUARES, rect)
                pygame.draw.rect(screen, COLOR_BORDERS, rect, int(cell_size/5))
                pygame.draw.rect(screen, COLOR_BACKGROUND, rect, int(cell_size/6))

                # Draw players' pawns on a board
                player = game.board[i][j]["player"]
                if player != 0:
                    # Do not draw the active pawn, because it will be drawn later as an active pawn (optional)
                    if not pawn_is_active or player != active_player:
                        rect = pygame.Rect(
                            board_origin[0] + j * cell_size + (cell_size - pawn_size) / 2,
                            board_origin[1] + i * cell_size + (cell_size - pawn_size) / 2,
                            pawn_size, pawn_size)
                        pygame.draw.rect(screen, COLOR_PLAYERS[str(player)], rect)

                    game.pawns_loc[player] = (i, j)

                # Show where player can move
                if pawn_is_active and (i, j) in game.available_moves(game.board, active_player, game.pawns_loc):
                    rect = pygame.Rect(
                        board_origin[0] + j * cell_size + (cell_size - pawn_size / 2) / 2,
                        board_origin[1] + i * cell_size + (cell_size - pawn_size / 2) / 2,
                        pawn_size / 2, pawn_size / 2)
                    pygame.draw.rect(screen, COLOR_PLAYERS[str(active_player)], rect)

                row.append(rect)
            cells.append(row)

        
        # Draw places for unused walls
        storage_rect_1 = pygame.Rect(
            storage_origin_1[0], storage_origin_1[1],
            storage_width, storage_height
        )
        pygame.draw.rect(screen, COLOR_SQUARES, storage_rect_1)
        pygame.draw.rect(screen, COLOR_BORDERS, storage_rect_1, int(cell_size * 0.05))

        storage_rect_2 = pygame.Rect(
            storage_origin_2[0], storage_origin_2[1],
            storage_width, storage_height
        )
        pygame.draw.rect(screen, COLOR_SQUARES, storage_rect_2)
        pygame.draw.rect(screen, COLOR_BORDERS, storage_rect_2, int(cell_size * 0.05))

        # Draw walls
        walls_rects = []
        for player in range(1, PLAYERS_NUMBER + 1):
            for wall in game.walls[player]:
                wall_width = cell_size * 2/8
                wall_height = cell_size * 10/6
                if not wall["active"]:
                    color = COLOR_WALLS
                else:
                    color = COLOR_WALLS_A

                # Draw a wall if it is on the board
                if wall["placed"]:
                    if wall["orientation"] == "horizontal":
                        x = board_origin[0] + wall["loc"][1] * cell_size + cell_size * 1/6
                        y = board_origin[1] + wall["loc"][0] * cell_size + cell_size * 5/6 + 1/24 * cell_size
                        wall_width, wall_height = wall_height, wall_width
                    else:
                        x = board_origin[0] + wall["loc"][1] * cell_size + cell_size * 5/6 + 1/24 * cell_size
                        y = board_origin[1] + wall["loc"][0] * cell_size + cell_size * 1/6
                    wall_rect = pygame.Rect(x, y, wall_width, wall_height)
                    pygame.draw.rect(screen, color, wall_rect)

                # Draw a wall if it is unused yet (laying on a "wall storage")
                else:
                    if player == 1:
                        x = storage_origin_1[0] + cell_size / 6
                        # y = storage_origin_2[1] + cell_size / 8 + wall["n"] * (wall_width + cell_size / 8)
                        y = storage_origin_1[1] + board_width / 48 + wall["n"] * (wall_width + board_width / 50)
                    elif player == 2:
                        x = storage_origin_2[0] + cell_size / 6
                        # y = storage_origin_2[1] + cell_size / 8 + wall["n"] * (wall_width + cell_size / 8)
                        y = storage_origin_2[1] + board_width / 48 + wall["n"] * (wall_width + board_width / 50)
                    wall_width, wall_height = wall_height, wall_width
                    wall_rect = pygame.Rect(x, y, wall_width, wall_height)
                    pygame.draw.rect(screen, color, wall_rect)
                walls_rects.append((wall, wall_rect))
                # maybe better version (not ready yet):
                # wall["rect"] = wall_rect



        # # AI Move button?
        # pass
        #
        # # Reset button
        # pass
        #
        # move = None

        for event in events:

            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print("event.pos: ", event.pos)

                    if game_is_active:

                        # Check if the click was on the board
                        up, down = board_origin[1], board_origin[1] + board_height
                        left, right = board_origin[0], board_origin[0] + board_width
                        if up < event.pos[1] < down and left < event.pos[0] < right:

                            # Get a coordinates (i, j) of the clicked cell
                            i = int((event.pos[1] - board_origin[1]) / cell_size)
                            j = int((event.pos[0] - board_origin[0]) / cell_size)
                            print(j, i)

                            # Activate pawn
                            if game.board[i][j]["player"] == active_player:
                                if pawn_is_active:
                                    pawn_is_active = False
                                    highlight_pawn = False
                                else:
                                    highlight_pawn = True
                                    pawn_is_active = True
                                    active_wall = None
                                    for wall in game.walls[active_player]:
                                        wall["active"] = False

                            # Make a move
                            if (i, j) in game.available_moves(game.board, active_player, game.pawns_loc) \
                                    and pawn_is_active:
                                game.board[i][j]["player"] = active_player
                                game.board[game.pawns_loc[active_player][0]][game.pawns_loc[active_player][1]]["player"] = 0
                                game.pawns_loc[active_player] = (i, j)
                                pawn_is_active = False
                                highlight_pawn = False
                                turn += 1

                        # Check if the click was on a wall
                        for wall in walls_rects:
                            if wall[1].collidepoint(event.pos):
                                double_click = False
                                if wall[0]["active"]:
                                    wall[0]["active"] = False
                                    active_wall = None
                                    double_click = True
                                if not wall[0]["placed"] and wall[0]["player"] == active_player:
                                    pawn_is_active = False
                                    highlight_pawn = False
                                    if double_click:
                                        wall[0]["active"] = False
                                        active_wall = None
                                    else:
                                        wall[0]["active"] = True
                                        active_wall = wall[0]
                            else:
                                wall[0]["active"] = False
                                active_wall = None

                        # Placing a wall
                        if active_wall:
                            wall_v_width = cell_size * 2/8
                            wall_v_height = cell_size * 4/6
                            wall_h_width, wall_h_height = wall_v_height, wall_v_width

                            for i in range(HEIGHT):
                                for j in range(WIDTH):
                                    x_v = board_origin[0] + j * cell_size + cell_size * 5/6 + 1/24 * cell_size
                                    y_v = board_origin[1] + i * cell_size + cell_size * 1/6
                                    wall_rect_ver = pygame.Rect(x_v, y_v, wall_v_width, wall_v_height)

                                    x_h = board_origin[0] + j * cell_size + cell_size * 1 / 6
                                    y_h = board_origin[1] + i * cell_size + cell_size * 5 / 6 + 1 / 24 * cell_size
                                    wall_rect_hor = pygame.Rect(x_h, y_h, wall_h_width, wall_h_height)

                                    place_h_wall = wall_rect_hor.collidepoint(event.pos)
                                    place_v_wall = wall_rect_ver.collidepoint(event.pos)
                                    if place_h_wall or place_v_wall:
                                        if i == HEIGHT - 1:
                                            i -= 1
                                        if j == WIDTH - 1:
                                            j -= 1

                                        no_h_barriers = not(
                                            game.board[i][j]["wall_down"] or game.board[i][j + 1]["wall_down"]
                                        )
                                        no_v_barriers = not(
                                                game.board[i][j]["wall_right"] or game.board[i + 1][j]["wall_right"]
                                        )
                                        no_barriers = (place_h_wall and no_h_barriers
                                                       or place_v_wall and no_v_barriers)\
                                                      and not game.board[i][j]["wall_origin"]

                                        if no_barriers:
                                            # Adding a "virtual board" to check
                                            # if pawns still can go to a win side of the board:
                                            virt_board = copy.deepcopy(game.board)
                                            if place_h_wall:
                                                virt_board[i][j]["wall_origin"] = True
                                                virt_board[i][j]["wall_down"] = True
                                                virt_board[i][j + 1]["wall_down"] = True

                                                if game.path_finder(virt_board, 1, game.pawns_loc) \
                                                        and game.path_finder(virt_board, 2, game.pawns_loc):
                                                    active_wall["orientation"] = "horizontal"
                                                    game.board[i][j]["wall_origin"] = True
                                                    game.board[i][j]["wall_down"] = True
                                                    game.board[i][j + 1]["wall_down"] = True

                                                    active_wall["loc"] = (i, j)
                                                    active_wall["placed"] = True
                                                    active_wall["active"] = False
                                                    active_wall = None
                                                    pawn_is_active = False
                                                    highlight_pawn = False
                                                    turn += 1
                                            else:
                                                virt_board[i][j]["wall_origin"] = True
                                                virt_board[i][j]["wall_right"] = True
                                                virt_board[i + 1][j]["wall_right"] = True

                                                if game.path_finder(virt_board, 1, game.pawns_loc) \
                                                        and game.path_finder(virt_board, 2, game.pawns_loc):
                                                    active_wall["orientation"] = "vertical"
                                                    # game.walls["orientation"] = "vertical"
                                                    game.board[i][j]["wall_origin"] = True
                                                    game.board[i][j]["wall_right"] = True
                                                    game.board[i + 1][j]["wall_right"] = True

                                                    active_wall["loc"] = (i, j)
                                                    active_wall["placed"] = True
                                                    active_wall["active"] = False
                                                    active_wall = None
                                                    pawn_is_active = False
                                                    highlight_pawn = False
                                                    turn += 1


            # if event.type == pygame.MOUSEBUTTONUP:


        # Draw activated pawn
        if highlight_pawn:
            rect = pygame.Rect(
                board_origin[0] + game.pawns_loc[active_player][1] * cell_size + (cell_size - pawn_size) / 2,
                board_origin[1] + game.pawns_loc[active_player][0] * cell_size + (cell_size - pawn_size) / 2,
                pawn_size, pawn_size)
            pygame.draw.rect(screen, COLOR_PLAYERS[str(active_player) + "a"], rect, int(pawn_size//4))

        if game_is_active:
            # A text with an active player's name
            player_name = players_names[active_player]
            t_your_move = subtitle_font.render(f"Your move, ", True, COLOR_TEXT)
            t_your_move_rect = t_your_move.get_rect()
            t_your_move_rect.midright = (board_origin[0], height / 12)
            screen.blit(t_your_move, t_your_move_rect)

            t_active_player = subtitle_font.render(player_name, True, COLOR_PLAYERS[str(active_player)])
            t_active_player_rect = t_active_player.get_rect()
            t_active_player_rect.midleft = (t_your_move_rect.right, height / 12)
            screen.blit(t_active_player, t_active_player_rect)

        # Stop the game and show the winner if there is one
        if game.won(active_player, game.pawns_loc):
            # Text with the winner's name
            player_name = players_names[active_player]
            t_you_won = subtitle_font.render(f"You won, ", True, COLOR_TEXT)
            t_you_won_rect = t_you_won.get_rect()
            t_you_won_rect.midright = (board_origin[0], height / 12)
            screen.blit(t_you_won, t_you_won_rect)

            t_active_player = subtitle_font.render(player_name, True, COLOR_PLAYERS[str(active_player)])
            t_active_player_rect = t_active_player.get_rect()
            t_active_player_rect.midleft = (t_you_won_rect.right, height / 12)
            screen.blit(t_active_player, t_active_player_rect)

            game_is_active = False

        pygame.display.flip()
        clock.tick(30)


# def draw_pawn():

def draw_instructions(clock, screen, width, height, title_font, subtitle_font, instruction_font):

    # Check if game quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Title
    title = title_font.render("Quoridor", True, COLOR_TEXT)
    title_rect = title.get_rect()
    title_rect.center = ((width / 2), (height / 10))
    screen.blit(title, title_rect)

    # Rules
    rules = [
        "Go to other side of the board!",
        "Make moves with your pawn and place walls.",
        "You can jump over other pawns but not over walls."
    ]
    for i, rule in enumerate(rules):
        line = instruction_font.render(rule, True, COLOR_TEXT)
        line_rect = line.get_rect()
        line_rect.center = ((width / 2), 200 + 35 * i)
        screen.blit(line, line_rect)

    # Play game button
    #                         left,            top,              width,     height
    button_rect = pygame.Rect((3 / 8) * width, (3 / 4) * height, width / 4, 60)
    button_text = subtitle_font.render("Play", True, COLOR_TEXT)
    button_text_rect = button_text.get_rect()
    button_text_rect.center = button_rect.center
    pygame.draw.rect(screen, COLOR_SQUARES, button_rect)
    screen.blit(button_text, button_text_rect)

    # Check if play button clicked
    click, _, _ = pygame.mouse.get_pressed()
    if click == 1:
        mouse = pygame.mouse.get_pos()
        if button_rect.collidepoint(mouse):
            time.sleep(0.3)
            return False

    pygame.display.flip()
    clock.tick(30)
    return True


if __name__ == '__main__':
    main()
