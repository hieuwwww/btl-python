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
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)


# Hàm tính khoảng cách
def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)


# Tải hình ảnh tạm thời
background_img = pygame.image.load('assets/background.png')
MAP_WIDTH, MAP_HEIGHT = background_img.get_width(), background_img.get_height()


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
    for obstacle in obstacles:
        if collide_with_obstacle(entity, obstacle):
            obstacle.image.set_alpha(128)
            if obstacle.image_path == 'assets/stone.png':
                handle_collision_small(entity, obstacle)
            else:
                handle_collision_large(entity, obstacle)
        else:
            obstacle.image.set_alpha(255)

    return velocity  # Trả về vận tốc mới để tiếp tục cập nhật trong lần sau


# Thu gọn mask để va chạm mượt hơn
def shrink_mask(mask):
    return mask.scale((mask.get_size()[0] - 5, mask.get_size()[1] - 5))


# Pseudocode for handling smooth sliding collisions
def handle_collision_small(sprite, obstacle):
    if sprite.rect.colliderect(obstacle.rect):
        old_pos = sprite.rect
        # Kiểm tra va chạm từ các hướng
        if 10 < sprite.rect.right - obstacle.rect.left < 25 and sprite.velocity.x > 0:
            # Va chạm từ bên trái
            sprite.rect.x = old_pos.x - 1  # Đặt lại vị trí để không đi xuyên qua
            sprite.velocity.x = 0
            sprite.velocity.y *= 0.8
        if 10 < obstacle.rect.right - sprite.rect.left < 25 and sprite.velocity.x < 0:
            # Va chạm từ bên phải
            sprite.rect.x = old_pos.x + 1
            sprite.velocity.x = 0
            sprite.velocity.y *= 0.8
        if 10 < sprite.rect.bottom - obstacle.rect.top < 25 and sprite.velocity.y > 0:
            # Va chạm từ trên
            sprite.rect.y = old_pos.y - 1
            sprite.velocity.y = 0
            sprite.velocity.x *= 0.8
        if 30 < obstacle.rect.bottom - sprite.rect.top < 45 and sprite.velocity.y < 0:
            # Va chạm từ dưới
            sprite.velocity.y = 0
            sprite.velocity.x *= 0.8
            sprite.rect.y = old_pos.y + 1


def handle_collision_large(sprite, obstacle):
    if sprite.rect.colliderect(obstacle.rect):
        old_pos = sprite.rect
        # Kiểm tra va chạm từ các hướng
        if 40 < sprite.rect.right - obstacle.rect.left < 50 and sprite.velocity.x > 0:
            # Va chạm từ bên trái
            sprite.rect.x = old_pos.x - 1  # Đặt lại vị trí để không đi xuyên qua
            sprite.velocity.x = 0
            sprite.velocity.y *= 0.8
        if 30 < obstacle.rect.right - sprite.rect.left < 45 and sprite.velocity.x < 0:
            # Va chạm từ bên phải
            sprite.rect.x = old_pos.x + 1
            sprite.velocity.x = 0
            sprite.velocity.y *= 0.8
        if 90 < sprite.rect.bottom - obstacle.rect.top < 105 and sprite.velocity.y > 0:
            # Va chạm từ trên
            sprite.rect.y = old_pos.y - 1
            sprite.velocity.y = 0
            sprite.velocity.x *= 0.8
        if 30 < obstacle.rect.bottom - sprite.rect.top < 45 and sprite.velocity.y < 0:
            # Va chạm từ dưới
            sprite.velocity.y = 0
            sprite.velocity.x *= 0.8
            sprite.rect.y = old_pos.y + 1


