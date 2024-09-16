import pygame
import json
import os
import random
import math
import time

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
MAP_WIDTH, MAP_HEIGHT = 1600, 1200
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sneakerdoodle Game")


trigger_distance = 100 # Khoảng cách ngưỡng để kích hoạt mục tiêu
activation_delay = 0.5  # Thời gian trễ khi target được kích hoạt
cone_angle = 45
num_segments = 30

# Màu sắc
WHITE = (255, 255, 255)
BLUE = (82, 210, 238, 153)  #độ mờ 60%
# Hàm tính khoảng cách
def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

# Tải hình ảnh tạm thời
background_img = pygame.image.load('assets/background.png')
dog_img = pygame.image.load('assets/dog.png')
dog_img = pygame.transform.scale(dog_img, (50, 50))
target_img = pygame.image.load('assets/target.png')
target_img = pygame.transform.scale(target_img, (50, 50))
obstacle_img = pygame.image.load('assets/obstacle.png')
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))

# Lớp Camera
class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # self.player = player
        self.offset = pygame.math.Vector2()
        self.floor_rect = background_img.get_rect(topleft = (0, 0))

    def custom_draw(self, player, all_sprites):
        self.offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = player.rect.centery - SCREEN_HEIGHT // 2

        floor_offset_pos = self.floor_rect.topleft - self.offset
        screen.blit(background_img, floor_offset_pos)
        for sprite in all_sprites:
            offset_pos = sprite.rect.topleft - self.offset
            screen.blit(sprite.image, offset_pos)
            

# Lớp đối tượng Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = dog_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.sprint_speed = 8
       

    def move(self, keys, obstacles):
        if keys[pygame.K_LSHIFT]:  # Nhấn shift để chạy
            speed = self.sprint_speed
        else:
            speed = self.speed
        old_position = self.rect.topleft
        if keys[pygame.K_LEFT]:
            self.rect.x -= speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += speed
        if keys[pygame.K_UP]:
            self.rect.y -= speed
        if keys[pygame.K_DOWN]:
            self.rect.y += speed
        if (collide_with_obstacles(self, obstacles)):
            self.rect.topleft = old_position
    
    


# Lớp đối tượng Target (mục tiêu đuổi theo)
class Target(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = target_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 2.5  # Mục tiêu di chuyển chậm hơn người chơi
        self.is_active = False
        self.direction = pygame.Vector2(1, 0)  # Hướng nhìn ban đầu (hướng sang phải)
        self.last_activation_time = None

    def update(self, player, obstacles):
        self.check_cone_of_vision(player)
        # Nếu target đã được kích hoạt, delay 0.5 giây trước khi đuổi
        if self.is_active and self.last_activation_time and (time.time() - self.last_activation_time) >= activation_delay:
            self.move_towards_player(player, obstacles)        

    def check_cone_of_vision(self, player):
        # Kiểm tra nếu player nằm trong hình nón
        player_vector = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        player_distance = player_vector.length()
        player_direction = player_vector.normalize()

        # Tính góc giữa hướng target và player
        angle = self.direction.angle_to(player_direction)

        # Nếu player nằm trong hình nón 45 độ và trong bán kính trigger_distance, kích hoạt target
        if abs(angle) <= 22.5 and player_distance <= trigger_distance:
            self.is_active = True
            self.last_activation_time = time.time()

    def move_towards_player(self, player, obstacles):
        # Di chuyển mục tiêu theo hướng người chơi
        old_position = self.rect.topleft
        
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
            self.direction = pygame.Vector2(1, 0)
        if self.rect.x > player.rect.x:
            self.rect.x -= self.speed
            self.direction = pygame.Vector2(-1, 0)
        if self.rect.y < player.rect.y:
            self.rect.y += self.speed
            self.direction = pygame.Vector2(0, 1)
        if self.rect.y > player.rect.y:
            self.rect.y -= self.speed
            self.direction = pygame.Vector2(0, -1)
        if (collide_with_obstacles(self, obstacles)):
            self.rect.topleft = old_position

    def draw_vision_cone(self, camera_offset):
    # Tạo surface tạm thời với alpha để vẽ hình nón
        s = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)

        # Tạo danh sách các điểm cho hình nón
        points = [self.rect.center - camera_offset]  # Điểm bắt đầu tại vị trí target
        angle_step = cone_angle / num_segments  # Chia nhỏ hình nón thành các đoạn
        cone_distance = trigger_distance

        # Tính toán góc bắt đầu và kết thúc của hình nón
        start_angle = self.direction.angle_to(pygame.Vector2(1, 0)) - cone_angle / 2
        for i in range(num_segments + 1):
            angle = math.radians(start_angle + i * angle_step)
            x = self.rect.centerx + math.cos(angle) * cone_distance
            y = self.rect.centery + math.sin(angle) * cone_distance
            points.append((x - camera_offset.x, y - camera_offset.y))

        # Vẽ hình nón bằng màu xanh lam mờ
        pygame.draw.polygon(s, BLUE, points)
        
        # Vẽ lên màn hình chính
        screen.blit(s, (0, 0))


def collide_with_obstacles(sprites, obstacles): # Va chạm vật thể
        if pygame.sprite.spritecollideany(sprites, obstacles):
            return True
        return False

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
    camera = Camera()
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
        # Vẽ tất cả các đối tượng
        camera.custom_draw(player, all_sprites)
        for target in targets:
            target.draw_vision_cone(camera.offset)
        keys = pygame.key.get_pressed()

        # Di chuyển player
        player.move(keys, obstacles)

        # Cập nhật vị trí mục tiêu
        targets.update(player, obstacles)

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
