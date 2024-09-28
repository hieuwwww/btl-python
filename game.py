import pygame
import json
import os
import random
import math
import time
import sys
# Khởi tạo Pygame
pygame.init()

# Biến xử lý cho class Slider
UNSELECTED = "red"
SELECTED = "white"
BUTTONSTATES = {
    True:SELECTED,
    False:UNSELECTED
}

# Cài đặt màn hình
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sneakerdoodle Game")


trigger_distance = 120 # Khoảng cách ngưỡng để kích hoạt mục tiêu
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
MAP_WIDTH, MAP_HEIGHT = background_img.get_width(), background_img.get_height()

dog_img = pygame.image.load('assets/dog.png').convert_alpha()
dog_img = pygame.transform.scale(dog_img, (50, 50))
target_img = pygame.image.load('assets/target.png').convert_alpha()
target_img = pygame.transform.scale(target_img, (40, 40))
patrol_target_img = pygame.image.load('assets/patrol_target.png').convert_alpha()
patrol_target_img = pygame.transform.scale(patrol_target_img, (40, 40))
distracted_target_img = pygame.image.load('assets/distracted_target.png').convert_alpha()
distracted_target_img = pygame.transform.scale(distracted_target_img, (40, 40))
obstacle_img = pygame.image.load('assets/obstacle.png').convert_alpha()
obstacle_img = pygame.transform.scale(obstacle_img, (50, 50))
start_img = pygame.image.load("assets/start_button.png").convert_alpha()
exit_img = pygame.image.load("assets/exit_button.png").convert_alpha()
pause_img = pygame.image.load("assets/pause_button.png").convert_alpha()
resume_img = pygame.image.load("assets/resume_button.png").convert_alpha()
main_menu_img = pygame.image.load("assets/main_menu_button.png").convert_alpha()
retry_img = pygame.image.load("assets/retry_button.png").convert_alpha()
to_main_menu_img = pygame.image.load("assets/to_main_menu_button.png").convert_alpha()

#Tải âm thanh tạm thời
pygame.mixer.music.load("assets/background_music.mp3")
pygame.mixer.music.set_volume(0.3)

#Lớp Button
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

