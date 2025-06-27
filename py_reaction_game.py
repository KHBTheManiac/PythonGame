import pygame
import sys
import random
import time
from pathlib import Path

## 인터페이스 구성 ##
width, height = 800, 600
bg_color_wait = (30, 30, 30)
bg_coor_ready = (255, 0, 0)
bg_color_go = (80, 180, 80)
font_name = "Arial"
random_delay_range = (2000, 5000)  # 2초에서 5초 사이의 랜덤 딜레이

pygame.init()
pygame.display.set_caption("Reaction Time Test")
clock = pygame.time.Clock()
screen = pygame.display.set_mode((width, height))
font_large = pygame.font.SysFont(font_name, 48)
font_medium = pygame.font.SysFont(font_name, 36)


## 함수 정의 ##
def draw_centered(text_surf, y):
    """draw a surface centered horizontally at a given y position."""
    rect = text_surf.get_rect(center=(width // 2, y))
    screen.blit(text_surf, rect)
    
state_wait = "WAIT"
state_ready = "READY"
state_go = "GO"
state_result = "RESULT"

state = state_wait
ready_start_time = 0
random_delay = 0
reaction_start_time = 0
reaction_time = 0.0
false_start = False

best_time = None


## 게임 루프 시작 ##
while True:
    dt = clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == state_wait:
                state = state_ready
                ready_start_time = pygame.time.get_ticks()
                random_delay = random.randint(*random_delay_range)
                false_start = False
            elif state == state_ready:
                reaction_time = 0.0
                false_start = True
                state = state_result
            elif state == state_go:
                click_time = pygame.time.get_ticks()
                reaction_time = (click_time - reaction_start_tim) / 1000.0
                
                if (best_time is None or reaction_time < best_time):
                    best_time = reaction_time
                state = state_result
            elif state == state_result:
                state = state_ready
                ready_start_time = pygame.time.get_ticks()
                random_delay = random.randint(*random_delay_range)
                false_start = False
                
                
                
    # 화면 업데이트
    if state == state_ready :
        current_ticks = pygame.time.get_ticks()
        if current_ticks - ready_start_time >= random_delay:
            state = state_go
            reaction_start_tim = pygame.time.get_ticks()
            
    # 렌더링 
    if state == state_wait:
        screen.fill(bg_color_wait)
        draw_centered(font_large.render("Reaction Time Test", True, (255, 255, 255)), height // 2 - 50)
        draw_centered(font_medium.render("Click to Start", True, (255, 255, 255)), height // 2 + 50)
        if best_time is not None:
            draw_centered(font_medium.render(f"Best Time: {best_time:.3f} seconds", True, (150, 200, 150)), height - 50)
            
    elif state == state_ready:
        screen.fill(bg_coor_ready)
        draw_centered(font_large.render("Get Ready...", True, (0, 0, 0)), height // 2)
        
    elif state == state_go:
        screen.fill(bg_color_go)
        draw_centered(font_large.render("CLICK!", True, (20, 20, 20)), height // 2)
        
    elif state == state_result:
        screen.fill(bg_color_wait)
        if false_start :
            draw_centered(font_large.render("TOO SOON!", True, (255, 80, 80)), height // 2 - 30)
        else:
            draw_centered(font_large.render(f"{reaction_time:.3f} seconds", True, (255, 255, 255)), height // 2 - 30)
            if reaction_time == best_time:
                draw_centered(font_medium.render("New Best Time!", True, (255, 215, 0)), height // 2 + 30)
        draw_centered(font_medium.render("Click to Restart", True, (255, 255, 255)), height - 50)
        if best_time is not None:
            draw_centered(font_medium.render(f"Best Time: {best_time:.3f} seconds", True, (150, 200, 150)), height - 100)
            
    pygame.display.flip()