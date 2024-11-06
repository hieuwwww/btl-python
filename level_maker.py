import os
import json
from ctypes import pydll

import pygame.transform


# Tạo level với số lượng mục tiêu và chướng ngại vật
# Thứ tự level, mục tiêu, chướng nghại vật, số mục tiêu để đạt 1/2/3 sao, tên file
def create_level(level, targets, obstacles, star_requirement, player, filename):
    # Kiểm tra nếu thư mục 'levels' không tồn tại và tạo mới
    if not os.path.exists('levels'):
        os.makedirs('levels')

    # Kiểm tra xem đường dẫn có phải là tệp không
    file_path = os.path.join('levels', filename)

    # Tạo tệp JSON và ghi dữ liệu vào đó
    level_data = {
        'level': level,
        'targets': targets,
        'obstacles': obstacles,
        'star_requirement': star_requirement,
        'player': player
    }
    with open(file_path, 'w') as f:
        json.dump(level_data, f)
    print(f'Level {filename} created!')


# đường dẫn đến hình ảnh và offset cho hitbox thật
obs1_path = 'assets/obstacle.png'
obs1_offset = (45, 52, 62, 114)  # width, height, x_offset, y_offset
obs2_path = 'assets/obstacle2.png'
obs2_offset = (40, 20, 53, 94)
obs3_path = 'assets/stone.png'
obs3_offset = (40, 40, 20, 20)
obs4_path = 'assets/house.png'
obs4_offset = (117, 90, 70, 125)