#Lớp Slider
class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
        self.pos = pos
        self.size = size
        self.hovered = False
        self.grabbed = False

        self.slider_left_pos = self.pos[0] - (size[0]//2)
        self.slider_right_pos = self.pos[0] + (size[0]//2)
        self.slider_top_pos = self.pos[1] - (size[1]//2)

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos-self.slider_left_pos)*initial_val # <- percentage

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

        # label
        #self.text = UI.fonts['m'].render(str(int(self.get_value())), True, "white", None)
        #self.label_rect = self.text.get_rect(center = (self.pos[0], self.slider_top_pos - 15))
        
    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos
    def hover(self):
        self.hovered = True
    def render(self, screen):
        pygame.draw.rect(screen, "darkgray", self.container_rect)
        pygame.draw.rect(screen, BUTTONSTATES[self.hovered], self.button_rect)
    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos - 1
        button_val = self.button_rect.centerx - self.slider_left_pos
        return (button_val/val_range)
    # def display_value(self, app):
    #     self.text = UI.fonts['m'].render(str(int(self.get_value())), True, "white", None)
    #     app.screen.blit(self.text, self.label_rect)

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
            
# Phương thức toàn cục xử lý di chuyển, gia tốc và kiểm tra va chạm
def move_entity(entity, direction_vector, velocity, acceleration, max_speed, obstacles):
    # Cập nhật vận tốc dựa trên gia tốc và hướng
    velocity += direction_vector * acceleration

    # Giới hạn tốc độ tối đa
    if velocity.length() > max_speed:
        velocity.scale_to_length(max_speed)

    # Lưu vị trí cũ
    old_position = entity.rect.topleft

    # Cập nhật vị trí theo vận tốc
    entity.rect.x += velocity.x
    entity.rect.y += velocity.y
    
    # Kiểm tra ko ra ngoài bản đồ
    if entity.rect.left < 0:
        entity.rect.left = 0
    if entity.rect.right > MAP_WIDTH:
        entity.rect.right = MAP_WIDTH
    if entity.rect.top < 0:
        entity.rect.top = 0
    if entity.rect.bottom > MAP_HEIGHT:
        entity.rect.bottom = MAP_HEIGHT

    # Kiểm tra va chạm với chướng ngại vật
    if collide_with_obstacles(entity, obstacles):
        entity.rect.topleft = old_position  # Quay về vị trí cũ nếu có va chạm

    return velocity  # Trả về vận tốc mới để tiếp tục cập nhật trong lần sau

# Lớp đối tượng Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = dog_img
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.sprint_speed = 8
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.5 # Gia tốc
        self.max_speed = 5 # Tốc độ tối đa
        self.friction = 0.9 # Ma sát
       

    def move(self, keys, obstacles):
        direction_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_LSHIFT]:  # Nhấn shift để chạy
            self.max_speed = self.sprint_speed
        else:
            self.max_speed = self.speed
        # Xác định hướng di chuyển
        if keys[pygame.K_LEFT]:
            direction_vector.x = -1
        if keys[pygame.K_RIGHT]:
            direction_vector.x = 1
        if keys[pygame.K_UP]:
            direction_vector.y = -1
        if keys[pygame.K_DOWN]:
            direction_vector.y = 1
        
        
        if direction_vector.length() != 0:
            direction_vector = direction_vector.normalize()
        else:
            self.velocity *= self.friction
            if self.velocity.length() < 0.1:
                self.velocity = pygame.Vector2(0, 0)
        self.velocity = move_entity(self, direction_vector, self.velocity, self.acceleration, self.max_speed, obstacles)

# Lớp đối tượng Target (mục tiêu đuổi theo)
class Target(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_speed = 2  # Mục tiêu di chuyển chậm hơn người chơi
        self.acceleration = 0.2
        self.velocity = pygame.Vector2(0, 0)
        self.is_active = False
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))  # Hướng nhìn ban đầu (random)

    def update(self, player, obstacles, camera_offset):
        self.check_cone_of_vision(player)
        self.draw_vision_cone(player, camera_offset)
        # Nếu target đã được kích hoạt, delay 0.5 giây trước khi đuổi
        if self.is_active :
           self.move_towards_player(player, obstacles)

    def check_cone_of_vision(self, player):
        # Tính toán vector từ target đến player
        player_vector = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        player_distance = player_vector.length()

        if player_distance <= trigger_distance:
            # Tính toán góc giữa hướng target và hướng tới player
            player_direction = player_vector.normalize()
            angle = self.direction.angle_to(player_direction)

            # Nếu player nằm trong hình nón của target (dựa trên góc cone_angle)
            if abs(angle) <= cone_angle / 2:
                self.is_active = True
                return True

    def move_towards_player(self, player, obstacles):
        self.direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        self.velocity = move_entity(self, self.direction, self.velocity, self.acceleration, self.max_speed, obstacles)        

    def draw_vision_cone(self, player, camera_offset):
        # Tạo surface tạm thời với alpha để vẽ hình nón
        s = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)

        # Điểm bắt đầu tại vị trí target
        points = [self.rect.center - camera_offset]
        angle_step = cone_angle / num_segments
        cone_distance = trigger_distance

        # Sử dụng cùng hướng với hàm check_cone_of_vision
        if self.is_active:
            direction_vector = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
            if direction_vector.length() > 0:
                direction_vector = direction_vector.normalize()
            start_angle = math.degrees(math.atan2(direction_vector.y, direction_vector.x)) - cone_angle / 2
        else:
            start_angle = math.degrees(math.atan2(self.direction.y, self.direction.x)) - cone_angle / 2

        # Tạo các điểm cho hình nón dựa trên góc và khoảng cách
        for i in range(num_segments + 1):
            angle = math.radians(start_angle + i * angle_step)
            x = self.rect.centerx + math.cos(angle) * cone_distance
            y = self.rect.centery + math.sin(angle) * cone_distance
            points.append((x - camera_offset.x, y - camera_offset.y))

        # Vẽ hình nón bằng màu xanh lam mờ
        pygame.draw.polygon(s, BLUE, points)

        # Vẽ lên màn hình chính
        screen.blit(s, (0, 0))
