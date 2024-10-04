import os
import json
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
# Ví dụ tạo level với 3 mục tiêu và 2 chướng ngại vật
if __name__ == '__main__':
    targets = [(100, 150, 'd'), (200, 250, 's'), (300, 650, 'p')]
    obstacles = [(500, 200, obs2_path, *obs2_offset)] 
    create_level(targets, obstacles, 'level1.json')
