import pygame, sys
from pygame.locals import *

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1200
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

start_img = pygame.image.load("assets/start_button.png").convert_alpha()
exit_img = pygame.image.load("assets/exit_button.png").convert_alpha()
pause_img = pygame.image.load("assets/pause_button.png").convert_alpha()
resume_img = pygame.image.load("assets/resume_button.png").convert_alpha()
main_menu_img = pygame.image.load("assets/main_menu_button.png").convert_alpha()
retry_img = pygame.image.load("assets/retry_button.png").convert_alpha()
to_main_menu_img = pygame.image.load("assets/to_main_menu_button.png").convert_alpha()
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()

        self.image = pygame.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
    
    def draw(self, cur_screen):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True   
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        cur_screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

start_button = Button(100, 400, start_img, 0.5)
exit_button = Button(600, 400, exit_img, 0.5)
pause_button = Button(200, 200, pause_img, 0.5)
resume_button = Button(300, 300, resume_img, 1)
main_menu_button = Button(300, 500, main_menu_img, 1)
retry_button = Button(100, 600, retry_img, 1)
to_main_menu_button = Button(500, 600, to_main_menu_img, 1)
# run = True
# while run:

#     screen.fill((0, 0, 0))

#     if start_button.draw():
#         print("END OF THE WORLD!!!")
#     if exit_button.draw():
#         pygame.quit()
#         sys.exit()
#     for event in pygame.event.get():
#         if event.type == QUIT:
#             pygame.quit()
#             sys.quit()
#     pygame.display.update()            
