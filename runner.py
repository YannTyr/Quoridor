import pygame
import sys
import time

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
COLOR_SQUARES = (16, 16, 16)
COLOR_BORDERS = (50, 50, 50)
COLOR_WALLS = (200, 200, 200)
COLOR_WALLS_A = (240, 240, 240)
COLOR_TEXT = (250, 250, 250)
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

walls = {
    player: [
        # [None, None, False] for _ in range(WALLS_NUMBER)
        {"loc": (None, None),
        "orientation": "horizontal",
        "placed": False}
    ]
    for player in range(1, PLAYERS_NUMBER + 1)
}
walls[1][0] = {"loc": (0, 7), "orientation": "horizontal", "placed": True}
print(walls)


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
    title_font = pygame.font.Font(SERIF, 80)
    subtitle_font = pygame.font.Font(SERIF, 40)
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

    wall_width = cell_size * 2/6 - 2
    wall_height = cell_size * 10/6

    storage_width = board_width / 4 + 10
    storage_height = board_height / 2
    storage_origin_1 = (board_origin[0] - storage_width - 50, board_origin[1] + cell_size * HEIGHT * 0.5 - cell_size/8)
    storage_origin_2 = (board_origin[0] + cell_size * WIDTH + 50, board_origin[1] + cell_size/8)

    # Create game and AI agent
    game = Quoridor(height=HEIGHT, width=WIDTH, walls=WALLS_NUMBER)
    # ai =

    # Show instructions initially
    instructions = True
    # instructions = False

    # Counter of turns
    turn = 0

    pawn_active = False
    highlight_pawn = False
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
                    if not pawn_active or player != active_player:
                        rect = pygame.Rect(
                            board_origin[0] + j * cell_size + (cell_size - pawn_size) / 2,
                            board_origin[1] + i * cell_size + (cell_size - pawn_size) / 2,
                            pawn_size, pawn_size)
                        pygame.draw.rect(screen, COLOR_PLAYERS[str(player)], rect)

                    game.pawns_locations[str(player)] = (i, j)

                # Show where player can move
                if pawn_active and (i, j) in game.available_moves(active_player):
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
        for player in range(1, PLAYERS_NUMBER + 1):
            for wall in walls[player]:

                # Draw a wall if it is on the board
                if wall["placed"]:
                    x = board_origin[0] + wall["loc"][1] * cell_size + cell_size * 5/6 + 1
                    y = board_origin[1] + wall["loc"][0] * cell_size + cell_size * 1/6
                    if wall["orientation"] == "vertical":
                        x, y = y, x
                        wall_width, wall_height = wall_height, wall_width
                    rect = pygame.Rect(x, y, wall_width, wall_height)
                    pygame.draw.rect(screen, COLOR_WALLS, rect)

                # Draw a wall if it is unused
                else:
                    if player == 1:
                        pass
                    elif player == 2:
                        pass

        # rect = pygame.Rect(
        #     board_origin[0] + 7 * cell_size + cell_size * 5/6 + 2,
        #     board_origin[1] + 5 * cell_size + cell_size * 1/6,
        #     cell_size * 2/6 - 2, cell_size * 10/6
        # )
        # pygame.draw.rect(screen, COLOR_WALLS, rect)

        # AI Move button?
        pass

        # Reset button
        pass

        move = None


        for event in events:
            # print(event)

            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    print("event.pos: ", event.pos)

                    # Check if the click was on the board
                    up, down = board_origin[1], board_origin[1] + board_height - 9  # -9px because of rounding
                    left, right = board_origin[0], board_origin[0] + board_width - 9
                    if up < event.pos[1] < down and left < event.pos[0] < right:

                        # Get a coordinates (i, j) of the clicked cell
                        i = int((event.pos[1] - board_origin[1]) / cell_size)
                        j = int((event.pos[0] - board_origin[0]) / cell_size)
                        print(j, i)

                        # Activate pawn
                        if game.board[i][j]["player"] == active_player:
                            if pawn_active:
                                pawn_active = False
                                highlight_pawn = False
                            else:
                                highlight_pawn = True
                                pawn_active = True

                        # Make a move
                        if (i, j) in game.available_moves(active_player) and pawn_active:
                            game.board[i][j]["player"] = active_player
                            player = str(active_player)
                            game.board[game.pawns_locations[player][0]][game.pawns_locations[player][1]]["player"] = 0
                            game.pawns_locations[str(active_player)] = (i, j)
                            pawn_active = False
                            highlight_pawn = False
                            turn += 1

            # if event.type == pygame.MOUSEBUTTONUP:


        # Draw activated pawn
        if highlight_pawn:
            rect = pygame.Rect(
                board_origin[0] + game.pawns_locations[str(active_player)][1] * cell_size + (cell_size - pawn_size) / 2,
                board_origin[1] + game.pawns_locations[str(active_player)][0] * cell_size + (cell_size - pawn_size) / 2,
                pawn_size, pawn_size)
            pygame.draw.rect(screen, COLOR_PLAYERS[str(active_player) + "a"], rect, int(pawn_size//4))

        if game_is_active:
            # Text with an active player's name
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
        if game.won(active_player):
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
