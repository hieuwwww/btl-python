import os
import json
from ctypes import pydll

import pygame.transform


# Tạo level với số lượng mục tiêu và chướng ngại vật
def create_level(targets, obstacles, filename):
    # Kiểm tra nếu thư mục 'levels' không tồn tại và tạo mới
    if not os.path.exists('levels'):
        os.makedirs('levels')
    
    # Kiểm tra xem đường dẫn có phải là tệp không
    file_path = os.path.join('levels', filename)
    
    # Tạo tệp JSON và ghi dữ liệu vào đó
    level_data = {
        'targets': targets,
        'obstacles': obstacles
    }
    with open(file_path, 'w') as f:
        json.dump(level_data, f)
    print(f'Level {filename} created!')
# đường dẫn đến hình ảnh và offset cho hitbox thật
obs1_path = 'assets/obstacle.png'
obs1_offset = (45, 52, 62, 114) # width, height, x_offset, y_offset
obs2_path = 'assets/obstacle2.png'
obs2_offset = (40, 20, 53, 94)
obs3_path = 'assets/stone.png'
obs3_offset = (40, 40, 20, 20)
obs4_path = 'assets/house.png'
obs4_offset = (117, 90, 70, 125)

# Ví dụ tạo level với 3 mục tiêu và 2 chướng ngại vật
if __name__ == '__main__':
    targets = [(100, 150, 'd'), (200, 250, 's'), (300, 650, 'p')]
    #obstacles = [(500, 200, obs2_image, *obs2_offset)]
    obstacles = [(500, 200, obs2_path, *obs2_offset), (100, 300, obs3_path, *obs3_offset), (200, 80, obs2_path, *obs2_offset), (100, 900, obs2_path, *obs2_offset), (100, 600, obs2_path, *obs2_offset), (580, 850, obs3_path, *obs3_offset), (700, 80, obs3_path, *obs3_offset), (600, 350, obs3_path, *obs3_offset), (290, 400, obs3_path, *obs3_offset), (430, 650, obs4_path, *obs4_offset), (600, 600, obs2_path, *obs2_offset), ]
    create_level(targets, obstacles, 'level1.json')
