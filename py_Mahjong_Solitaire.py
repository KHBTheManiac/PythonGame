"""
Minimal Sichuan (Shisen-Sho) Tile-matching Puzzle – Pygame
=========================================================
A single-file prototype (~300 lines) illustrating the core mechanics:
  • Variable-sized board (even number of inner cells)
  • Tiles appear in pairs; shuffle until solvable
  • Player removes two identical tiles if a path with ≤2 right-angle turns exists
  • Hint (H) shows first removable pair; Shuffle (S) shuffles remaining tiles
  • Victory screen when board clears; Esc quits at any time

Controls
---------
Mouse   : click two tiles to try removing them
H key   : show a hint (flashes a removable pair)
S key   : shuffle the remaining tiles
Esc key : quit game

Notes
-----
• Board uses a 1-cell empty border to simplify wrap-around-free pathfinding.
• Path-finding is done by a BFS variant that tracks direction changes (≤2).
• For brevity, there is no fancy animation; logic focuses on gameplay.
• Assets: generated colored rectangles; replace with images easily by blitting.

Author  : ChatGPT (OpenAI) – 2025-06-26
License : MIT
"""

import sys
import random
import pygame
from collections import deque
from typing import List, Optional, Tuple

# ───────────────────────────────── Configuration ─────────────────────────────
CELL        = 48             # pixel size of a board cell
INNER_W     = 14             # inner grid width (even)
INNER_H     = 10             # inner grid height (even)
BORDER      = 1              # border thickness (empty cells)
GRID_W      = INNER_W + BORDER * 2
GRID_H      = INNER_H + BORDER * 2
SCREEN_W    = GRID_W * CELL
SCREEN_H    = GRID_H * CELL
FPS         = 60
TILE_PAIRS  = (INNER_W * INNER_H) // 2
TILE_KINDS  = 20             # distinct tile images (will wrap around)

# Colors
BG_COLOR      = (25, 25, 25)
BORDER_COLOR  = (45, 45, 45)
SELECT_COLOR  = (250, 250, 0)
HINT_COLOR    = (0, 200, 255)
TEXT_COLOR    = (240, 240, 240)
TILE_COLORS = [
    (255, 0, 0),      # red
    (0, 255, 0),      # green
    (0, 0, 255),      # blue
    (255, 255, 0),    # yellow
    (255, 0, 255),    # magenta
    (0, 255, 255),    # cyan
    (255, 165, 0),    # orange
    (128, 0, 128),    # purple
    (0, 128, 0),      # dark green
    (0, 0, 128),      # navy
    (128, 128, 0),    # olive
    (139, 69, 19),    # brown
    (255, 105, 180),  # hot pink
    (105, 105, 105),  # dim gray
    (0, 139, 139),    # dark cyan
    (220, 20, 60),    # crimson
    (0, 100, 0),      # dark green
    (255, 20, 147),   # deep pink
    (25, 25, 112),    # midnight blue
    (255, 215, 0)     # gold
]
    
Vec = Tuple[int, int]
Board = List[List[Optional[int]]]

# ────────────────────────────── Board Utilities ──────────────────────────────

def generate_board() -> Board:
    """Create a shuffled board that is guaranteed to have at least one move."""
    ids = [i % TILE_KINDS for i in range(TILE_PAIRS * 2)]
    while True:
        random.shuffle(ids)
        # Place into inner area; border is None
        board: Board = [[None for _ in range(GRID_W)] for _ in range(GRID_H)]
        idx = 0
        for y in range(BORDER, BORDER + INNER_H):
            for x in range(BORDER, BORDER + INNER_W):
                board[y][x] = ids[idx]
                idx += 1
        if find_first_pair(board):
            return board  # solvable at start


def tiles_remaining(board: Board) -> bool:
    return any(board[y][x] is not None for y in range(BORDER, BORDER+INNER_H) for x in range(BORDER, BORDER+INNER_W))

# ───────────────────────── Path-finding (≤2 turns)  ──────────────────────────
DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # U R D L

def in_bounds(x: int, y: int) -> bool:
    return 0 <= x < GRID_W and 0 <= y < GRID_H


def path_exists(board: Board, a: Vec, b: Vec) -> bool:
    """Return True if a path with ≤2 turns connects a→b through empty cells."""
    if a == b:
        return False
    ax, ay = a
    bx, by = b
    if board[ay][ax] != board[by][bx]:
        return False

    visited = [[[3] * 4 for _ in range(GRID_W)] for _ in range(GRID_H)]
    q = deque()

    # Seed queue with four directions from a (if empty/target)
    for d, (dx, dy) in enumerate(DIRS):
        nx, ny = ax + dx, ay + dy
        if not in_bounds(nx, ny):
            continue
        if board[ny][nx] is None or (nx, ny) == b:
            visited[ny][nx][d] = 0
            q.append((nx, ny, d, 0))  # x, y, dir, turns

    while q:
        x, y, d, turns = q.popleft()
        if turns > 2:
            continue
        if (x, y) == b:
            return True
        dx, dy = DIRS[d]
        nx, ny = x + dx, y + dy
        # Continue straight
        if in_bounds(nx, ny) and (board[ny][nx] is None or (nx, ny) == b):
            if turns < visited[ny][nx][d]:
                visited[ny][nx][d] = turns
                q.appendleft((nx, ny, d, turns))  # straight paths prioritized
        # Turn left/right
        for nd, (tx, ty) in enumerate(DIRS):
            if nd == d or nd == (d + 2) % 4:  # skip same & opposite
                continue
            nx, ny = x + tx, y + ty
            if not in_bounds(nx, ny):
                continue
            if board[ny][nx] is None or (nx, ny) == b:
                nt = turns + 1
                if nt <= 2 and nt < visited[ny][nx][nd]:
                    visited[ny][nx][nd] = nt
                    q.append((nx, ny, nd, nt))
    return False

