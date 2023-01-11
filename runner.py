import pygame
import sys
import time

from quoridor import Quoridor

# Game settings
HEIGHT = 9
WIDTH = 9
WALLS = 10

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
COLOR_WALLS = (250, 250, 250)
COLOR_TEXT = (250, 250, 250)
COLOR_PLAYERS = {
    "1": (230, 220, 130),
    "1a": (250, 240, 190),
    "2": (200, 75, 75),
    "2a": (255, 90, 90)
}

def main():

    # Create game
    pygame.init()
    size = width, height = 1200, 700
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()

    # Fonts
    SERIF = "assets/fonts/EBGaramond-VariableFont_wght.ttf"
    title_font = pygame.font.Font(SERIF, 80)
    subtitle_font = pygame.font.Font(SERIF, 40)
    instruction_font = pygame.font.Font(SERIF, 30)

    # Compute board size
    BOARD_PADDING = 20
    # board_width = ((3 / 4) * width) - (BOARD_PADDING * 2)
    board_height = ((3 / 4) * height) - (BOARD_PADDING * 2)
    board_width = board_height
    cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
    # board_origin = (BOARD_PADDING, BOARD_PADDING)
    board_origin = ((width / 2 - board_width / 2), (height / 2 - board_height / 2))
    pawn_size = cell_size / 2

    # Create game and AI agent
    game = Quoridor(height=HEIGHT, width=WIDTH, walls=WALLS)


    # Show instructions initially
    # instructions = True
    instructions = False

    # Counter of moves
    turn = 0

    pawn_active = False
    pawns_locations = {"1": (),
                       "2": (),
                       "3": (),
                       "4": ()}

    while True:

        # Check if game quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(COLOR_BACKGROUND)

        #Show game instructions
        if instructions:

            # Title
            title = title_font.render("Quoridor", True, COLOR_TEXT)
            title_rect = title.get_rect()
            title_rect.center = ((width / 2), (height / 10))
            screen.blit(title, title_rect)

            # Rules
            rules = [
                "",
                ""
            ]
            for i, rule in enumerate(rules):
                line = instruction_font.render(rule, True, COLOR_TEXT)
                line_rect = line.get_rect()
                line_rect.center = ((width / 2), 150 + 30 * i)
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
                    instructions = False
                    time.sleep(0.3)

            pygame.display.flip()
            continue

        # Draw board
        cells = []
        for i in range(HEIGHT):
            row = []
            for j in range(WIDTH):
                # Draw rectangle for cell
                rect = pygame.Rect(
                    board_origin[0] + j * cell_size,
                    board_origin[1] + i * cell_size,
                    cell_size, cell_size
                )
                pygame.draw.rect(screen, COLOR_SQUARES, rect)
                pygame.draw.rect(screen, COLOR_BORDERS, rect, int(cell_size/6))
                pygame.draw.rect(screen, COLOR_BACKGROUND, rect, int(cell_size/8))

                # Draw players' pawns on a board
                player = game.board[i][j]["player"]
                if player != 0:
                    rect = pygame.Rect(
                        board_origin[0] + j * cell_size + pawn_size / 2,
                        board_origin[1] + i * cell_size + pawn_size / 2,
                        pawn_size, pawn_size)
                    pygame.draw.rect(screen, COLOR_PLAYERS[str(player)], rect)

                    pawns_locations[str(player)] = (i, j)

                row.append(rect)
            cells.append(row)

        # AI Move button?
        pass

        # Reset button
        pass

        move = None

        # Check for a right/left click
        left, _, right = pygame.mouse.get_pressed()

        player = game.player(turn)

        if left == 1:
            mouse = pygame.mouse.get_pos()
            for i in range(HEIGHT):
                for j in range(WIDTH):

                    # Highlight selected pawn if it is player's pawn
                    if cells[i][j].collidepoint(mouse) and game.board[i][j]["player"] == player:
                        highlight_pawn = True
                        pawn_active = True
                        rect = pygame.Rect(
                            board_origin[0] + j * cell_size + pawn_size / 2,
                            board_origin[1] + i * cell_size + pawn_size / 2,
                            pawn_size, pawn_size)
                        pygame.draw.rect(screen, COLOR_PLAYERS[str(player) + "a"], rect)

                    elif cells[i][j].collidepoint(mouse) and pawn_active:
                        game.board[i][j]["player"] = player
                        game.board[pawns_locations[str(player)][0]][pawns_locations[str(player)][1]]["player"] = 0
                        pawns_locations[str(player)] = (i, j)
                        pawn_active = False

        # if highlight_pawn:


        # screen.blit(cells, board_origin)

        pygame.display.flip()
        clock.tick(60)


# def draw_pawn():



if __name__ == '__main__':
    main()