# Lớp Player với animation
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Tải hình ảnh cho các trạng thái
        self.idle_images = [
            pygame.transform.scale(pygame.image.load(f'assets/move/player_idle_{i}.png').convert_alpha(), (65, 53)) for
            i in range(4)]  # 6 frame idle
        self.moving_images = [
            pygame.transform.scale(pygame.image.load(f'assets/move/player_move_{i}.png').convert_alpha(), (65, 53)) for
            i in range(6)]  # 6 frame moving
        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.idle_images[self.current_frame]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x -= 5
        self.rect.y -= 5
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
    def __init__(self, x, y):
        super().__init__()
        # Thêm hình ảnh animation idle và moving
        self.idle_images = [
            pygame.transform.scale(pygame.image.load(f'assets/target_move/target_idle_{i}.png').convert_alpha(),
                                   (50, 65)) for i in range(4)]
        self.moving_images = [
            pygame.transform.scale(pygame.image.load(f'assets/target_move/target_move_{i}.png').convert_alpha(),
                                   (50, 65)) for i in range(6)]

        self.current_frame = 0
        self.animation_speed = 0.1
        self.image = self.idle_images[self.current_frame]  # Bắt đầu với trạng thái idle
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.max_speed = 3  # mục tiêu di chuyển chậm hơn mục tiêu
        self.acceleration = 0.2
        self.velocity = pygame.Vector2(0, 0)
        self.is_active = False
        self.direction = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))  # random hướng nhìn ban đầu
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
                self.moving_images = [pygame.transform.flip(moving_image, True, False) for moving_image in
                                      self.moving_images]
                self.idle_images = [pygame.transform.flip(idle_image, True, False) for idle_image in
                                    self.idle_images]  # Lật ảnh sang phải
            elif self.velocity.x < 0 and self.facing_right:
                self.facing_right = False
                self.moving_images = [pygame.transform.flip(moving_image, True, False) for moving_image in
                                      self.moving_images]
                self.idle_images = [pygame.transform.flip(idle_image, True, False) for idle_image in
                                    self.idle_images]  # Lật ảnh sang trái

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
    def __init__(self, x, y, patrol_points):
        super().__init__(x, y)
        self.run_images = [
            pygame.transform.scale(pygame.image.load(f'assets/patrolling_move/patrolling_{i}.png').convert_alpha(),
                                   (60, 70)) for i in range(6)]
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
    def __init__(self, x, y):
        super().__init__(x, y)
        # them anh animation idle, move, stop
        self.idle_image = [
            pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_idle_{i}.png').convert_alpha(),
                                   (50, 65)) for i in range(4)]
        self.move_image = [
            pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_move_{i}.png').convert_alpha(),
                                   (50, 65)) for i in range(6)]
        self.stop_image = [
            pygame.transform.scale(pygame.image.load(f'assets/distracted_move/distracted_stop_{i}.png').convert_alpha(),
                                   (50, 65)) for i in range(3)]

        self.current_frame = 0
        self.last_update = 0
        self.animation_speed = 100  # Tốc độ chuyển frame (ms)
        self.is_moving = False  # biến theo dõi trạng thái di chuyển
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
            self.velocity = move_entity(self, self.direction, self.velocity, self.acceleration, self.max_speed,
                                        obstacles)

    def deactivate(self, player):
        # Khi DistractedTarget bị mất sự chú ý, quay lại trạng thái không hoạt động
        if self.check_cone_of_vision(player):
            self.last_activation = time.time()
        if time.time() - self.last_activation > self.attention_span:
            self.is_active = False


def create_custom_mask(sprite, x, y, offset_x=0, offset_y=0):
    """Tạo một mask hình vuông nhỏ hơn ở giữa sprite."""
    # Tạo một surface tạm thời để vẽ hình vuông
    square_surface = pygame.Surface((x, y), pygame.SRCALPHA)
    square_surface.fill((255, 255, 255))  # Màu trắng cho vùng hitbox

    # Tạo một mask từ surface này
    square_mask = pygame.mask.from_surface(square_surface)

    # Cập nhật vị trí của mask dựa trên offset
    square_rect = square_surface.get_rect(center=sprite.rect.topleft)
    square_rect.y += offset_y
    square_rect.x += offset_x

    return square_mask, square_rect


def collide_with_obstacle(sprite, obstacle):
    # Tạo mask hình vuông nhỏ hơn cho obstacle
    obstacle_mask, obstacle_rect = create_custom_mask(obstacle, obstacle.width, obstacle.height, obstacle.x_offset,
                                                      obstacle.y_offset)

    # Lấy mask và vị trí của sprite
    sprite_mask = pygame.mask.from_surface(sprite.image)
    sprite_rect = sprite.rect

    # Tính toán offset giữa sprite và obstacle để kiểm tra overlap
    offset = (obstacle_rect.left - sprite_rect.left, obstacle_rect.top - sprite_rect.top)

    # Kiểm tra va chạm giữa sprite mask và obstacle mask nhỏ hơn
    if sprite_mask.overlap(obstacle_mask, offset):
        return True  # Có va chạm
    return False  # Không có va chạm


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
    def __init__(self, x_pos, y_pos, image_path, width, height, x_offset, y_offset):
        super().__init__()
        self.image_path = image_path
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (x_pos, y_pos)
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.width = width
        self.height = height


# Hàm tải level từ file JSON
def load_level(filename):
    with open(os.path.join('levels', filename), 'r') as f:
        return json.load(f)


# Lớp ScoreBar

