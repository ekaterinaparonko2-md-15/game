import arcade
import random
import time

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Simple Platformer"
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
PLAYER_SCALING = 1
PROJECTILE_SPEED = 10
ENEMY_SPEED = 2
PLAYER_MAX_HEALTH = 5
VIEWPORT_MARGIN = 200
RIGHT_MARGIN = 400
FALL_THRU_SPEED = -5
TRIPLE_SHOOT_DURATION = 5  # Продолжительность стрельбы в три стороны (секунды)

""" 
Класс, представляющий игрока.
Отвечает за управление и обновление состояния игрока, включая передвижение, прыжки, стрельбу и здоровье.
"""
class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("images/knight_0.png", PLAYER_SCALING)
        self.center_x = 50
        self.center_y = 100
        self.change_x = 0
        self.change_y = 0
        self.jumping = False
        self.facing_right = True
        self.health = PLAYER_MAX_HEALTH
        self.on_platform = False
        self.triple_shoot = False
        self.triple_shoot_end_time = 0

    """
    Функция обновления состояния игрока.
    Обновляет позицию игрока, применяет гравитацию и проверяет столкновения.
    """
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_y -= GRAVITY

        if self.left < 0:
            self.left = 0

        if self.bottom < 0:
            self.bottom = 0

        if self.change_y != 0:
            self.texture = arcade.load_texture("images/knight_1.png", mirrored=not self.facing_right)
        else:
            self.texture = arcade.load_texture("images/knight_0.png", mirrored=not self.facing_right)

        # Отключение стрельбы в три стороны по истечении времени
        if self.triple_shoot and time.time() > self.triple_shoot_end_time:
            self.triple_shoot = False


""" 
Класс, представляющий платформу.
Отвечает за создание платформ и их свойства, такие как позиция и является ли платформа полом.
"""
class Platform(arcade.Sprite):
    def __init__(self, image, x, y, is_floor=False):
        super().__init__(image, 1)
        self.center_x = x
        self.center_y = y
        self.is_floor = is_floor


