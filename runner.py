import pygame
import sys
import time
import copy
import random

from quoridor import Quoridor
import AI

# Game settings
HEIGHT = 9
WIDTH = 9
PLAYERS_NUMBER = 2
WALLS_NUMBER = 12

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
COLOR_WALLS = (200, 200, 200)
COLOR_WALLS_A = (175, 5, 5)
COLOR_TEXT = (240, 240, 240)
COLOR_TEXT_2 = (100, 100, 100)
COLOR_PLAYERS = {
    "1": (205, 195, 120),
    "1a": (230, 220, 10),
    "2": (205, 65, 65),
    "2a": (255, 90, 90)
}

players_names = {
    1: "Theseus",
    2: "Minotaur"
}

# Create game and AI agent
game = Quoridor(height=HEIGHT, width=WIDTH, walls_number=WALLS_NUMBER)
ai = AI.PrimitiveAI()


def main():

    # Create game
    global game
    global ai
    pygame.init()
    size = width, height = 1200, 700
    # size = width, height = 1920, 1080
    # size = width, height = 1366, 768
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # Fonts
    SERIF = "assets/fonts/EBGaramond-VariableFont_wght.ttf"
    font_size = 10
    if width >= 1920: font_size = int(font_size * 1.5)
    title_font = pygame.font.Font(SERIF, font_size * 8)
    subtitle_font = pygame.font.Font(SERIF, font_size * 5)
    instruction_font = pygame.font.Font(SERIF, font_size * 3)

    # Compute board size
    BOARD_PADDING = 20
    board_height_abt = ((3 / 4) * height) - (BOARD_PADDING * 2)
    board_width_abt = board_height_abt
    cell_size = int(min(board_width_abt / WIDTH, board_height_abt / HEIGHT))
    border_width = cell_size / 30
    board_height = cell_size * HEIGHT
    board_width = board_height
    board_origin = ((width / 2 - board_width / 2), (height / 2 - board_height / 2))

    pawn_size = cell_size / 2.1
    #
    wall_width = cell_size * 2/8
    wall_height = cell_size * 10/6

    storage_width = cell_size * 2
    # storage_height = board_height / 2
    storage_height = WALLS_NUMBER * wall_width * 2 + wall_width
    # storage_origin_1 = (board_origin[0] - storage_width - 50, board_origin[1] + cell_size * HEIGHT * 0.5 - cell_size/8)
    storage_origin_1 = (board_origin[0] - storage_width - 50, (board_origin[1] + board_height) - storage_height - cell_size/6)
    storage_origin_2 = (board_origin[0] + cell_size * WIDTH + 50, board_origin[1] + cell_size/6)

    # Show instructions initially
    show_instructions = True

    # Counter of turns
    turn = 0

    pawn_is_active = False
    highlight_pawn = False
    active_wall = None
    game_is_active = True
    repeat_reset = False

    while True:

        events = pygame.event.get()
        screen.fill(COLOR_BACKGROUND)

        # Show game instructions
        if show_instructions:
            # Check if game quit
            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()
            # Show instruction
            show_instructions, ai_on = draw_instructions(clock, screen, width, height, title_font, subtitle_font, instruction_font, font_size, border_width)
            continue  # Continue the loop

        if game_is_active:
            active_player = game.player(turn)
        turn_is_done = False

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
                if pawn_is_active and (i, j) in game.available_moves(game.board, game.pawns_loc[active_player]):
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
                # if not wall["active"]:
                #     color = COLOR_WALLS
                # else:
                #     color = COLOR_WALLS_A

                # Draw a wall if it is on the board
                if wall["placed"]:
                    color = COLOR_WALLS
                    if wall["orientation"] == "horizontal":
                        x = board_origin[0] + wall["loc"][1] * cell_size + cell_size * 1/6
                        y = board_origin[1] + wall["loc"][0] * cell_size + cell_size * 5/6 + 1/30 * cell_size
                        wall_rect = pygame.Rect(x, y, wall_height, wall_width)
                    else:
                        x = board_origin[0] + wall["loc"][1] * cell_size + cell_size * 5/6 + 1/30 * cell_size
                        y = board_origin[1] + wall["loc"][0] * cell_size + cell_size * 1/6
                        wall_rect = pygame.Rect(x, y, wall_width, wall_height)
                    pygame.draw.rect(screen, color, wall_rect)

                else:
                    # Highlight a wall when placing it on the board
                    if wall["active"]:
                        x, y = pygame.mouse.get_pos()
                        if board_origin[0] <= x <= board_origin[0] + board_width \
                                and board_origin[1] <= y <= board_origin[1] + board_height:
                            cell_y = (y - board_origin[1] - 1 / 6 * cell_size) % cell_size
                            cell_x = (x - board_origin[0] - 1 / 6 * cell_size) % cell_size
                            if cell_y <= cell_size * 4 / 6 <= cell_x:
                                orientation = "vertical"
                            elif cell_y >= cell_size * 4 / 6 >= cell_x:
                                orientation = "horizontal"
                            else:
                                orientation = None
                            if orientation is not None:
                                i = int((y - board_origin[1] - 1 / 6 * cell_size) // cell_size)
                                j = int((x - board_origin[0] - 1 / 6 * cell_size) // cell_size)
                                if i == HEIGHT - 1:
                                    i -= 1
                                if j == WIDTH - 1:
                                    j -= 1

                                color = GRAY
                                if orientation == "horizontal":
                                    x = board_origin[0] + j * cell_size + cell_size * 1 / 6
                                    y = board_origin[1] + i * cell_size + cell_size * 5 / 6 + 1 / 30 * cell_size
                                    wall_rect = pygame.Rect(x, y, wall_height, wall_width)
                                else:
                                    x = board_origin[0] + j * cell_size + cell_size * 5 / 6 + 1 / 30 * cell_size
                                    y = board_origin[1] + i * cell_size + cell_size * 1 / 6
                                    wall_rect = pygame.Rect(x, y, wall_width, wall_height)
                                pygame.draw.rect(screen, color, wall_rect)

                    # Draw a wall if it is unused yet (laying on a "wall storage")
                    if not wall["active"]:
                        color = COLOR_PLAYERS[str(player)]
                    else:
                        color = COLOR_PLAYERS[str(player) + "a"]
                    if player == 1:
                        x = storage_origin_1[0] + cell_size / 6
                        # y = storage_origin_2[1] + cell_size / 8 + wall["n"] * (wall_width + cell_size / 8)
                        # y = storage_origin_1[1] + board_width / 48 + wall["n"] * (wall_width + board_width / 50)
                        y = storage_origin_1[1] + wall_width + wall["n"] * wall_width * 2
                    elif player == 2:
                        x = storage_origin_2[0] + cell_size / 6
                        # y = storage_origin_2[1] + cell_size / 8 + wall["n"] * (wall_width + cell_size / 8)
                        # y = storage_origin_2[1] + board_width / 48 + wall["n"] * (wall_width + board_width / 50)
                        y = storage_origin_2[1] + wall_width + wall["n"] * wall_width * 2
                    wall_rect = pygame.Rect(x, y, wall_height, wall_width)
                    pygame.draw.rect(screen, color, wall_rect)
                walls_rects.append((wall, wall_rect))
                # maybe better version (not ready yet):
                # wall["rect"] = wall_rect

        # Draw Reset button
        reset_width = width // 10
        reset_height = height // 20
        reset_button_rect = pygame.Rect(width - reset_width - reset_height, height - 2 * reset_height,
                                        reset_width, reset_height)
        reset_button_border_rect = pygame.Rect(width - reset_width - reset_height - border_width,
                                               height - 2 * reset_height - border_width,
                                               reset_width + 2 * border_width, reset_height + 2 * border_width)
        reset_button_text = instruction_font.render("Reset", True, COLOR_TEXT_2)
        reset_button_text_rect = reset_button_text.get_rect()
        reset_button_text_rect.center = reset_button_rect.center
        pygame.draw.rect(screen, COLOR_BORDERS, reset_button_border_rect)
        pygame.draw.rect(screen, COLOR_SQUARES, reset_button_rect)
        screen.blit(reset_button_text, reset_button_text_rect)

        # Draw active Reset? button
        if repeat_reset:
            pygame.draw.rect(screen, RED, reset_button_rect)
            reset_button_text = instruction_font.render("Reset?", True, COLOR_TEXT)
            screen.blit(reset_button_text, reset_button_text_rect)

        # move = None

        if ai_on and active_player == 2:
        # if active_player:
            if game_is_active:
                item, orientation, i, j = ai.move(game.board, game.pawns_loc, game.walls, active_player)
                if item == "pawn":
                    game.board[i][j]["player"] = active_player
                    game.board[game.pawns_loc[active_player][0]][game.pawns_loc[active_player][1]]["player"] = 0
                    game.pawns_loc[active_player] = (i, j)
                    turn_is_done = True
                elif item == "wall":
                    for wall in game.walls[active_player]:
                        if not wall["placed"]:
                            active_wall = wall
                            if orientation == "horizontal":
                                # active_wall["orientation"] = "horizontal"
                                game.board[i][j]["wall_origin"] = True
                                game.board[i][j]["wall_down"] = True
                                game.board[i][j + 1]["wall_down"] = True
                            else:
                                active_wall["orientation"] = "vertical"
                                game.board[i][j]["wall_origin"] = True
                                game.board[i][j]["wall_right"] = True
                                game.board[i + 1][j]["wall_right"] = True

                            active_wall["loc"] = (i, j)
                            active_wall["placed"] = True
                            active_wall["active"] = False
                            active_wall = None
                            # pawn_is_active = False
                            # highlight_pawn = False
                            turn_is_done = True
                            break

        for event in events:

            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print("event.pos: ", event.pos)

                    # Check if Reset is pressed
                    if reset_button_rect.collidepoint(event.pos):
                        if repeat_reset:
                            print("reset")
                            repeat_reset = False
                            game = Quoridor(height=HEIGHT, width=WIDTH, walls_number=WALLS_NUMBER)
                            ai = AI.PrimitiveAI()
                            game_is_active = True
                        else:
                            repeat_reset = True
                    else:
                        repeat_reset = False

                    if game_is_active:
                        if not ai_on or active_player == 1:

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
                                    # active_wall = None

                            # Placing a wall
                            if active_wall:
                                x, y = event.pos
                                cell_y = (y - board_origin[1] - 1/6 * cell_size) % cell_size
                                cell_x = (x - board_origin[0] - 1/6 * cell_size) % cell_size
                                orientation = None
                                if cell_y <= cell_size * 4/6 <= cell_x:
                                    orientation = "vertical"
                                elif cell_y >= cell_size * 4/6 >= cell_x:
                                    orientation = "horizontal"
                                if orientation is not None:
                                    i = int((y - board_origin[1] - 1 / 6 * cell_size) // cell_size)
                                    j = int((x - board_origin[0] - 1 / 6 * cell_size) // cell_size)
                                    if i == HEIGHT - 1:
                                        i -= 1
                                    if j == WIDTH - 1:
                                        j -= 1
                                    virt_wall = {
                                        "loc": (i, j),
                                        "orientation": orientation
                                    }
                                    if virt_wall in game.available_walls(game.board, game.pawns_loc, active_player):
                                        if orientation == "horizontal":
                                            # active_wall["orientation"] = "horizontal"
                                            game.board[i][j]["wall_origin"] = True
                                            game.board[i][j]["wall_down"] = True
                                            game.board[i][j + 1]["wall_down"] = True
                                        else:
                                            active_wall["orientation"] = "vertical"
                                            game.board[i][j]["wall_origin"] = True
                                            game.board[i][j]["wall_right"] = True
                                            game.board[i + 1][j]["wall_right"] = True

                                        active_wall["loc"] = (i, j)
                                        active_wall["placed"] = True
                                        active_wall["active"] = False
                                        active_wall = None
                                        pawn_is_active = False
                                        highlight_pawn = False
                                        turn_is_done = True

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
                                if (i, j) in game.available_moves(game.board, game.pawns_loc[active_player]) \
                                        and pawn_is_active:
                                    game.board[i][j]["player"] = active_player
                                    game.board[game.pawns_loc[active_player][0]][game.pawns_loc[active_player][1]]["player"] = 0
                                    game.pawns_loc[active_player] = (i, j)
                                    pawn_is_active = False
                                    highlight_pawn = False
                                    turn_is_done = True

                # if event.type == pygame.MOUSEBUTTONUP:

        # Activate a pawn if player has no walls
        if game_is_active and all(wall["placed"] for wall in game.walls[active_player]):
            pawn_is_active = True
            highlight_pawn = True

        # End of the turn
        if turn_is_done:
            turn += 1
            pawn_is_active = False
            highlight_pawn = False
            active_wall = None

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
        clock.tick(24)


# def draw_pawn():

def draw_instructions(clock, screen, width, height, title_font, subtitle_font, instruction_font, font_size, border_width):

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
        line_rect.center = ((width / 2), height / 4 + font_size * 3.5 * i)
        screen.blit(line, line_rect)

    # Play_with_friend game button
    #                         left,            top,              width,     height
    # button_rect = pygame.Rect((3 / 8) * width, (3 / 4) * height, width / 4, height / 10)
    button_rect_0 = pygame.Rect((1 / 8) * width + 50, height / 2 + 50, width / 4 - 50, width / 4 - 50)
    button_border_rect_0 = pygame.Rect((1 / 8) * width - border_width + 50, height / 2 - border_width + 50,
                                     width / 4 + 2 * border_width - 50, width / 4 + 2 * border_width - 50)
    button_text = subtitle_font.render("Play", True, COLOR_TEXT)
    button_text_bottom = instruction_font.render("with friend", True, COLOR_TEXT_2)
    button_text_rect = button_text.get_rect()
    button_text_bottom_rect = button_text_bottom.get_rect()
    button_text_rect.center = button_rect_0.center
    button_text_bottom_rect.midtop = button_text_rect.midbottom
    pygame.draw.rect(screen, COLOR_BORDERS, button_border_rect_0)
    pygame.draw.rect(screen, COLOR_SQUARES, button_rect_0)
    screen.blit(button_text, button_text_rect)
    screen.blit(button_text_bottom, button_text_bottom_rect)

    # Play_with_weak_AI game button
    button_rect_1 = pygame.Rect((3 / 8) * width + 50, height / 2 + 50, width / 4 - 50, width / 4 - 50)
    button_border_rect_1 = pygame.Rect((3 / 8) * width - border_width + 50, height / 2 - border_width + 50,
                                     width / 4 + 2 * border_width - 50, width / 4 + 2 * border_width - 50)
    button_text = subtitle_font.render("Play", True, COLOR_TEXT)
    button_text_bottom = instruction_font.render("with weak AI", True, COLOR_TEXT_2)
    button_text_rect = button_text.get_rect()
    button_text_bottom_rect = button_text_bottom.get_rect()
    button_text_rect.center = button_rect_1.center
    button_text_bottom_rect.midtop = button_text_rect.midbottom
    pygame.draw.rect(screen, COLOR_BORDERS, button_border_rect_1)
    pygame.draw.rect(screen, COLOR_SQUARES, button_rect_1)
    screen.blit(button_text, button_text_rect)
    screen.blit(button_text_bottom, button_text_bottom_rect)

    # Play_with_strong_AI game button
    button_rect_2 = pygame.Rect((5 / 8) * width + 50, height / 2 + 50, width / 4 - 50, width / 4 - 50)
    button_border_rect_2 = pygame.Rect((5 / 8) * width - border_width + 50, height / 2 - border_width + 50,
                                     width / 4 + 2 * border_width - 50, width / 4 + 2 * border_width - 50)
    button_text = subtitle_font.render("Play", True, COLOR_TEXT_2)
    button_text_bottom = instruction_font.render("with strong AI", True, COLOR_TEXT_2)
    button_text_rect = button_text.get_rect()
    button_text_bottom_rect = button_text_bottom.get_rect()
    button_text_rect.center = button_rect_2.center
    button_text_bottom_rect.midtop = button_text_rect.midbottom
    pygame.draw.rect(screen, COLOR_BORDERS, button_border_rect_2)
    pygame.draw.rect(screen, COLOR_SQUARES, button_rect_2)
    screen.blit(button_text, button_text_rect)
    screen.blit(button_text_bottom, button_text_bottom_rect)

    # Check if play buttons clicked
    click, _, _ = pygame.mouse.get_pressed()
    if click == 1:
        mouse = pygame.mouse.get_pos()
        if button_rect_0.collidepoint(mouse):
            time.sleep(0.3)
            # ai_on = False
            return False, False
        elif button_rect_1.collidepoint(mouse):
            time.sleep(0.3)
            # ai_on = True
            return False, True

    pygame.display.flip()
    clock.tick(30)
    return True, None


if __name__ == '__main__':
    main()