# ─────────────────────────────── Solver Utils ────────────────────────────────

def find_first_pair(board: Board) -> Optional[Tuple[Vec, Vec]]:
    """Return first removable pair coordinates or None."""
    for y1 in range(BORDER, BORDER + INNER_H):
        for x1 in range(BORDER, BORDER + INNER_W):
            tile = board[y1][x1]
            if tile is None:
                continue
            for y2 in range(y1, BORDER + INNER_H):
                x_start = x1 + 1 if y2 == y1 else BORDER
                for x2 in range(x_start, BORDER + INNER_W):
                    if board[y2][x2] != tile:
                        continue
                    if path_exists(board, (x1, y1), (x2, y2)):
                        return (x1, y1), (x2, y2)
    return None

# ───────────────────────────── Drawing Routines ──────────────────────────────

def draw_board(screen: pygame.Surface, board: Board, sel: Optional[Vec], hint: Optional[Tuple[Vec, Vec]]):
    screen.fill(BG_COLOR)
    # Grid & tiles
    for y in range(GRID_H):
        for x in range(GRID_W):
            rect = pygame.Rect(x * CELL, y * CELL, CELL, CELL)
            # Border shading
            if x < BORDER or x >= GRID_W-BORDER or y < BORDER or y >= GRID_H-BORDER:
                pygame.draw.rect(screen, BORDER_COLOR, rect)
            # Tile
            tile = board[y][x]
            if tile is not None:
                color = TILE_COLORS[tile]
                pygame.draw.rect(screen, color, rect.inflate(-4, -4), border_radius=6)
    # Selection highlight
    if sel:
        x, y = sel
        pygame.draw.rect(screen, SELECT_COLOR, (x*CELL+2, y*CELL+2, CELL-4, CELL-4), 3, border_radius=6)
    # Hint highlight pair
    if hint:
        for (hx, hy) in hint:
            pygame.draw.rect(screen, HINT_COLOR, (hx*CELL+6, hy*CELL+6, CELL-12, CELL-12), 3, border_radius=6)

# ────────────────────────────────── Main Game ────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Sichuan Puzzle – Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 28, bold=True)

    board = generate_board()
    selection: Optional[Vec] = None
    hint_pair: Optional[Tuple[Vec, Vec]] = None
    hint_timer = 0

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_h:
                    hint_pair = find_first_pair(board)
                    hint_timer = 1000  # 1-second flash
                elif event.key == pygame.K_s:
                    board = shuffle_board(board)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                x, y = mx // CELL, my // CELL
                if not in_bounds(x, y):
                    continue
                if board[y][x] is None:
                    continue
                if selection is None:
                    selection = (x, y)
                else:
                    if (x, y) == selection:
                        selection = None
                    elif board[y][x] == board[selection[1]][selection[0]] and path_exists(board, selection, (x, y)):
                        # Remove tiles
                        board[y][x] = None
                        board[selection[1]][selection[0]] = None
                        selection = None
                        if not tiles_remaining(board):
                            victory(screen, font)
                            board = generate_board()
                    else:
                        selection = (x, y)

        # Update hint timer
        if hint_timer > 0:
            hint_timer -= dt
            if hint_timer <= 0:
                hint_pair = None

        draw_board(screen, board, selection, hint_pair)
        # HUD text
        remain = sum(1 for row in board for t in row if t is not None)
        txt = font.render(f"Tiles left: {remain//2}", True, TEXT_COLOR)
        screen.blit(txt, (8, 8))
        pygame.display.flip()


def shuffle_board(board: Board) -> Board:
    """Shuffle remaining tiles in-place until a move exists or no tiles left."""
    tiles = [t for row in board for t in row if t is not None]
    if not tiles:
        return board
    while True:
        random.shuffle(tiles)
        idx = 0
        for y in range(BORDER, BORDER+INNER_H):
            for x in range(BORDER, BORDER+INNER_W):
                if board[y][x] is not None:
                    board[y][x] = tiles[idx]
                    idx += 1
        if find_first_pair(board):
            return board


def victory(screen: pygame.Surface, font: pygame.font.Font):
    msg = font.render("🎉  CLEAR!  Press any key…", True, TEXT_COLOR)
    rect = msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
    screen.blit(msg, rect)
    pygame.display.flip()
    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.QUIT):
                wait = False
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        pygame.time.delay(10)


if __name__ == "__main__":
    main()