# Target đi tuần tra khu vực
class PatrollingTarget(Target):
    def __init__(self, x, y, image, patrol_points):
        super().__init__(x, y, image)
        self.patrol_points = patrol_points # Tuần tra theo các điểm
        self.current_point = 0
        self.patrol_speed = 0.8

    def update(self, player, obstacles, camera_offset):   
        if not self.is_active:
            self.patrol()
        self.check_cone_of_vision(player)
        self.draw_vision_cone(player, camera_offset)
        if self.is_active:
            self.move_towards_player(player, obstacles)
    
    def patrol(self): # Đi tuần
        # Điểm ban đầu
        target_point = pygame.Vector2(self.patrol_points[self.current_point])

        direction_vector = target_point - pygame.Vector2(self.rect.center)
        if direction_vector.length() > 0:
            direction_vector = direction_vector.normalize()
        # Di chuyển
        self.rect.x += direction_vector.x * self.patrol_speed
        self.rect.y += direction_vector.y * self.patrol_speed

        # Chuyển sang điểm tiếp theo
        if pygame.Vector2(self.rect.center).distance_to(target_point) < 5:
            self.current_point = (self.current_point + 1) % len(self.patrol_points)
        
        # Chuyển lại hướng
        self.direction = direction_vector

class DistractedTarget(Target):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.attention_span = 5
        self.last_activation = 0

    def deactivate(self, player):
        if self.check_cone_of_vision(player):
            self.last_activation = time.time()
        if time.time() - self.last_activation > self.attention_span:
            self.is_active = False
    
    def update(self, player, obstacles, camera_offset):
        self.deactivate(player)
        super().update(player, obstacles, camera_offset)



def collide_with_obstacles(sprites, obstacles): # Va chạm vật thể
        if pygame.sprite.spritecollideany(sprites, obstacles) and pygame.sprite.spritecollideany(sprites, obstacles, pygame.sprite.collide_mask):
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
    volume_slider = Slider((500, 700),(450, 50), 0.5, 0, 1)
    player = Player()
    targets = pygame.sprite.Group()

    obstacles = pygame.sprite.Group()
    camera = Camera()
    start_button = Button(100, 200, start_img, 0.5)
    exit_button = Button(300, 200, exit_img, 0.5)
    pause_button = Button(50, 50, pause_img, 0.5)
    resume_button = Button(75, 50, resume_img, 1)
    main_menu_button = Button(75, 150, main_menu_img, 0.5)
    retry_button = Button(100, 200, retry_img, 0.5)
    to_main_menu_button = Button(300, 200, to_main_menu_img, 0.5)
    # Tải level
    level_data = load_level(level_file)
    for target_pos in level_data['targets']:
        x = target_pos[0]
        y = target_pos[1]
        if target_pos[2] == 's':
            targets.add(Target(x, y, target_img))
        elif target_pos[2] == 'p':
            targets.add(PatrollingTarget(x, y, patrol_target_img, [[x + 50, y],[x - 50, y], [x, y - 50]]))
        elif target_pos[2] == 'd':
            targets.add(DistractedTarget(x, y, distracted_target_img))
    for obstacle_pos in level_data['obstacles']:
        obstacles.add(Obstacle(*obstacle_pos))

    all_sprites = pygame.sprite.Group(player, targets, obstacles)

    
    
    
    # Vòng lặp game
    clock = pygame.time.Clock()
    game_state = "start"
    running = False
    pygame.mixer.music.play()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
        if game_state == "start":
            screen.fill(WHITE)
            print("YIPEE")
            if start_button.draw(screen):
                game_state = "ingame"
            if exit_button.draw(screen):
                pygame.quit()
                sys.exit()
        if game_state == "ingame":
            camera.custom_draw(player, all_sprites)
            keys = pygame.key.get_pressed()
            # Di chuyển player
            player.move(keys, obstacles)
            # Cập nhật vị trí mục tiêu
            targets.update(player, obstacles, camera.offset)
            # Kiểm tra nếu người chơi va chạm mục tiêu
            if pygame.sprite.spritecollideany(player, targets):
                print("You got caught!")
                game_state = "game_over"
                running = False
            # Cập nhật màn hình
            pygame.display.flip()
            # Tốc độ khung hình
            clock.tick(60)
            if pause_button.draw(screen):
                game_state = "pause"
        if game_state == "game_over":
            if retry_button.draw(screen):
                game_state = "ingame"
            if to_main_menu_button.draw(screen):
                game_state = "start"
        if game_state == "pause":
            if resume_button.draw(screen):
                game_state = "ingame"
            if to_main_menu_button.draw(screen):
                game_state = "start"
        print(game_state)
    pygame.quit()

if __name__ == '__main__':
    run_game('level1.json')
