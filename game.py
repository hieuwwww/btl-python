import pygame
import json
import os
import random
import math

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
WIDTH, HEIGHT = 1600, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sneakerdoodle Game")

# Màu sắc
WHITE = (255, 255, 255)

# Khoảng cách ngưỡng để kích hoạt mục tiêu
trigger_distance = 100

# Hàm tính khoảng cách
def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

# Tải hình ảnh tạm thời
background_img = pygame.image.load('assets/background.png')
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
dog_img = pygame.image.load('assets/dog.png')
dog_img = pygame.transform.scale(dog_img, (50, 50))
target_img = pygame.image.load('assets/target.png')
target_img = pygame.transform.scale(target_img, (50, 50))
obstacle_img = pygame.image.load('assets/obstacle.png')
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))

# Lớp đối tượng Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = dog_img
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.sprint_speed = 8
        self.is_active = False

    def move(self, keys):
        if keys[pygame.K_LSHIFT]:  # Nhấn shift để chạy
            speed = self.sprint_speed
        else:
            speed = self.speed
        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
        if keys[pygame.K_UP]:
            self.rect.y -= speed
        if keys[pygame.K_DOWN]:
            self.rect.y += speed
    def check_distance(self, player):
        target_pos = (self.rect.x, self.rect.y)
        dis = distance()

# Lớp đối tượng Target (mục tiêu đuổi theo)
class Target(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = target_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2.5  # Mục tiêu di chuyển chậm hơn người chơi

    def update(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        if self.rect.x > player.rect.x:
            self.rect.x -= self.speed
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
        if self.rect.y > player.rect.y:
            self.rect.y -= self.speed

# Lớp Obstacle (chướng ngại vật)
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = obstacle_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

# Hàm tải level từ file JSON
def load_level(filename):
    with open(os.path.join('levels', filename), 'r') as f:
        return json.load(f)

# Hàm chính để chạy game
def run_game(level_file):
    # Tạo đối tượng
    player = Player()
    targets = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # Tải level
    level_data = load_level(level_file)
    for target_pos in level_data['targets']:
        targets.add(Target(*target_pos))
    for obstacle_pos in level_data['obstacles']:
        obstacles.add(Obstacle(*obstacle_pos))

    all_sprites = pygame.sprite.Group(player, targets, obstacles)
    
    # Vòng lặp game
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.blit(background_img, (0, 0))
        keys = pygame.key.get_pressed()

        # Di chuyển player
        player.move(keys)

        # Cập nhật vị trí mục tiêu
        targets.update(player)

        # Vẽ tất cả các đối tượng
        all_sprites.draw(screen)
        
        # Kiểm tra nếu người chơi va chạm mục tiêu
        if pygame.sprite.spritecollideany(player, targets):
            print("You got caught!")
            running = False

        # Cập nhật màn hình
        pygame.display.flip()

        # Tốc độ khung hình
        clock.tick(60)

        # Kiểm tra sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == '__main__':
    run_game('level1.json')
