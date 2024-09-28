
import pygame, sys
from pygame.locals import *
import button
import ui.ui as UI

WHITE =(255, 255, 255)
GREEN =(0, 255, 0)
BLUE = (0, 0, 128)
pygame.init()   
screen = pygame.display.set_mode ((800, 800)) 
catImg = pygame.image.load("assets/cat.png")
volume_slider = UI.volume_slider
pygame.mixer.music.load("assets/background_music.mp3")
pygame.mixer.music.set_volume(0.3)
catx = 100
caty = 100
x = 5
y = 5
fps_clock = pygame.time.Clock()
fps = 15
game_state = "start"
pygame.mixer.music.play()
while True: # main game loop DISPLAYSURF.fill(WHITE)
    screen.fill(BLUE)
    if game_state != "pause" and game_state != "game over":
        if game_state == "start" and button.start_button.draw(screen):
            game_state = "ingame"
        if game_state == "ingame" and button.pause_button.draw(screen):
            game_state = "pause"
            pygame.mixer.music.pause()
            continue
        if button.exit_button.draw(screen):
            pygame.quit()
            sys.exit()
        if game_state == "ingame":
            screen.fill(BLUE)
            button.pause_button.draw(screen)
            if catx >= 500:
                x = -5
                y = -5  
            elif catx <= 100:
                x = 5
                y = 5
            catx += x
            caty += y
            screen.blit(catImg, (catx, caty))
            if catx == 500:
                game_state = "game over"
    elif game_state == "pause":
        if button.resume_button.draw(screen):
            game_state = "ingame"
            pygame.mixer.music.unpause()
        if button.main_menu_button.draw(screen):
            game_state = "start"
            pygame.mixer.music.unpause()
            catx = 100
            caty = 100
            x = 5
            y = 5
    else:
        if button.retry_button.draw(screen):
            game_state = "ingame"
            pygame.mixer.music.unpause()
            catx = 100
            caty = 100
            x = 5
            y = 5
        if button.to_main_menu_button.draw(screen):
            game_state = "start"
    if game_state == "start" or game_state == "pause":
            volume_slider.render(screen)
            mouse_pos = pygame.mouse.get_pos()
            mouse_state = pygame.mouse.get_pressed()
            if volume_slider.container_rect.collidepoint(mouse_pos):
                if mouse_state[0]:
                    volume_slider.grabbed = True
            if not mouse_state[0]:
                volume_slider.grabbed = False
            if volume_slider.button_rect.collidepoint(mouse_pos):  
                volume_slider.hover()
            if volume_slider.grabbed:
                volume_slider.move_slider(mouse_pos)
                volume_slider.hover()
            else:
                volume_slider.hovered = False
            pygame.mixer.music.set_volume(volume_slider.get_value())
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    fps_clock.tick(fps)

    screen.fill(BLUE)
    if game_state != "pause" and game_state != "game over":
        if game_state == "start" and button.start_button.draw(screen):
            game_state = "ingame"
        if game_state == "ingame" and button.pause_button.draw(screen):
            game_state = "pause"
            pygame.mixer.music.pause()
            continue
        if button.exit_button.draw(screen):
            pygame.quit()
            sys.exit()
        if game_state == "ingame":
            screen.fill(BLUE)
            button.pause_button.draw(screen)
            if catx >= 500:
                x = -5
                y = -5  
            elif catx <= 100:
                x = 5
                y = 5
            catx += x
            caty += y
            screen.blit(catImg, (catx, caty))
            if catx == 500:
                game_state = "game over"
    elif game_state == "pause":
        if button.resume_button.draw(screen):
            game_state = "ingame"
            pygame.mixer.music.unpause()
        if button.main_menu_button.draw(screen):
            game_state = "start"
            pygame.mixer.music.unpause()
            catx = 100
            caty = 100
            x = 5
            y = 5
    else:
        if button.retry_button.draw(screen):
            game_state = "ingame"
            pygame.mixer.music.unpause()
            catx = 100
            caty = 100
            x = 5
            y = 5
        if button.to_main_menu_button.draw(screen):
            game_state = "start"
    if game_state == "start" or game_state == "pause":
            volume_slider.render(screen)
            mouse_pos = pygame.mouse.get_pos()
            mouse_state = pygame.mouse.get_pressed()
            if volume_slider.container_rect.collidepoint(mouse_pos):
                if mouse_state[0]:
                    volume_slider.grabbed = True
            if not mouse_state[0]:
                volume_slider.grabbed = False
            if volume_slider.button_rect.collidepoint(mouse_pos):  
                volume_slider.hover()
            if volume_slider.grabbed:
                volume_slider.move_slider(mouse_pos)
                volume_slider.hover()
            else:
                volume_slider.hovered = False
            pygame.mixer.music.set_volume(volume_slider.get_value())    