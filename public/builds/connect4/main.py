import asyncio
import random
import pygame

pygame.init()

# --------------------------------------------------
# WINDOW / GAME SETTINGS
# --------------------------------------------------

WIDTH = 600
HEIGHT = 600
HUD_HEIGHT = 60

COLS = 7
ROWS = 6
CELL_SIZE = 76
DISC_RADIUS = 30

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE
BOARD_LEFT = (WIDTH - BOARD_WIDTH) // 2
BOARD_TOP = HEIGHT - BOARD_HEIGHT - 20

# Row above the board where the next disc hovers
PREVIEW_Y = BOARD_TOP - CELL_SIZE // 2 - 2

GRAVITY = 2600          # pixels / second^2 for falling discs
CPU_DELAY = 450         # ms the CPU "thinks" before moving
CPU_DEPTH = 4           # minimax search depth

EMPTY = 0
RED = 1
YELLOW = 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4")

clock = pygame.time.Clock()


# --------------------------------------------------
# FONTS
# --------------------------------------------------

title_font = pygame.font.Font(None, 80)
big_font = pygame.font.Font(None, 64)
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 26)


# --------------------------------------------------
# COLORS
# --------------------------------------------------

BACKGROUND = (20, 20, 20)
HUD_COLOR = (28, 28, 28)
BORDER_COLOR = (65, 65, 65)

BOARD_COLOR = (0, 81, 186)
BOARD_SHADOW = (0, 55, 130)
HOLE_COLOR = (20, 20, 20)

RED_COLOR = (232, 0, 13)
RED_SHADE = (160, 0, 10)
YELLOW_COLOR = (255, 200, 0)
YELLOW_SHADE = (190, 140, 0)

WIN_RING = (240, 240, 240)

TEXT_COLOR = (240, 240, 240)
MUTED_TEXT = (170, 170, 170)

BUTTON_COLOR = (0, 81, 186)
BUTTON_HOVER = (40, 120, 210)
BUTTON_TEXT = (240, 240, 240)

PLAYER_COLORS = {
    RED: (RED_COLOR, RED_SHADE),
    YELLOW: (YELLOW_COLOR, YELLOW_SHADE),
}

PLAYER_NAMES = {
    RED: "Red",
    YELLOW: "Yellow",
}


# --------------------------------------------------
# BUTTONS
# --------------------------------------------------

two_player_button = pygame.Rect(
    WIDTH // 2 - 120,
    HEIGHT // 2 + 10,
    240,
    60
)

cpu_button = pygame.Rect(
    WIDTH // 2 - 120,
    HEIGHT // 2 + 90,
    240,
    60
)


# --------------------------------------------------
# BOARD LOGIC
# --------------------------------------------------

def new_board():
    """Board is a list of rows; row 0 is the TOP row."""

    return [[EMPTY] * COLS for _ in range(ROWS)]


def valid_columns(board):
    return [c for c in range(COLS) if board[0][c] == EMPTY]


def landing_row(board, col):
    """Lowest empty row in a column, or None if the column is full."""

    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            return row

    return None


def find_win(board, player):
    """Return the four winning (row, col) cells, or None."""

    directions = [
        (0, 1),    # horizontal
        (1, 0),    # vertical
        (1, 1),    # diagonal down-right
        (1, -1),   # diagonal down-left
    ]

    for row in range(ROWS):
        for col in range(COLS):

            if board[row][col] != player:
                continue

            for dr, dc in directions:
                cells = [
                    (row + dr * i, col + dc * i)
                    for i in range(4)
                ]

                if all(
                    0 <= r < ROWS
                    and 0 <= c < COLS
                    and board[r][c] == player
                    for r, c in cells
                ):
                    return cells

    return None


def board_full(board):
    return all(cell != EMPTY for cell in board[0])


def other(player):
    return YELLOW if player == RED else RED


# --------------------------------------------------
# CPU OPPONENT (minimax + alpha-beta)
# --------------------------------------------------

# Every possible line of four on the board, precomputed once
WINDOWS = []

for _r in range(ROWS):
    for _c in range(COLS):
        for _dr, _dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
            _cells = [(_r + _dr * i, _c + _dc * i) for i in range(4)]
            if all(0 <= r < ROWS and 0 <= c < COLS for r, c in _cells):
                WINDOWS.append(_cells)

# Center first: center columns are stronger and make pruning faster
SEARCH_ORDER = [3, 2, 4, 1, 5, 0, 6]


