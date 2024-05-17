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
        self.platform_list = None

    def update(self):
        initial_x = self.center_x
        initial_y = self.center_y
        
        self.center_x += self.change_x
        self.center_y += self.change_y
        self.change_y -= GRAVITY

        collisions = arcade.check_for_collision_with_list(self, self.platform_list)
        for platform in collisions:
            if self.change_y < 0:  # Только если падаем
                if self.bottom >= platform.top:
                    self.bottom = platform.top
                    self.change_y = 0
                    self.on_platform = True

        if self.left < 0:
            self.left = 0

        if self.bottom < 0:
            self.bottom = 0

        if self.change_y != 0:
            self.texture = arcade.load_texture("images/knight_1.png", mirrored=not self.facing_right)
        else:
            self.texture = arcade.load_texture("images/knight_0.png", mirrored=not self.facing_right)

        if self.triple_shoot and time.time() > self.triple_shoot_end_time:
            self.triple_shoot = False

class Platform(arcade.Sprite):
    def __init__(self, image, x, y, is_floor=False):
        super().__init__(image, 1)
        self.center_x = x
        self.center_y = y
        self.is_floor = is_floor

class Projectile(arcade.Sprite):
    def __init__(self, x, y, direction_x, direction_y=0):
        super().__init__("images/coin_0.png", 0.5)
        self.center_x = x
        self.center_y = y
        self.change_x = PROJECTILE_SPEED * direction_x
        self.change_y = PROJECTILE_SPEED * direction_y

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y
        if self.right < 0 or self.left > SCREEN_WIDTH or self.top < 0 or self.bottom > SCREEN_HEIGHT:
            self.kill()

class Enemy(arcade.Sprite):
    def __init__(self, image, x, y):
        super().__init__(image, 1)
        self.center_x = x
        self.center_y = y
        self.change_x = ENEMY_SPEED
        self.direction = 1  # 1 - вправо, -1 - влево

    def update(self):
        self.center_x += self.change_x * self.direction
        if self.left < 0 or self.right > SCREEN_WIDTH:
            self.direction *= -1

class Platformer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)
        self.player = None
        self.platform_list = None
        self.projectile_list = None
        self.enemy_list = None
        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.game_over = False
        self.fall_through = False

    def setup(self):
        self.player = Player()
        self.platform_list = arcade.SpriteList()
        self.projectile_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        self.player.platform_list = self.platform_list

        floor = Platform("images/platform_0.png", SCREEN_WIDTH // 2, 32, is_floor=True)
        self.platform_list.append(floor)
        for i in range(5):
            platform = Platform("images/platform_0.png", random.randint(50, SCREEN_WIDTH - 50), random.randint(100, 400))
            self.platform_list.append(platform)

        for i in range(3):
            enemy = Enemy("images/platform_1.png", random.randint(50, SCREEN_WIDTH - 50), random.randint(200, 400))
            self.enemy_list.append(enemy)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.platform_list, gravity_constant=GRAVITY)

    def on_draw(self):
        arcade.start_render()
        self.platform_list.draw()
        self.projectile_list.draw()
        self.enemy_list.draw()
        self.player.draw()

        if self.game_over:
            arcade.draw_text("Game Over", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, arcade.color.RED, 54, anchor_x="center")

    def update(self, delta_time):
        if not self.game_over:
            self.player.update()
            self.projectile_list.update()
            self.enemy_list.update()
            self.physics_engine.update()

            for projectile in self.projectile_list:
                if arcade.check_for_collision_with_list(projectile, self.enemy_list):
                    projectile.kill()

            if self.player.health <= 0:
                self.game_over = True

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