# Ví dụ tạo 4 level khác nhau
if __name__ == '__main__':
    # Ví dụ tạo level với 3 mục tiêu và 2 chướng ngại vật
    targets = [(100, 700, 's'), (200, 700, 's'), (600, 200, 's'), (650, 700, 's'), (200, 400, 'p'), (450, 400, 'p')]
    # obstacles = [(500, 200, obs2_image, *obs2_offset)]
    obstacles = [(200, 0, obs2_path, *obs2_offset), (200, 40, obs2_path, *obs2_offset), (200, 80, obs2_path, *obs2_offset), (200, 120, obs2_path, *obs2_offset), (200, 150, obs2_path, *obs2_offset),
                 (0, 250, obs2_path, *obs2_offset), (40, 250, obs2_path, *obs2_offset), (80, 250, obs2_path, *obs2_offset),
                 (300, 850, obs3_path, *obs3_offset), (300, 810, obs3_path, *obs3_offset), (300, 770, obs3_path, *obs3_offset), (300, 730, obs3_path, *obs3_offset), (300, 690, obs3_path, *obs3_offset), (300, 650, obs3_path, *obs3_offset), (300, 610, obs3_path, *obs3_offset),
                 (650, 500, obs4_path, *obs4_offset), (533, 500, obs4_path, *obs4_offset),
                 (300, 500, obs3_path, *obs3_offset), (345, 500, obs3_path, *obs3_offset), (390, 500, obs3_path, *obs3_offset), (345, 448, obs3_path, *obs3_offset),
                 (450, 700, obs1_path, *obs1_offset), (600, 600, obs1_path, *obs1_offset), (600, 800, obs1_path, *obs1_offset)
                 ]
    player = (100, 100)
    star_requirement = [3, 4, 6]
    level = 1
    create_level(level, targets, obstacles, star_requirement, player, 'level1.json')

    targets = [(600, 100, 's'), (120, 100, 's'), (350, 725, 's'), (600, 700, 's'), (120, 700, 's')]
    obstacles = [(400, 0, obs1_path, *obs1_offset), (400, 52, obs1_path, *obs1_offset), (400, 104, obs1_path, *obs1_offset),
                 (350, 156, obs4_path, *obs4_offset), (350, 246, obs4_path, *obs4_offset), (350, 336, obs4_path, *obs4_offset), (350, 426, obs4_path, *obs4_offset), (350, 516, obs4_path, *obs4_offset),
                 (475, 156, obs3_path, *obs3_offset), (475, 196, obs3_path, *obs3_offset), (475, 236, obs3_path, *obs3_offset), (475, 276, obs3_path, *obs3_offset), (475, 316, obs3_path, *obs3_offset), (475, 356, obs3_path, *obs3_offset), (475, 396, obs3_path, *obs3_offset), (475, 436, obs3_path, *obs3_offset), (475, 476, obs3_path, *obs3_offset), (475, 516, obs3_path, *obs3_offset), (475, 556, obs3_path, *obs3_offset), (475, 596, obs3_path, *obs3_offset),
                 (700, 156, obs3_path, *obs3_offset), (700, 196, obs3_path, *obs3_offset), (700, 236, obs3_path, *obs3_offset), (700, 276, obs3_path, *obs3_offset), (700, 316, obs3_path, *obs3_offset), (700, 356, obs3_path, *obs3_offset), (700, 396, obs3_path, *obs3_offset), (700, 436, obs3_path, *obs3_offset), (700, 476, obs3_path, *obs3_offset), (700, 516, obs3_path, *obs3_offset), (700, 556, obs3_path, *obs3_offset), (700, 596, obs3_path, *obs3_offset),
                 (275, 156, obs3_path, *obs3_offset), (275, 196, obs3_path, *obs3_offset), (275, 236, obs3_path, *obs3_offset), (275, 276, obs3_path, *obs3_offset), (275, 316, obs3_path, *obs3_offset), (275, 356, obs3_path, *obs3_offset), (275, 396, obs3_path, *obs3_offset), (275, 436, obs3_path, *obs3_offset), (275, 476, obs3_path, *obs3_offset), (275, 516, obs3_path, *obs3_offset), (275, 556, obs3_path, *obs3_offset), (275, 596, obs3_path, *obs3_offset),
                 (20, 156, obs3_path, *obs3_offset), (20, 196, obs3_path, *obs3_offset), (20, 236, obs3_path, *obs3_offset), (20, 276, obs3_path, *obs3_offset), (20, 316, obs3_path, *obs3_offset), (20, 356, obs3_path, *obs3_offset), (20, 396, obs3_path, *obs3_offset), (20, 436, obs3_path, *obs3_offset), (20, 476, obs3_path, *obs3_offset), (20, 516, obs3_path, *obs3_offset), (20, 556, obs3_path, *obs3_offset), (20, 596, obs3_path, *obs3_offset),
                ]
    star_requirement = [2, 3, 5]
    level = 2
    player = (450, 50)
    create_level(level, targets, obstacles, star_requirement, player, 'level2.json')

    targets = [(100, 150, 's'), (200, 250, 's'), (300, 650, 's')]
    obstacles = [(500, 200, obs2_path, *obs2_offset), (100, 300, obs3_path, *obs3_offset),
                 (200, 80, obs2_path, *obs2_offset), (100, 900, obs2_path, *obs2_offset),
                 (100, 600, obs2_path, *obs2_offset), (580, 850, obs3_path, *obs3_offset),
                 (700, 80, obs3_path, *obs3_offset), (600, 350, obs3_path, *obs3_offset),
                 (290, 400, obs3_path, *obs3_offset), (430, 650, obs4_path, *obs4_offset),
                 (600, 600, obs2_path, *obs2_offset)]
    star_requirement = [1, 2, 3]
    level = 3
    player = (400, 400)
    create_level(level, targets, obstacles, star_requirement, player, 'level3.json')

    targets = [(600, 100, 's'), (120, 100, 's'), (350, 725, 's'), (600, 700, 's'), (120, 700, 's')]
    obstacles = [(500, 10, obs1_path, *obs1_offset), (500, 62, obs1_path, *obs1_offset), (500, 112, obs1_path, *obs1_offset), (500, 162, obs1_path, *obs1_offset),
                 (20, 300, obs2_path, *obs2_offset), (60, 300, obs2_path, *obs2_offset), (100, 300, obs2_path, *obs2_offset), (140, 300, obs2_path, *obs2_offset), (180, 300, obs2_path, *obs2_offset), (220, 300, obs2_path, *obs2_offset), (260, 300, obs2_path, *obs2_offset),
                 (725, 300, obs2_path, *obs2_offset), (685, 300, obs2_path, *obs2_offset),
                 (600, 750, obs2_path, *obs2_offset), (450, 600,  obs2_path, *obs2_offset)
                 ]
    star_requirement = [2, 3, 5]
    level = 4
    player = (400 , 400)
    create_level(level, targets, obstacles, star_requirement, player, 'level4.json')

    targets = [(600, 100, 's'), (120, 100, 's'), (350, 725, 's'), (600, 700, 's'), (120, 700, 's')]
    obstacles = [(500, 10, obs1_path, *obs1_offset), (500, 62, obs1_path, *obs1_offset), (500, 112, obs1_path, *obs1_offset), (500, 162, obs1_path, *obs1_offset),
                 (20, 300, obs2_path, *obs2_offset), (60, 300, obs2_path, *obs2_offset), (100, 300, obs2_path, *obs2_offset), (140, 300, obs2_path, *obs2_offset), (180, 300, obs2_path, *obs2_offset), (220, 300, obs2_path, *obs2_offset), (260, 300, obs2_path, *obs2_offset),
                 (725, 300, obs2_path, *obs2_offset), (685, 300, obs2_path, *obs2_offset),
                 (600, 750, obs2_path, *obs2_offset), (450, 600,  obs2_path, *obs2_offset)
                 ]
    star_requirement = [2, 3, 5]
    level = 5
    player = (400 , 400)
    create_level(level, targets, obstacles, star_requirement, player, 'level5.json')

    targets = [(600, 100, 's'), (120, 100, 's'), (350, 725, 's'), (600, 700, 's'), (120, 700, 's')]
    obstacles = [(500, 10, obs1_path, *obs1_offset), (500, 62, obs1_path, *obs1_offset), (500, 112, obs1_path, *obs1_offset), (500, 162, obs1_path, *obs1_offset),
                 (20, 300, obs2_path, *obs2_offset), (60, 300, obs2_path, *obs2_offset), (100, 300, obs2_path, *obs2_offset), (140, 300, obs2_path, *obs2_offset), (180, 300, obs2_path, *obs2_offset), (220, 300, obs2_path, *obs2_offset), (260, 300, obs2_path, *obs2_offset),
                 (725, 300, obs2_path, *obs2_offset), (685, 300, obs2_path, *obs2_offset),
                 (600, 750, obs2_path, *obs2_offset), (450, 600,  obs2_path, *obs2_offset)
                 ]
    star_requirement = [2, 3, 5]
    level = 6
    player = (400 , 400)
    create_level(level, targets, obstacles, star_requirement, player, 'level6.json')

    targets = [(100, 700, 's'), (200, 700, 's'), (600, 200, 's'), (650, 700, 's'), (200, 400, 'p'), (450, 400, 'p')]
    # obstacles = [(500, 200, obs2_image, *obs2_offset)]
    obstacles = [(200, 0, obs2_path, *obs2_offset), (200, 40, obs2_path, *obs2_offset), (200, 80, obs2_path, *obs2_offset), (200, 120, obs2_path, *obs2_offset), (200, 150, obs2_path, *obs2_offset),
                 (0, 250, obs2_path, *obs2_offset), (40, 250, obs2_path, *obs2_offset), (80, 250, obs2_path, *obs2_offset),
                 (300, 850, obs3_path, *obs3_offset), (300, 810, obs3_path, *obs3_offset), (300, 770, obs3_path, *obs3_offset), (300, 730, obs3_path, *obs3_offset), (300, 690, obs3_path, *obs3_offset), (300, 650, obs3_path, *obs3_offset), (300, 610, obs3_path, *obs3_offset),
                 (650, 500, obs4_path, *obs4_offset), (533, 500, obs4_path, *obs4_offset),
                 (300, 500, obs3_path, *obs3_offset), (345, 500, obs3_path, *obs3_offset), (390, 500, obs3_path, *obs3_offset), (345, 448, obs3_path, *obs3_offset),
                 (450, 700, obs1_path, *obs1_offset), (600, 600, obs1_path, *obs1_offset), (600, 800, obs1_path, *obs1_offset)
                 ]
    player = (100, 100)
    star_requirement = [3, 4, 6]
    level = 7
    create_level(level, targets, obstacles, star_requirement, player, 'level7.json')

    targets = [(600, 100, 's'), (120, 100, 's'), (350, 725, 's'), (600, 700, 's'), (120, 700, 's')]
    obstacles = [(400, 0, obs1_path, *obs1_offset), (400, 52, obs1_path, *obs1_offset), (400, 104, obs1_path, *obs1_offset),
                 (350, 156, obs4_path, *obs4_offset), (350, 246, obs4_path, *obs4_offset), (350, 336, obs4_path, *obs4_offset), (350, 426, obs4_path, *obs4_offset), (350, 516, obs4_path, *obs4_offset),
                 (475, 156, obs3_path, *obs3_offset), (475, 196, obs3_path, *obs3_offset), (475, 236, obs3_path, *obs3_offset), (475, 276, obs3_path, *obs3_offset), (475, 316, obs3_path, *obs3_offset), (475, 356, obs3_path, *obs3_offset), (475, 396, obs3_path, *obs3_offset), (475, 436, obs3_path, *obs3_offset), (475, 476, obs3_path, *obs3_offset), (475, 516, obs3_path, *obs3_offset), (475, 556, obs3_path, *obs3_offset), (475, 596, obs3_path, *obs3_offset),
                 (700, 156, obs3_path, *obs3_offset), (700, 196, obs3_path, *obs3_offset), (700, 236, obs3_path, *obs3_offset), (700, 276, obs3_path, *obs3_offset), (700, 316, obs3_path, *obs3_offset), (700, 356, obs3_path, *obs3_offset), (700, 396, obs3_path, *obs3_offset), (700, 436, obs3_path, *obs3_offset), (700, 476, obs3_path, *obs3_offset), (700, 516, obs3_path, *obs3_offset), (700, 556, obs3_path, *obs3_offset), (700, 596, obs3_path, *obs3_offset),
                 (275, 156, obs3_path, *obs3_offset), (275, 196, obs3_path, *obs3_offset), (275, 236, obs3_path, *obs3_offset), (275, 276, obs3_path, *obs3_offset), (275, 316, obs3_path, *obs3_offset), (275, 356, obs3_path, *obs3_offset), (275, 396, obs3_path, *obs3_offset), (275, 436, obs3_path, *obs3_offset), (275, 476, obs3_path, *obs3_offset), (275, 516, obs3_path, *obs3_offset), (275, 556, obs3_path, *obs3_offset), (275, 596, obs3_path, *obs3_offset),
                 (20, 156, obs3_path, *obs3_offset), (20, 196, obs3_path, *obs3_offset), (20, 236, obs3_path, *obs3_offset), (20, 276, obs3_path, *obs3_offset), (20, 316, obs3_path, *obs3_offset), (20, 356, obs3_path, *obs3_offset), (20, 396, obs3_path, *obs3_offset), (20, 436, obs3_path, *obs3_offset), (20, 476, obs3_path, *obs3_offset), (20, 516, obs3_path, *obs3_offset), (20, 556, obs3_path, *obs3_offset), (20, 596, obs3_path, *obs3_offset),
                ]
    star_requirement = [2, 3, 5]
    level = 8
    player = (450, 50)
    create_level(level, targets, obstacles, star_requirement, player, 'level8.json')

    targets = [(100, 150, 's'), (200, 250, 's'), (300, 650, 's')]
    obstacles = [(500, 200, obs2_path, *obs2_offset), (100, 300, obs3_path, *obs3_offset),
                 (200, 80, obs2_path, *obs2_offset), (100, 900, obs2_path, *obs2_offset),
                 (100, 600, obs2_path, *obs2_offset), (580, 850, obs3_path, *obs3_offset),
                 (700, 80, obs3_path, *obs3_offset), (600, 350, obs3_path, *obs3_offset),
                 (290, 400, obs3_path, *obs3_offset), (430, 650, obs4_path, *obs4_offset),
                 (600, 600, obs2_path, *obs2_offset)]
    star_requirement = [1, 2, 3]
    level = 9
    player = (400, 400)
    create_level(level, targets, obstacles, star_requirement, player, 'level9.json')
