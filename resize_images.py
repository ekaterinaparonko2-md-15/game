from PIL import Image

# Функция для вырезания и изменения размера спрайтов
def crop_and_resize_sprites(image_path, coordinates, output_prefix, new_size):
    img = Image.open(image_path)
    for idx, (x, y, w, h) in enumerate(coordinates):
        cropped_img = img.crop((x, y, x + w, y + h))
        resized_img = cropped_img.resize(new_size, Image.NEAREST)
        resized_img.save(f'images/{output_prefix}_{idx}.png')

# Координаты для вырезания спрайтов
knight_coords = [
    (0, 0, 32, 32),  # IDLE
    (32, 0, 32, 32), # RUN 1
    (64, 0, 32, 32), # RUN 2
    (96, 0, 32, 32), # RUN 3
    (128, 0, 32, 32), # RUN 4
    (160, 0, 32, 32), # ROLL 1
    (192, 0, 32, 32), # ROLL 2
    (224, 0, 32, 32), # HIT 1
    (256, 0, 32, 32), # HIT 2
    (288, 0, 32, 32), # DEATH 1
    (320, 0, 32, 32), # DEATH 2
]

platform_coords = [
    (0, 0, 64, 16),  # Деревянная платформа
    (0, 16, 64, 16), # Каменная платформа
]

coin_coords = [
    (0, 0, 16, 16),  # Монета 1
    (16, 0, 16, 16), # Монета 2
    (32, 0, 16, 16), # Монета 3
    (48, 0, 16, 16), # Монета 4
    (64, 0, 16, 16), # Монета 5
    (80, 0, 16, 16), # Монета 6
    (96, 0, 16, 16), # Монета 7
    (112, 0, 16, 16), # Монета 8
]

# Новые координаты для врагов
slime_green_coords = [
    (0, 0, 16, 16),  # Slime Green 1
    (16, 0, 16, 16), # Slime Green 2
    (32, 0, 16, 16), # Slime Green 3
    (48, 0, 16, 16), # Slime Green 4
    (0, 16, 16, 16), # Slime Green 5
    (16, 16, 16, 16), # Slime Green 6
    (32, 16, 16, 16), # Slime Green 7
    (48, 16, 16, 16), # Slime Green 8
    (0, 32, 16, 16), # Slime Green 9
    (16, 32, 16, 16), # Slime Green 10
    (32, 32, 16, 16), # Slime Green 11
    (48, 32, 16, 16), # Slime Green 12
]

# Вырезание спрайтов и изменение их размера
crop_and_resize_sprites('images/knight.png', knight_coords, 'knight', (64, 64))
crop_and_resize_sprites('images/platforms.png', platform_coords, 'platform', (128, 32))
crop_and_resize_sprites('images/coin.png', coin_coords, 'coin', (32, 32))
crop_and_resize_sprites('images/slime_green.png', slime_green_coords, 'slime_green', (64, 64))
crop_and_resize_sprites('images/s1.png', [(0,0,14,15)], 's1', (64, 64))
crop_and_resize_sprites('images/s2.png', [(0,0,14,15)], 's2', (64, 64))
crop_and_resize_sprites('images/s3.png', [(0,0,14,15)], 's3', (64, 64))
crop_and_resize_sprites('images/s4.png', [(0,0,14,15)], 's4', (64, 64))