def score_position(board, player):
    """Heuristic score of the board from `player`'s point of view."""

    opponent = other(player)
    score = 0

    # Favor the center column
    center = [board[r][COLS // 2] for r in range(ROWS)]
    score += center.count(player) * 3

    for window in WINDOWS:
        values = [board[r][c] for r, c in window]
        mine = values.count(player)
        theirs = values.count(opponent)
        empty = values.count(EMPTY)

        if mine == 3 and empty == 1:
            score += 5
        elif mine == 2 and empty == 2:
            score += 2

        if theirs == 3 and empty == 1:
            score -= 4

    return score


def minimax(board, depth, alpha, beta, maximizing, cpu):
    human = other(cpu)

    if find_win(board, cpu):
        return 100000 + depth, None
    if find_win(board, human):
        return -100000 - depth, None

    columns = [c for c in SEARCH_ORDER if board[0][c] == EMPTY]

    if not columns:
        return 0, None
    if depth == 0:
        return score_position(board, cpu), None

    best_col = columns[0]

    if maximizing:
        best = -float("inf")

        for col in columns:
            row = landing_row(board, col)
            board[row][col] = cpu
            value, _ = minimax(board, depth - 1, alpha, beta, False, cpu)
            board[row][col] = EMPTY

            if value > best:
                best, best_col = value, col
            alpha = max(alpha, best)
            if alpha >= beta:
                break

        return best, best_col

    best = float("inf")

    for col in columns:
        row = landing_row(board, col)
        board[row][col] = human
        value, _ = minimax(board, depth - 1, alpha, beta, True, cpu)
        board[row][col] = EMPTY

        if value < best:
            best, best_col = value, col
        beta = min(beta, best)
        if alpha >= beta:
            break

    return best, best_col


def cpu_move(board, cpu):
    _, col = minimax(
        board,
        CPU_DEPTH,
        -float("inf"),
        float("inf"),
        True,
        cpu
    )

    if col is None:
        col = random.choice(valid_columns(board))

    return col


# --------------------------------------------------
# DRAWING HELPERS
# --------------------------------------------------

def cell_center(row, col):
    x = BOARD_LEFT + col * CELL_SIZE + CELL_SIZE // 2
    y = BOARD_TOP + row * CELL_SIZE + CELL_SIZE // 2
    return x, y


def column_at(x):
    """Board column under an x position, or None."""

    if BOARD_LEFT <= x < BOARD_LEFT + BOARD_WIDTH:
        return (x - BOARD_LEFT) // CELL_SIZE

    return None


def draw_disc(x, y, player, radius=DISC_RADIUS):
    color, shade = PLAYER_COLORS[player]

    pygame.draw.circle(screen, shade, (x, y), radius)
    pygame.draw.circle(screen, color, (x, y), radius - 4)


def draw_button(rect, label):
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = BUTTON_HOVER
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(screen, color, rect, border_radius=8)

    text = font.render(label, True, BUTTON_TEXT)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_centered(text_surface, center):
    screen.blit(text_surface, text_surface.get_rect(center=center))


# --------------------------------------------------
# DRAWING
# --------------------------------------------------

def draw_menu(tally):
    screen.fill(BACKGROUND)

    # Little row of discs as a logo
    for i in range(4):
        player = RED if i % 2 == 0 else YELLOW
        draw_disc(
            WIDTH // 2 - 90 + i * 60,
            HEIGHT // 2 - 190,
            player,
            24
        )

    draw_centered(
        title_font.render("CONNECT 4", True, BOARD_COLOR),
        (WIDTH // 2, HEIGHT // 2 - 115)
    )

    draw_centered(
        small_font.render(
            "Mouse or Arrow Keys / A D, drop with Enter / Space",
            True,
            MUTED_TEXT
        ),
        (WIDTH // 2, HEIGHT // 2 - 60)
    )

    draw_centered(
        small_font.render(
            f"Red {tally[RED]}   -   Draws {tally[EMPTY]}   -   Yellow {tally[YELLOW]}",
            True,
            TEXT_COLOR
        ),
        (WIDTH // 2, HEIGHT // 2 - 25)
    )

    draw_button(two_player_button, "2 PLAYERS")
    draw_button(cpu_button, "VS CPU")

    draw_centered(
        small_font.render("or press 1 / 2", True, MUTED_TEXT),
        (WIDTH // 2, HEIGHT // 2 + 180)
    )

    pygame.display.update()


def draw_hud(turn, vs_cpu, tally):
    pygame.draw.rect(screen, HUD_COLOR, (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(
        screen,
        BORDER_COLOR,
        (0, HUD_HEIGHT),
        (WIDTH, HUD_HEIGHT),
        2
    )

    # Scores on each side
    draw_disc(30, HUD_HEIGHT // 2, RED, 14)
    screen.blit(
        font.render(str(tally[RED]), True, TEXT_COLOR),
        (52, 18)
    )

    draw_disc(WIDTH - 30, HUD_HEIGHT // 2, YELLOW, 14)
    yellow_score = font.render(str(tally[YELLOW]), True, TEXT_COLOR)
    screen.blit(
        yellow_score,
        yellow_score.get_rect(midright=(WIDTH - 52, HUD_HEIGHT // 2))
    )

    # Whose turn
    if turn is not None:
        name = PLAYER_NAMES[turn]

        if vs_cpu:
            name = "Your" if turn == RED else "CPU's"
            label = f"{name} turn"
        else:
            label = f"{name}'s turn"

        draw_centered(
            font.render(label, True, PLAYER_COLORS[turn][0]),
            (WIDTH // 2, HUD_HEIGHT // 2 - 6)
        )

        draw_centered(
            small_font.render("Esc = Menu", True, MUTED_TEXT),
            (WIDTH // 2, HUD_HEIGHT - 10)
        )


def make_board_frame():
    """Blue board surface with transparent holes punched out."""

    frame = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    frame.fill(BOARD_COLOR)

    for row in range(ROWS):
        for col in range(COLS):
            cx = col * CELL_SIZE + CELL_SIZE // 2
            cy = row * CELL_SIZE + CELL_SIZE // 2

            pygame.draw.circle(frame, BOARD_SHADOW, (cx, cy), DISC_RADIUS + 3)
            pygame.draw.circle(frame, (0, 0, 0, 0), (cx, cy), DISC_RADIUS)

    return frame


BOARD_FRAME = make_board_frame()


def draw_board(board, falling=None, win_cells=None):
    # Discs already on the board (drawn first, board frame goes on top)
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != EMPTY:
                x, y = cell_center(row, col)
                draw_disc(x, y, board[row][col])

    # Falling disc sits behind the board frame too
    if falling:
        draw_disc(falling["x"], int(falling["y"]), falling["player"])

    # Board frame goes on top so discs look like they're inside it
    screen.blit(BOARD_FRAME, (BOARD_LEFT, BOARD_TOP))

    pygame.draw.rect(
        screen,
        BOARD_SHADOW,
        (BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT),
        3,
        border_radius=6
    )

    # Highlight the winning four
    if win_cells:
        for row, col in win_cells:
            pygame.draw.circle(
                screen,
                WIN_RING,
                cell_center(row, col),
                DISC_RADIUS - 2,
                4
            )


def draw_play(board, turn, hover_col, falling, vs_cpu, tally):
    screen.fill(BACKGROUND)

    # Empty holes show the dark background through the frame
    pygame.draw.rect(
        screen,
        HOLE_COLOR,
        (BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    )

    draw_board(board, falling)
    draw_hud(turn, vs_cpu, tally)

    human_turn = not (vs_cpu and turn == YELLOW)

    # Preview disc above the selected column
    if falling is None and hover_col is not None:
        x = BOARD_LEFT + hover_col * CELL_SIZE + CELL_SIZE // 2

        if human_turn:
            draw_disc(x, PREVIEW_Y, turn)
        else:
            # CPU "thinking": dimmed disc
            draw_disc(x, PREVIEW_Y, turn, DISC_RADIUS - 8)

    pygame.display.update()


def draw_game_over(board, winner, win_cells, vs_cpu, tally):
    screen.fill(BACKGROUND)

    pygame.draw.rect(
        screen,
        HOLE_COLOR,
        (BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    )

    draw_board(board, None, win_cells)
    draw_hud(None, vs_cpu, tally)

    if winner is None:
        message = "DRAW!"
        color = TEXT_COLOR
    elif vs_cpu:
        message = "YOU WIN!" if winner == RED else "CPU WINS!"
        color = PLAYER_COLORS[winner][0]
    else:
        message = f"{PLAYER_NAMES[winner].upper()} WINS!"
        color = PLAYER_COLORS[winner][0]

    # Result in the HUD, instructions in the strip above the board,
    # so the whole board (and the winning four) stays visible
    draw_centered(
        big_font.render(message, True, color),
        (WIDTH // 2, HUD_HEIGHT // 2 + 2)
    )

    draw_centered(
        font.render("R or click = play again", True, TEXT_COLOR),
        (WIDTH // 2, PREVIEW_Y - 10)
    )

    draw_centered(
        small_font.render("M = menu", True, MUTED_TEXT),
        (WIDTH // 2, PREVIEW_Y + 16)
    )

    pygame.display.update()


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------

async def main():

    board = new_board()
    tally = {RED: 0, YELLOW: 0, EMPTY: 0}   # EMPTY = draws

    state = "menu"
    vs_cpu = False

    starting_player = RED
    turn = RED
    hover_col = COLS // 2

    falling = None          # disc currently animating
    winner = None
    win_cells = None

    cpu_ready_at = 0        # tick when the CPU is allowed to move

    def start_game(starter):
        nonlocal board, turn, hover_col, falling, winner, win_cells
        nonlocal cpu_ready_at, state

        board = new_board()
        turn = starter
        hover_col = COLS // 2
        falling = None
        winner = None
        win_cells = None
        cpu_ready_at = pygame.time.get_ticks() + CPU_DELAY
        state = "playing"

    def try_drop(col):
        """Start a falling disc in `col` if the move is legal."""

        nonlocal falling

        if falling is not None or col is None:
            return

        row = landing_row(board, col)

        if row is None:
            return

        x, target_y = cell_center(row, col)

        falling = {
            "col": col,
            "row": row,
            "player": turn,
            "x": x,
            "y": float(PREVIEW_Y),
            "vy": 0.0,
            "target_y": target_y,
        }

    running = True

    while running:

        # Clamp so a slow frame doesn't teleport the disc
        dt = min(clock.get_time() / 1000, 0.05)

        human_turn = not (vs_cpu and turn == YELLOW)

        # ------------------------------------------
        # INPUT
        # ------------------------------------------

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # MENU
            if state == "menu":

                if event.type == pygame.KEYDOWN:

                    if event.key in (pygame.K_1, pygame.K_KP1):
                        vs_cpu = False
                        start_game(starting_player)

                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        vs_cpu = True
                        start_game(starting_player)

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    if two_player_button.collidepoint(event.pos):
                        vs_cpu = False
                        start_game(starting_player)

                    elif cpu_button.collidepoint(event.pos):
                        vs_cpu = True
                        start_game(starting_player)

            # PLAYING
            elif state == "playing":

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    state = "menu"
                    continue

                if not human_turn or falling is not None:
                    continue

                if event.type == pygame.MOUSEMOTION:
                    col = column_at(event.pos[0])
                    if col is not None:
                        hover_col = col

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    col = column_at(event.pos[0])
                    if col is not None:
                        hover_col = col
                        try_drop(col)

                elif event.type == pygame.KEYDOWN:

                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        hover_col = max(0, hover_col - 1)

                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        hover_col = min(COLS - 1, hover_col + 1)

                    elif event.key in (
                        pygame.K_RETURN,
                        pygame.K_SPACE,
                        pygame.K_DOWN,
                        pygame.K_s
                    ):
                        try_drop(hover_col)

                    elif pygame.K_1 <= event.key <= pygame.K_7:
                        hover_col = event.key - pygame.K_1
                        try_drop(hover_col)

            # GAME OVER
            elif state == "game_over":

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_r:
                        start_game(starting_player)

                    elif event.key in (pygame.K_m, pygame.K_ESCAPE):
                        state = "menu"

                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                ):
                    start_game(starting_player)

        # ------------------------------------------
        # CPU MOVE
        # ------------------------------------------

        if (
            state == "playing"
            and vs_cpu
            and turn == YELLOW
            and falling is None
        ):
            now = pygame.time.get_ticks()

            if now >= cpu_ready_at:
                col = cpu_move(board, YELLOW)
                hover_col = col
                try_drop(col)

        # ------------------------------------------
        # UPDATE FALLING DISC
        # ------------------------------------------

        if state == "playing" and falling is not None:

            falling["vy"] += GRAVITY * dt
            falling["y"] += falling["vy"] * dt

            if falling["y"] >= falling["target_y"]:

                # Disc landed: commit it to the board
                row, col = falling["row"], falling["col"]
                board[row][col] = falling["player"]
                falling = None

                cells = find_win(board, turn)

                if cells:
                    winner = turn
                    win_cells = cells
                    tally[turn] += 1
                    state = "game_over"

                elif board_full(board):
                    winner = None
                    win_cells = None
                    tally[EMPTY] += 1
                    state = "game_over"

                else:
                    turn = other(turn)
                    cpu_ready_at = pygame.time.get_ticks() + CPU_DELAY

                # Alternate who goes first each game
                if state == "game_over":
                    starting_player = other(starting_player)

        # ------------------------------------------
        # DRAW
        # ------------------------------------------

        if state == "menu":

            draw_menu(tally)

        elif state == "playing":

            draw_play(board, turn, hover_col, falling, vs_cpu, tally)

        elif state == "game_over":

            draw_game_over(board, winner, win_cells, vs_cpu, tally)

        clock.tick(60)

        # Required for Pygbag/browser compatibility
        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