class ScoreBar:
    def __init__(self, pos: tuple, size: tuple, star_requirement: tuple, target_count: int) -> None:
        self.pos = pos
        self.size = size  # chiều rộng theo trục Ox/ chiều dài theo trục Oy
        self.container_rect = pygame.Rect(pos, size)
        self.star_requirement = star_requirement
        self.target_count = target_count

    def draw(self, current_targer_count):
        x = self.pos[0]
        y = self.pos[1]
        # Vẽ
        #pygame.draw.rect(screen, WHITE, self.container_rect)
        not_glowing_star_img = pygame.image.load("assets/not_glowing_star.png").convert_alpha()
        glowing_star_img = pygame.image.load("assets/glowing_star.png").convert_alpha()

        # Khoảng cách giữa lề trên của thanh rìa ngoài và thanh hiển thị điểm bên trong
        left_margin = 5

        # Tính độ dài thanh hiển thị điểm và vẽ nó
        target_count_bar = pygame.Rect((x, y + left_margin), (
        self.size[0] * current_targer_count / self.target_count, self.size[1] - left_margin * 2))
        #pygame.draw.rect(screen, WHITE, target_count_bar)

        # Vẽ các đường phân mức cho từng mức sao
        for target_count_requirement in self.star_requirement:
            # Vị trí của đường phân mức
            x_new = x + self.size[0] * target_count_requirement / self.target_count
            indicate_line = pygame.Rect((x_new, y), (1, self.size[1]))
            #pygame.draw.rect(screen, BLACK, indicate_line)
            # Vẽ ngôi sao tương ứng với mức điểm
            if current_targer_count >= target_count_requirement:
                screen.blit(glowing_star_img,
                            (x_new - glowing_star_img.get_width() // 2, y - glowing_star_img.get_height() // 2))
            else:
                screen.blit(not_glowing_star_img,
                            (x_new - not_glowing_star_img.get_width() // 2, y - not_glowing_star_img.get_height() // 2))


# Lớp Slider
BUTTONSTATES = {
    False: "lightgray",  # không hovered
    True: "orange"  # hovered
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
        self.button_rect = pygame.Rect(self.slider_left_pos + self.initial_val - 5, self.slider_top_pos, 10,
                                       self.size[1])

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
        try:
            pos = pygame.mouse.get_pos()
            action = False

            if self.rect.collidepoint(pos):
                if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                    self.clicked = True
                    action = True
                    print("Button clicked!")
                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False

            cur_screen.blit(self.image, (self.rect.x, self.rect.y))
            return action

        except Exception as e:
            return False


# Chạy màn hình bắt đầu
start_img = pygame.image.load("assets/start_button.png").convert_alpha()
exit_img = pygame.image.load("assets/exit_button.png").convert_alpha()


def start_screen():
    pygame.mixer.music.load("assets/main_menu.mp3")
    pygame.mixer.music.play(-1)
    start_button = Button(150, 250, start_img, 0.7)
    exit_button = Button(450, 250, exit_img, 0.7)

    screen.fill((128, 128, 128))

    running = True
    while running:

        font = pygame.font.Font(None, 60)
        volume_text = font.render('SNEAKERDOODLE', True, (0, 0, 0))
        screen.blit(volume_text, (190, 100))

        # Kiểm tra sự kiện thoát
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Vẽ nút và kiểm tra xem có nhấn nút nào không
                if start_button.draw(screen):
                    #pygame.mixer.music.stop()
                    # Gọi hàm bắt đầu game khi nhấn nút Start
                    running = False
                    time.sleep(0.1)
                    choose_level_menu()
                if exit_button.draw(screen):
                    pygame.quit()
                    exit()  # Thoát chương trình khi nhấn nút Exit

                # Cập nhật màn hình
        pygame.display.update()


# Chạy màn hình pause game
to_main_menu_img = pygame.image.load('assets/to_main_menu_button.png').convert_alpha()
resume_img = pygame.image.load('assets/resume_button.png').convert_alpha()


def options_screen():
    running = True
    volume_slider = Slider((450, 100), (300, 20), 0.5, 0, 1)  # Tạo slider âm lượng một lần tại đây
    while running:
        screen.fill((128, 128, 128))
        font = pygame.font.Font(None, 36)

        volume_text = font.render('VOLUME', True, (0, 0, 0))
        screen.blit(volume_text, (150, 89))

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
        pygame.mixer.music.set_volume(volume_slider.get_value())
        # Nút để quay lại menu chính
        back_button = Button(450, 250, to_main_menu_img, 0.7)
        if back_button.draw(screen):
            print("Returning to Main Menu...")
            start_screen()
            running = False  # Quay lại màn hình chính
        # Nút quay lại game
        resume_button = Button(150, 250, resume_img, 0.7)
        if resume_button.draw(screen):
            print("Return to game")
            return
        pygame.display.update()


# Chạy màn hình khi kết thúc level/ game
retry_img = pygame.image.load('assets/retry_button.png')
next_level_img = pygame.image.load('assets/next_level_button.png')


def game_over_screen(actived_target, star_requirement, level_file, current_level):
    running = True

    retry_button = Button(140, 300, retry_img, 0.5)
    to_main_menu_button = Button(510, 300, to_main_menu_img, 0.5)
    next_level_button = Button(330, 300, next_level_img, 0.5)
    screen.fill(GRAY)

    if actived_target < star_requirement[0]:

        # Chơi nhạc khi thua level
        pygame.mixer.music.load("assets/game_over.mp3")
        pygame.mixer.music.play()

        while running:
            font = pygame.font.Font(None, 50)
            volume_text = font.render('YOU GOT CAUGHT', True, (0, 0, 0))
            screen.blit(volume_text, (240, 150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if retry_button.draw(screen):  # Chơi lại level
                print("Try again")
                return run_game(level_file)
            if to_main_menu_button.draw(screen):
                print("Not Try again")
                time.sleep(0.2)
                return start_screen()  # Quay về màn hình chính
            pygame.display.update()
    else:
        # Chơi nhạc khi hoàn thành level
        pygame.mixer.music.load("assets/level_complete.mp3")
        pygame.mixer.music.play()

        not_glowing_star_img = pygame.image.load("assets/not_glowing_star.png").convert_alpha()
        glowing_star_img = pygame.image.load("assets/glowing_star.png").convert_alpha()
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            # Vị trí bắt đầu của ảnh ngôi sao đầu tiên
            x = 100
            y = 100
            # Khoảng cách giữa các ảnh ngôi sao
            img_distance = 30
            for target_requirement in star_requirement:
                # Nếu số mục tiêu đạt đủ điều kiện thì hiển thị sao vàng và ngược lại
                if actived_target >= target_requirement:
                    screen.blit(glowing_star_img, (x, y))
                else:
                    screen.blit(not_glowing_star_img, (x, y))
                # Tăng khoảng cách giữa các ảnh
                x += glowing_star_img.get_width() + img_distance
            if retry_button.draw(screen):  # Chơi lại level
                print("Try again")
                return run_game(level_file)
            if to_main_menu_button.draw(screen):
                print("Not Try again")
                return start_screen()  # Quay về màn hình chính
            if next_level_button.draw(screen):
                print("Next Level")
                return run_game("level" + str(current_level + 1) + ".json")
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
    player.rect.x = level_data['player'][0]
    player.rect.y = level_data['player'][1]
    for target_pos in level_data['targets']:
        x = target_pos[0]
        y = target_pos[1]
        if target_pos[2] == 's':
            targets.add(Target(x, y))
        elif target_pos[2] == 'p':
            targets.add(PatrollingTarget(x, y, [[x + 50, y], [x - 50, y], [x, y - 50]]))
        elif target_pos[2] == 'd':
            targets.add(DistractedTarget(x, y))
    for obstacle in level_data['obstacles']:
        obstacles.add(Obstacle(*obstacle))
        # print(*obstacle)

    all_sprites = pygame.sprite.Group(targets, obstacles, player)
    score_bar = ScoreBar((30, 30), (200, 50), level_data['star_requirement'], len(targets))

    # Vòng lặp game
    clock = pygame.time.Clock()
    running = True

    # Chơi và lặp lại nhạc nền trong game liên tục
    pygame.mixer.music.load("assets/ingame_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    while running:
        screen.fill((0, 0, 0))

        # Vẽ tất cả các đối tượng
        camera.custom_draw(player, all_sprites)
        keys = pygame.key.get_pressed()

        # Di chuyển player
        player.move(keys, obstacles)

        # Cập nhật vị trí mục tiêu
        targets.update(player, obstacles, camera.offset)

        # Đếm số mục tiêu đã kích hoạt
        actived_target = 0
        for target in targets:
            if target.is_active:
                actived_target += 1
        # Hiển thị điểm
        score_bar.draw(actived_target)

        # Kiểm tra nếu người chơi va chạm mục tiêu
        if actived_target == level_data['star_requirement'][2] or pygame.sprite.spritecollideany(player, targets, custom_collide_shrunken_mask):
            print("You got caught!")
            return game_over_screen(actived_target, level_data['star_requirement'], level_file, level_data['level'])
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

def choose_level_menu():
    print("Choosing menu")
    back_button = Button(450, 250, to_main_menu_img, 0.7)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((128, 128, 128))
        level_list = list()
        for i in range(0, 9):
            level_list.append(Button(200 + (i%3)*150, 100 + (i//3)*150,pygame.image.load("assets/button_level" + str(i + 1) + ".png").convert_alpha(), 2))
        for i in range(0, 9):
            if level_list[i].draw(screen):
                print('level' + str(i + 1) + ".json" + " choosen")
                return run_game('level' + str(i + 1) + ".json")
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    start_screen()