"""
Класс, представляющий снаряд.
Отвечает за создание и движение снарядов, выпущенных игроком.
"""
class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y=0):
        super().__init__("images/coin_0.png", 0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = PROJECTILE_SPEED * direction_x
        self.change_y = PROJECTILE_SPEED * direction_y


    """ 
    Функция обновления состояния снаряда.
    Обновляет позицию снаряда и удаляет его, если он выходит за пределы экрана.
    """
    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        view_left, view_right, view_bottom, view_top = arcade.get_viewport()
        if self.right < view_left or self.left > view_right or self.top < view_bottom or self.bottom > view_top:
            self.remove_from_sprite_lists()


"""
Класс, представляющий врага.
Отвечает за создание врагов, их движение и проверку столкновений с игроком.
"""
class Enemy(arcade.Sprite):
    def __init__(self, x, y, direction):
        super().__init__("images/slime_green_10.png", 1)
        self.center_x = x
        self.center_y = y
        self.change_x = ENEMY_SPEED * direction

    """ 
    Функция обновления состояния врага.
    Обновляет позицию врага и изменяет направление при столкновении с краями платформ.
    """
    def update(self):
        self.center_x += self.change_x
        view_left, view_right, view_bottom, view_top = arcade.get_viewport()
        if self.right < view_left or self.left > view_right:
            self.remove_from_sprite_lists()


""" 
Класс, представляющий игру.
Отвечает за настройку игры, обработку ввода от пользователя и обновление игрового состояния.
"""
class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player = None
        self.platform_list = None
        self.projectile_list = None
        self.enemy_list = None
        self.kills = 0
        self.game_over = False

        self.view_left = 0
        self.view_bottom = 0
        self.end_of_map = 0
        self.generated_x = 0
        self.fall_through = False
        self.cheat_activated = False

    """ 
    Функция настройки игры.
    Инициализирует игрока, платформы, снаряды, врагов и физический движок.
    """
    def setup(self):
        arcade.set_background_color(arcade.color.SKY_BLUE)
        self.player = Player()
        self.platform_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        # Создание начального пола
        for x in range(0, SCREEN_WIDTH, 64):
            platform = Platform("images/platform_0.png", x, 32, is_floor=True)
            self.platform_list.append(platform)

        # Создание случайных воздушных платформ
        self.create_random_platforms()

        # Добавление врагов и монет
        self.spawn_entities()

    def create_random_platforms(self):
        levels = 0  # Количество уровней платформ
        for level in range(1, levels + 3):
            num_platforms = random.randint(2, 5)  # Случайное количество платформ на уровне
            for _ in range(num_platforms):
                x = random.randint(self.generated_x, self.generated_x + SCREEN_WIDTH)
                y = random.randint(150, SCREEN_HEIGHT - 64)
                platform = Platform("images/platform_1.png", x, y)
                self.platform_list.append(platform)
        self.generated_x += SCREEN_WIDTH

    def create_floor(self):
        for x in range(self.generated_x, self.generated_x + SCREEN_WIDTH, 64):
            platform = Platform("images/platform_0.png", x, 32, is_floor=True)
            self.platform_list.append(platform)

    def spawn_entities(self, num_enemies=4):
        view_left, view_right, view_bottom, view_top = arcade.get_viewport()
        for _ in range(num_enemies):  # Генерация num_enemies врагов
            side = random.choice(["left", "right"])
            y = random.randint(50, SCREEN_HEIGHT - 50)
            direction = 1 if side == "left" else -1
            x = view_left if side == "left" else view_right
            enemy = Enemy(x, y, direction)
            self.enemy_list.append(enemy)

    """ 
    Функция обработки отрисовки.
    Отвечает за отрисовку всех игровых объектов и интерфейса.
    """
    def on_draw(self):
        arcade.start_render()
        self.platform_list.draw()
        self.player.draw()
        self.projectile_list.draw()
        self.enemy_list.draw()
        # Отрисовка здоровья
        self.draw_health()
        # Отрисовка количества убитых врагов
        self.draw_kills()
        # Отрисовка улучшений
        self.draw_power_ups()
        if self.game_over:
            self.draw_game_over_screen()

    def draw_health(self):
        health_text = f"HP: {self.player.health}"
        arcade.draw_text(health_text, 10 + self.view_left, SCREEN_HEIGHT - 20 + self.view_bottom, arcade.color.WHITE, 14)
        for i in range(self.player.health):
            arcade.draw_text("❤️", 60 + i * 20 + self.view_left, SCREEN_HEIGHT - 20 + self.view_bottom, arcade.color.RED, 14)

    def draw_kills(self):
        kills_text = f"Kills: {self.kills}"
        arcade.draw_text(kills_text, SCREEN_WIDTH - 100 + self.view_left, SCREEN_HEIGHT - 20 + self.view_bottom, arcade.color.WHITE, 14)

    def draw_power_ups(self):
        if self.player.triple_shoot:
            time_left = int(self.player.triple_shoot_end_time - time.time())
            if time_left > 0:
                power_up_text = f"Тройной выстрел: {time_left}"
                arcade.draw_text(power_up_text, 10 + self.view_left, SCREEN_HEIGHT - 40 + self.view_bottom, arcade.color.WHITE, 14)

    def draw_game_over_screen(self):
        arcade.draw_rectangle_filled(self.view_left + SCREEN_WIDTH // 2, self.view_bottom + SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK)
        arcade.draw_text("ТЫ УМЕР", self.view_left + SCREEN_WIDTH // 2, self.view_bottom + SCREEN_HEIGHT // 2 + 20, arcade.color.RED, 50, anchor_x="center")
        arcade.draw_text(f"Ты убил {self.kills} монстров", self.view_left + SCREEN_WIDTH // 2, self.view_bottom + SCREEN_HEIGHT // 2 - 20, arcade.color.RED, 20, anchor_x="center")

    """ 
    Функция обновления состояния игры.
    Отвечает за обновление всех игровых объектов и проверку условий конца игры.
    
    Параметры:
    delta_time (float): Время, прошедшее с последнего обновления.
    """
    def update(self, delta_time):
        if self.game_over:
            return

        self.player.update()
        self.projectile_list.update()
        self.enemy_list.update()

        # Проверка столкновений с платформами
        if not self.fall_through:
            platforms_hit = arcade.check_for_collision_with_list(self.player, self.platform_list)
            if platforms_hit:
                self.player.jumping = False
                self.player.change_y = 0
                self.player.on_platform = True
            else:
                self.player.on_platform = False

        # Проверка столкновений снарядов с врагами
        for projectile in self.projectile_list:
            hit_list = arcade.check_for_collision_with_list(projectile, self.enemy_list)
            if hit_list:
                projectile.remove_from_sprite_lists()
                for enemy in hit_list:
                    enemy.remove_from_sprite_lists()
                    self.kills += 1
                    # Включение стрельбы в три стороны при убийстве каждого 10-го врага
                    if self.kills % 10 == 0:
                        self.player.triple_shoot = True
                        self.player.triple_shoot_end_time = time.time() + TRIPLE_SHOOT_DURATION

        # Проверка столкновений игрока с врагами
        for enemy in self.enemy_list:
            if arcade.check_for_collision(self.player, enemy):
                enemy.remove_from_sprite_lists()
                self.player.health -= 1
                if self.player.health <= 0:
                    self.game_over = True

        # Спавн врагов через каждые несколько секунд
        if random.randint(1, 180) == 1:  # Увеличение интервала между спавном врагов
            self.spawn_entities(num_enemies=1)

        # Прокрутка мира
        self.scroll_viewport()

    def scroll_viewport(self):
        changed = False

        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player.left < left_boundary:
            self.view_left -= left_boundary - self.player.left
            changed = True

        right_boundary = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player.right > right_boundary:
            self.view_left += self.player.right - right_boundary
            changed = True

        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(self.view_left, SCREEN_WIDTH + self.view_left, self.view_bottom, SCREEN_HEIGHT + self.view_bottom)
            if self.view_left + SCREEN_WIDTH >= self.generated_x:
                self.create_floor()
                self.create_random_platforms()
                self.spawn_entities(num_enemies=2)

    """ 
    Функция обработки нажатия клавиш.
    Отвечает за обработку ввода от пользователя и выполнение соответствующих действий.
    
    Параметры:
    key (int): Код нажатой клавиши.
    modifiers (int): Модификаторы клавиш (например, Shift, Ctrl).
    """
    def on_key_press(self, key, modifiers):
        if self.game_over:
            return

        if key == arcade.key.UP:
            if self.player.on_platform:
                self.player.change_y = PLAYER_JUMP_SPEED
                self.player.jumping = True
                self.player.on_platform = False
        elif key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
            self.player.facing_right = False
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
            self.player.facing_right = True
        elif key == arcade.key.DOWN:
            if self.player.on_platform and not self.fall_through:
                platforms_hit = arcade.check_for_collision_with_list(self.player, self.platform_list)
                if platforms_hit:
                    for platform in platforms_hit:
                        if not platform.is_floor:
                            self.fall_through = True
                            self.player.change_y = FALL_THRU_SPEED
                            break
        elif key == arcade.key.SPACE:
            direction = 1 if self.player.facing_right else -1
            projectile = Projectile(self.player.center_x, self.player.center_y, direction)
            self.projectile_list.append(projectile)
            if self.player.triple_shoot:
                # Стрельба влево, вправо и вверх
                projectile_left = Projectile(self.player.center_x, self.player.center_y, -1)
                self.projectile_list.append(projectile_left)
                projectile_up = Projectile(self.player.center_x, self.player.center_y, 0, 1)
                self.projectile_list.append(projectile_up)
                projectile_right = Projectile(self.player.center_x, self.player.center_y, 1)
                self.projectile_list.append(projectile_right)
        elif key == arcade.key.KEY_1 and modifiers & arcade.key.MOD_CTRL:
            if self.player.triple_shoot:
                self.player.triple_shoot_end_time += 15
            else:
                self.player.triple_shoot = True
                self.player.triple_shoot_end_time = time.time() + 15

    """ 
    Функция обработки отпускания клавиш.
    Отвечает за остановку движения игрока при отпускании клавиш направления.
    
    Параметры:
    key (int): Код отпущенной клавиши.
    modifiers (int): Модификаторы клавиш (например, Shift, Ctrl).
    """
    def on_key_release(self, key, modifiers):
        if self.game_over:
            return

        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player.change_x = 0
        elif key == arcade.key.DOWN:
            self.fall_through = False

def main():
    window = Platformer()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
