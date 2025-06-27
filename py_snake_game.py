import pygame
import sys
import random

# ──────────────────────────────────────────────────────────────────────────────
# Configuration constants
# ──────────────────────────────────────────────────────────────────────────────
CELL_SIZE     = 20         # pixel size of each grid cell
GRID_WIDTH    = 30         # number of cells horizontally
GRID_HEIGHT   = 30         # number of cells vertically
SCREEN_WIDTH  = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS_BASE      = 10         # initial frames per second (game speed)

# Colors (R, G, B)
COLOR_BG         = (30, 30, 30)        # background
COLOR_GRID       = (40, 40, 40)
COLOR_SNAKE_HEAD = (0, 255, 0)
COLOR_SNAKE_BODY = (0, 180, 0)
COLOR_FOOD       = (220, 20, 60)
COLOR_TEXT       = (250, 250, 250)

# ──────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────────────────────

def draw_grid(surface: pygame.Surface) -> None:
    """Draw faint grid lines for visual reference."""
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))


def random_food_position(snake: list[tuple[int, int]]) -> tuple[int, int]:
    """Return a random grid position not currently occupied by the snake."""
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in snake:
            return pos


def draw_text(surface: pygame.Surface, text: str, size: int, center: tuple[int, int]):
    font = pygame.font.SysFont("consolas", size, bold=True)
    text_surface = font.render(text, True, COLOR_TEXT)
    text_rect = text_surface.get_rect(center=center)
    surface.blit(text_surface, text_rect)

# ──────────────────────────────────────────────────────────────────────────────
# Main game function
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game (Pygame)")
    clock = pygame.time.Clock()

    # Initial snake and food setup
    snake: list[tuple[int, int]] = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
    direction: tuple[int, int] = (0, -1)  # moving up initially
    food: tuple[int, int] = random_food_position(snake)
    score: int = 0
    speed: int = FPS_BASE

    running = True
    while running:
        clock.tick(speed)

        # ───── Event handling ─────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                    direction = (0, -1)
                elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                    direction = (0, 1)
                elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                    direction = (-1, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                    direction = (1, 0)
                elif event.key == pygame.K_r:  # restart on‑the‑fly
                    return main()

        # ───── Update snake position ─────
        head_x, head_y = snake[0]
        new_head = ((head_x + direction[0]) % GRID_WIDTH,
                    (head_y + direction[1]) % GRID_HEIGHT)

        # Collision with self → game over
        if new_head in snake:
            break

        snake.insert(0, new_head)

        # Check for food consumption
        if new_head == food:
            score += 1
            speed = FPS_BASE + score // 5  # speed up every 5 points
            food = random_food_position(snake)
        else:
            snake.pop()  # remove tail segment when no food eaten

        # ───── Drawing section ─────
        screen.fill(COLOR_BG)
        draw_grid(screen)

        # Draw food
        pygame.draw.rect(
            screen,
            COLOR_FOOD,
            pygame.Rect(food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE),
        )

        # Draw snake segments
        for i, (x, y) in enumerate(snake):
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE).inflate(-2, -2),
            )

        # Draw score
        draw_text(screen, f"Score: {score}", 24, (80, 20))

        pygame.display.flip()

    # ──────────────────────────────────
    # Game‑over screen
    # ──────────────────────────────────
    while True:
        screen.fill(COLOR_BG)
        draw_text(screen, "GAME OVER", 48, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        draw_text(screen, f"Final Score: {score}", 32, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        draw_text(screen, "Press R to Restart or Q to Quit", 24, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return main()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main()