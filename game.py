from os.path import curdir

import pygame
import json
import os
import random
import math
import time

import pygame.image

# Khởi tạo Pygame
pygame.init()

# Cài đặt màn hình
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sneakerdoodle Game")

trigger_distance = 120  # Khoảng cách ngưỡng để kích hoạt mục tiêu
activation_delay = 0.5  # Thời gian trễ khi target được kích hoạt
cone_angle = 45
num_segments = 30

# Màu sắc
WHITE = (255, 255, 255)
BLUE = (82, 210, 238, 153)  # độ mờ 60%


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
obstacle_img = pygame.transform.scale(obstacle_img, (120, 120))


# Lớp Camera
class Camera(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # self.player = player
        self.offset = pygame.math.Vector2()
        self.floor_rect = background_img.get_rect(topleft=(0, 0))

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
#Thu gọn mask để va chạm mượt hơn
def shrink_mask(mask):
    return mask.scale((mask.get_size()[0] - 5, mask.get_size()[1] - 5))

# Lớp Player với animation
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Tải hình ảnh cho các trạng thái
        self.idle_images = [pygame.transform.scale(pygame.image.load(f'assets/move/player_idle_{i}.png').convert_alpha(), (65, 53)) for i in range(4)]  # 4 frame idle
        self.moving_images = [pygame.transform.scale(pygame.image.load(f'assets/move/player_move_{i}.png').convert_alpha(), (65, 53)) for i in range(4)]  # 4 frame moving
        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.idle_images[self.current_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.speed = 5
        self.sprint_speed = 8
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 0.5
        self.max_speed = 5
        self.friction = 0.9
        self.is_moving = False
        self.facing_right = True  # Biến để xác định hướng của nhân vật
        self.last_update = pygame.time.get_ticks()

    def update_animation(self):
        # Lấy thời gian hiện tại
        current_time = pygame.time.get_ticks()

        # Chuyển frame sau một khoảng thời gian nhất định (điều chỉnh animation_speed)
        if current_time - self.last_update > 100:  # Cứ 100ms chuyển frame
            self.last_update = current_time
            self.current_frame += 1

            if self.is_moving:
                if self.current_frame >= len(self.moving_images):
                    self.current_frame = 0
                self.image = self.moving_images[self.current_frame]
            else:
                if self.current_frame >= len(self.idle_images):
                    self.current_frame = 0
                self.image = self.idle_images[self.current_frame]
            self.mask = shrink_mask(pygame.mask.from_surface(self.image))
            # Chỉ lật ảnh khi cần (khi thay đổi hướng)
            if self.facing_right and self.image.get_width() < 0:
                self.image = pygame.transform.flip(self.image, True, False)
            elif not self.facing_right and self.image.get_width() > 0:
                self.image = pygame.transform.flip(self.image, True, False)

    def move(self, keys, obstacles):
        direction_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_LSHIFT]:
            self.max_speed = self.sprint_speed
        else:
            self.max_speed = self.speed

        # Xác định hướng di chuyển
        if keys[pygame.K_LEFT]:
            direction_vector.x = -1
            self.facing_right = False  # Nhân vật quay mặt sang trái
        if keys[pygame.K_RIGHT]:
            direction_vector.x = 1
            self.facing_right = True  # Nhân vật quay mặt sang phải
        if keys[pygame.K_UP]:
            direction_vector.y = -1
        if keys[pygame.K_DOWN]:
            direction_vector.y = 1

        # Xác định trạng thái di chuyển
        if direction_vector.length() != 0:
            direction_vector = direction_vector.normalize()
            self.is_moving = True
        else:
            self.is_moving = False
            self.velocity *= self.friction
            if self.velocity.length() < 0.1:
                self.velocity = pygame.Vector2(0, 0)

        # Cập nhật vị trí và hoạt ảnh
        self.velocity = move_entity(self, direction_vector, self.velocity, self.acceleration, self.max_speed, obstacles)
        self.update_animation()


# Lớp đối tượng Target (mục tiêu đuổi theo)
class Target(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        # Thêm hình ảnh animation idle và moving
        self.idle_images = [pygame.transform.scale(pygame.image.load(f'assets/target_move/target_idle_{i}.png').convert_alpha(), (50, 65)) for i in range(4)]
        self.moving_images = [pygame.transform.scale(pygame.image.load(f'assets/target_move/target_move_{i}.png').convert_alpha(), (50, 65)) for i in range(4)]

        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.idle_images[self.current_frame]  # Bắt đầu với trạng thái idle
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_speed = 2  # mục tiêu di chuyển chậm hơn mục tiêu
        self.acceleration = 0.2
        self.velocity = pygame.Vector2(0, 0)
        self.is_active = False
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))  #random hướng nhìn ban đầu
        self.last_update = pygame.time.get_ticks()
        self.facing_right = True  # Biến để theo dõi hướng nhìn

    def update(self, player, obstacles, camera_offset):
        self.check_cone_of_vision(player)
        self.draw_vision_cone(player, camera_offset)
        # Nếu target đã được kích hoạt, delay 0.5 giây trước khi đuổi
        if self.is_active:
            self.move_towards_player(player, obstacles)
        self.update_animation()

    def update_animation(self):
        # Lấy thời gian hiện tại
        current_time = pygame.time.get_ticks()

        # Chuyển frame sau một khoảng thời gian nhất định
        if current_time - self.last_update > 100:  # Cứ 100ms chuyển frame
            self.last_update = current_time
            self.current_frame += 1
            if self.velocity.length() > 0:  # Nếu đang di chuyển
                if self.current_frame >= len(self.moving_images):
                    self.current_frame = 0
                self.image = self.moving_images[self.current_frame]
            else:  # Nếu đứng yên
                if self.current_frame >= len(self.idle_images):
                    self.current_frame = 0
                self.image = self.idle_images[self.current_frame]

            if self.velocity.x > 0 and not self.facing_right:
                self.facing_right = True
                self.moving_images = [pygame.transform.flip(moving_image, True, False) for moving_image in self.moving_images]
                self.idle_images = [pygame.transform.flip(idle_image, True, False) for idle_image in self.idle_images]  # Lật ảnh sang phải
            elif self.velocity.x < 0 and self.facing_right:
                self.facing_right = False
                self.moving_images = [pygame.transform.flip(moving_image, True, False) for moving_image in self.moving_images]
                self.idle_images = [pygame.transform.flip(idle_image, True, False) for idle_image in self.idle_images]  # Lật ảnh sang trái

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
        if self.direction.length() > 0:  # Kiểm tra nếu có hướng di chuyển
            self.direction = self.direction.normalize()
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
        self.run_images = [pygame.transform.scale(pygame.image.load(f'assets/patrolling_move/patrolling_{i}.png').convert_alpha(), (60, 70)) for i in range(4)]
        self.animation_speed = 100
        self.current_frame = 0
        self.last_update = 0

        self.patrol_points = patrol_points  # Tuần tra theo các điểm
        self.current_point = 0
        self.patrol_speed = 0.8

        self.facing_right = True  # Biến theo dõi hướng của nhân vật

    def update(self, player, obstacles, camera_offset):
        if not self.is_active:
            self.patrol()  # Khi không phát hiện người chơi, tuần tra

        # Kiểm tra nếu người chơi nằm trong tầm nhìn
        self.check_cone_of_vision(player)
        # Vẽ hình nón tầm nhìn của nhân vật tuần tra
        self.draw_vision_cone(player, camera_offset)
        if self.is_active:
            self.move_towards_player(player, obstacles)  # Di chuyển về phía người chơi nếu phát hiện

        # Cập nhật hoạt ảnh tuần tra
        self.update_animation()

    def patrol(self):  # Đi tuần
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

    def update_animation(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update > self.animation_speed:
            self.last_update = current_time
            self.current_frame = (self.current_frame + 1) % len(self.run_images)
            self.image = self.run_images[self.current_frame]

            # Lật hình ảnh khi thay đổi hướng
            if self.direction.x > 0 and not self.facing_right:
                self.facing_right = True
                self.run_images = [pygame.transform.flip(move_image, True, False) for move_image in self.run_images]
            elif self.direction.x < 0 and self.facing_right:
                self.facing_right = False
                self.run_images = [pygame.transform.flip(move_image, True, False) for move_image in self.run_images]

class DistractedTarget(Target):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        # them anh animation idle, move, stop
        self.idle_image = [pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_idle_{i}.png').convert_alpha(), (50, 65)) for i in range(4)]
        self.move_image = [pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_move_{i}.png').convert_alpha(), (50, 65)) for i in range(4)]
        self.stop_image = [pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_stop_{i}.png').convert_alpha(), (50, 65)) for i in range(3)]

        self.current_frame = 0
        self.last_update = 0
        self.animation_speed = 100  # Tốc độ chuyển frame (ms)
        self.is_moving = False   # biến theo dõi trạng thái di chuyển
        self.is_stopping = False  # Biến theo dõi trạng thái dừng
        self.stop_time = 0  # Thời gian dừng
        self.stop_duration = 5000  # Thời gian dừng 5 giây
        self.facing_left = False
        self.attention_span = 5
        self.last_activation = 0
        self.move_start_time = 0  # thời gian bắt đầu di chuyển

    def update(self, player, obstacles, camera_offset):
        self.deactivate(player)  # Kiểm tra xem DistractedTarget có mất sự tập trung không
        super().update(player, obstacles, camera_offset)

        # Nếu dừng lại, đếm thời gian trước khi quay lại trạng thái idle
        if self.is_stopping and pygame.time.get_ticks() - self.stop_time >= self.stop_duration:
            self.is_stopping = False

        # Cập nhật animation khi di chuyển hoặc đứng yên
        self.update_animation()

    def update_animation(self):
        # lay thoi gian hien tai
        current_time = pygame.time.get_ticks()

        if current_time - self.last_update > self.animation_speed:
            self.last_update = current_time
            self.current_frame += 1

            if self.is_moving:
                if self.current_frame >= len(self.move_image):
                    self.current_frame = 0
                self.image = self.move_image[self.current_frame]
            elif self.is_stopping:
                if self.current_frame >= len(self.stop_image):
                    self.current_frame = 0
                self.image = self.stop_image[self.current_frame]
            else:
                if self.current_frame >= len(self.idle_image):
                    self.current_frame = 0
                self.image = self.idle_image[self.current_frame]

            # Xử lý lật ảnh khi đổi hướng
            if self.velocity.x > 0 and not self.facing_right:
                self.facing_right = True
                self.move_image = [pygame.transform.flip(moving_image, True, False) for moving_image in
                                      self.move_image]
                self.idle_image = [pygame.transform.flip(idle_image, True, False) for idle_image in
                                    self.idle_image]  # Lật ảnh sang phải
            elif self.velocity.x < 0 and self.facing_right:
                self.facing_right = False
                self.move_image = [pygame.transform.flip(moving_image, True, False) for moving_image in
                                      self.move_image]
                self.idle_image = [pygame.transform.flip(idle_image, True, False) for idle_image in
                                    self.idle_image]  # Lật ảnh sang trái

    def move_towards_player(self, player, obstacles):
        # Tính toán hướng và khoảng cách di chuyển về phía người chơi
        self.direction = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        if not self.is_moving and not self.is_stopping:
            self.is_moving = True
            self.move_start_time = pygame.time.get_ticks()  # ghi lại thời gian bắt đầu di chuyển

        # di chuyển trong thời gian nhất định (5 giây)
        if pygame.time.get_ticks() - self.move_start_time >= self.stop_duration:
            self.is_moving = False  # sau 5 giây, dừng lại
            self.is_stopping = True
            self.stop_time = pygame.time.get_ticks()

        if self.is_moving:
            # Chỉ di chuyển khi đang ở trạng thái di chuyển
            self.velocity = move_entity(self, self.direction, self.velocity, self.acceleration, self.max_speed, obstacles)

    def deactivate(self, player):
        # Khi DistractedTarget bị mất sự chú ý, quay lại trạng thái không hoạt động
        if self.check_cone_of_vision(player):
            self.last_activation = time.time()
        if time.time() - self.last_activation > self.attention_span:
            self.is_active = False


def collide_with_obstacles(sprites, obstacles):  # Va chạm vật thể
    if pygame.sprite.spritecollideany(sprites, obstacles) and pygame.sprite.spritecollideany(sprites, obstacles, pygame.sprite.collide_mask):
        return True
    return False

def custom_collide_shrunken_mask(sprite1, sprite2):
    # Shrink mask của sprite1 và sprite2
    mask1 = shrink_mask(pygame.mask.from_surface(sprite1.image))
    mask2 = shrink_mask(pygame.mask.from_surface(sprite2.image))
    
    # Tính toán offset giữa 2 sprite
    offset = (sprite2.rect.left - sprite1.rect.left, sprite2.rect.top - sprite1.rect.top)

    # Kiểm tra va chạm bằng hàm overlap giữa 2 mask đã thu nhỏ
    return mask1.overlap(mask2, offset) is not None
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
    

#Lớp Slider
BUTTONSTATES = {
    False: "lightgray",  # không hovered
    True: "orange"       # hovered
}

class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: int, max: int) -> None:
        self.pos = pos
        self.size = size
        self.hovered = False
        self.grabbed = False

        self.slider_left_pos = self.pos[0] - (size[0] // 2)
        self.slider_right_pos = self.pos[0] + (size[0] // 2)
        self.slider_top_pos = self.pos[1] - (size[1] // 2)

        self.min = min
        self.max = max
        self.initial_val = (self.slider_right_pos - self.slider_left_pos) * initial_val  # percentage

        self.container_rect = pygame.Rect(self.slider_left_pos, self.slider_top_pos, self.size[0], self.size[1])
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10, self.size[1])

    def move_slider(self, mouse_pos):
        pos = mouse_pos[0]
        if pos < self.slider_left_pos:
            pos = self.slider_left_pos
        if pos > self.slider_right_pos:
            pos = self.slider_right_pos
        self.button_rect.centerx = pos

    def hover(self):
        self.hovered = True

    def unhover(self):
        self.hovered = False

    def render(self, screen):
        pygame.draw.rect(screen, "darkgray", self.container_rect)
        pygame.draw.rect(screen, BUTTONSTATES[self.hovered], self.button_rect)

    def get_value(self):
        val_range = self.slider_right_pos - self.slider_left_pos
        button_val = self.button_rect.centerx - self.slider_left_pos
        return (button_val / val_range) * (self.max - self.min) + self.min
class Button:
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False  # Thêm biến này để theo dõi trạng thái nhấn
    
    def draw(self, cur_screen):
        # Lấy vị trí chuột hiện tại
        pos = pygame.mouse.get_pos()
        action = False  # Biến để xác định có nhấn hay không

        # Kiểm tra nếu con trỏ chuột đang nằm trên nút
        if self.rect.collidepoint(pos):
            # Kiểm tra nếu nhấn chuột trái
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True  # Cập nhật trạng thái là đã nhấn
                action = True  # Xác định đã có hành động nhấn
                print("Button clicked!")
            # Kiểm tra nếu chuột không còn nhấn
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False  # Reset trạng thái để cho phép nhấn tiếp
        
        # Vẽ nút lên màn hình
        cur_screen.blit(self.image, (self.rect.x, self.rect.y))
        
        return action  # Trả về True nếu nút được nhấn
# Chạy màn hình bắt đầu
start_img = pygame.image.load("assets/start_button.png").convert_alpha()
exit_img = pygame.image.load("assets/exit_button.png").convert_alpha()
def start_screen():
    start_button = Button(100, 200, start_img, 0.5)
    exit_button = Button(300, 200, exit_img, 0.5)
    
    screen.fill((255, 255, 255))

    running = True
    while running:
        # Kiểm tra sự kiện thoát
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Vẽ nút và kiểm tra xem có nhấn nút nào không
        if start_button.draw(screen):
            print("Start button clicked! Moving to the game...")
            # Gọi hàm bắt đầu game khi nhấn nút Start
            running = False
            run_game('level1.json')
        if exit_button.draw(screen):
            print("Exit button clicked! Exiting game...")
            pygame.quit()
            exit()  # Thoát chương trình khi nhấn nút Exit

        # Cập nhật màn hình
        pygame.display.update()

#Chạy màn hình pause game
to_main_menu_img = pygame.image.load('assets/to_main_menu_button.png').convert_alpha()
resume_img = pygame.image.load('assets/resume_button.png').convert_alpha()
def options_screen():
    running = True
    volume_slider = Slider((400, 100), (300, 20), 0.5, 0, 1)  # Tạo slider âm lượng một lần tại đây
    while running:
        screen.fill((200, 200, 200))
        font = pygame.font.Font(None, 36)

        volume_text = font.render('Volume', True, (0, 0, 0))
        screen.blit(volume_text, (100, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and volume_slider.container_rect.collidepoint(event.pos):
                volume_slider.move_slider(event.pos)
                if volume_slider.button_rect.collidepoint(event.pos):
                    volume_slider.grabbed = True
            if event.type == pygame.MOUSEBUTTONUP:
                volume_slider.grabbed = False
            if event.type == pygame.MOUSEMOTION:
                if volume_slider.grabbed:
                    volume_slider.move_slider(event.pos)

        # Kiểm tra hover
        if volume_slider.container_rect.collidepoint(pygame.mouse.get_pos()):
            volume_slider.hover()
        else:
            volume_slider.unhover()

        volume_slider.render(screen)
        # Nút để quay lại menu chính
        back_button = Button(400, 200, to_main_menu_img, 0.5)
        if back_button.draw(screen):
            print("Returning to Main Menu...")
            start_screen()
            running = False  # Quay lại màn hình chính
        # Nút quay lại game
        resume_button = Button(100, 200, resume_img, 0.5)
        if resume_button.draw(screen):
            print("Return to game")
            return
        pygame.display.update()

#Chạy màn hình khi kết thúc level/ game
retry_img = pygame.image.load('assets/retry_button.png')
def game_over_screen():
    running = True
    retry_button = Button(100, 300, retry_img, 0.5)
    to_main_menu_button = Button(400, 300, to_main_menu_img, 0.5)
    screen.fill(WHITE)
    print("Initiate game over menu")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if retry_button.draw(screen): # Chơi lại level
            print("Try again")
            return run_game('level1.json')
        if to_main_menu_button.draw(screen):
            print("Not Try again")
            return start_screen() # Quay về màn hình chính
        pygame.display.update()

# Hàm chính để chạy game
pause_img = pygame.image.load('assets/pause_button.png')
def run_game(level_file):
    # Tạo đối tượng
    player = Player()
    targets = pygame.sprite.Group()

    obstacles = pygame.sprite.Group()
    camera = Camera()
    options_button = Button(700, 20, pause_img, 0.5)  # Ví dụ: dùng hình ảnh của nút Exit
    
    # Tải level
    level_data = load_level(level_file)
    for target_pos in level_data['targets']:
        x = target_pos[0]
        y = target_pos[1]
        if target_pos[2] == 's':
            targets.add(Target(x, y, target_img))
        elif target_pos[2] == 'p':
            targets.add(PatrollingTarget(x, y, patrol_target_img, [[x + 50, y], [x - 50, y], [x, y - 50]]))
        elif target_pos[2] == 'd':
            targets.add(DistractedTarget(x, y, distracted_target_img))
    for obstacle_pos in level_data['obstacles']:
        obstacles.add(Obstacle(*obstacle_pos))

    all_sprites = pygame.sprite.Group(player, targets, obstacles)

    # Vòng lặp game
    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill((0, 0, 0))
        
        # Vẽ tất cả các đối tượng
        camera.custom_draw(player, all_sprites)
        keys = pygame.key.get_pressed()

        # Di chuyển player
        player.move(keys, obstacles)

        # Cập nhật vị trí mục tiêu
        targets.update(player, obstacles, camera.offset)

        # Kiểm tra nếu người chơi va chạm mục tiêu
        if pygame.sprite.spritecollideany(player, targets, custom_collide_shrunken_mask):
            print("You got caught!")
            return game_over_screen()
        if options_button.draw(screen):
            print("Opening Options...")
            options_screen()  # Mở menu Options khi nhấn nút

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
    start_screen()
    #run_game('level1.json')