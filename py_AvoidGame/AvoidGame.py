import pygame
from random import *

pygame.init()

screen_width = 480
screen_height = 640
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Avoid them all!")

clock = pygame.time.Clock()


#########################
# 1. 사용자 게임 초기화 (배경 화면, 게임 이미지, 좌표, 폰트 등)
#########################


background = pygame.image.load("C:/PythonGame/py_AvoidGame/background.png")

character = pygame.image.load("C:/PythonGame/py_AvoidGame/character.png")
character_size = character.get_rect().size
character_width = character_size[0]
character_height = character_size[1]
character_x = (screen_width / 2) - (character_width / 2)
character_y = screen_height - character_height

to_x = 0

enemy = pygame.image.load("C:/PythonGame/py_AvoidGame/enemy.png")
enemy_size = enemy.get_rect().size
enemy_width = enemy_size[0]
enemy_height = enemy_size[1]
enemy_x_pos = randrange(0, screen_width - enemy_width)
enemy_y_pos = 0
enemy_speed = 10

character_speed = 0.6

game_font = pygame.font.Font(None, 40)

total_time = 30

start_ticks = pygame.time.get_ticks()
enemy_count = 10

##########################
# 2. 이벤트 처리 (키보드, 마우스 등)
##########################


running = True
while running:
    dt = clock.tick(30)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                to_x -= character_speed
            elif event.key == pygame.K_RIGHT:
                to_x += character_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                to_x = 0
                
                
    character_x += to_x * dt
    enemy_y_pos += enemy_speed

    #가로 경계값 처리
    if character_x <= 0:
        character_x = 0
    elif character_x >= screen_width - character_width:
        character_x = screen_width - character_width
        
    character_rect = character.get_rect()
    character_rect.left = character_x
    character_rect.top = character_y

    enemy_rect = enemy.get_rect()
    enemy_rect.left = enemy_x_pos
    enemy_rect.top = enemy_y_pos


    if enemy_count > 1:
        if enemy_y_pos >= screen_height:
            enemy_count -= 1
            enemy_x_pos = randrange(0, screen_width - enemy_width)
            enemy_y_pos = 0
            print(enemy_count)
            
    if character_rect.colliderect(enemy_rect):
        print("Game Over!")
        running = False
        
    if enemy_count == 1 and enemy_y_pos == screen_height:
        print("게임 클리어!")
        running = False
        
        
    screen.blit(background, (0, 0))

    screen.blit(character, (character_x, character_y))
    screen.blit(enemy, (enemy_x_pos, enemy_y_pos))


    elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000

    timer = game_font.render(str(int(total_time - elapsed_time)), True, (255, 255, 255))

    screen.blit(timer, (10, 10))

    enemy_count_render = game_font.render("Enemy Count : " + str(int(enemy_count -1)), True, (255, 255, 255))
    screen.blit(enemy_count_render, (screen_width - 300, 10))

    if enemy_count == 1 and enemy_y_pos == screen_height:
        mission_clear_render = game_font.render("Mission Clear!", True, (255, 255, 255))
        mission_clear_size = mission_clear_render.get_rect().size
        mission_clear_width = mission_clear_size[0]
        screen.blit(mission_clear_render, ((screen_width / 2) - (mission_clear_width / 2), screen_height / 2))
    
    pygame.display.update()
    
pygame.time.delay(2000)
pygame.quit()