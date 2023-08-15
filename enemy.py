from main import *
from random import choice
import math

class Enemy(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed, disp):
        super().__init__()
        ship_img = pg.transform.scale(
                pg.image.load(
                    "pixelart/enemy_ship_" + str(randint(1,4)) + ".png"), (WIDTH//10, WIDTH//10))
        self.orig = ship_img
        self.image = self.orig
        self.disp_rect = disp.get_rect()
        self.rect = self.orig.get_rect(center=self.disp_rect.center)
        self.health = 100

        # axis move attr
        self.speed = speed

        # angle move attr
        self.angle_increase = 0
        self.angle = 0

        # shoot attr
        self.shoot_d = 1
        self.shoot_t_old = 0
        self.shoot_t_now = self.shoot_d

        self.spawn_edge = choice(["top", "bottom", "left", "right"])

        if self.spawn_edge == "left":
            self.rect.x = -self.rect.width
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif self.spawn_edge == "right":
            self.speed = -self.speed
            self.rect.x = WIDTH
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif self.spawn_edge == "bottom":
            self.speed = -self.speed
            self.rect.y = HEIGHT
            self.rect.x = randint(0,WIDTH-self.rect.width)
        else:
            self.rect.y = -self.rect.height
            self.rect.x = randint(0,WIDTH-self.rect.width)

    def shoot_at_player_and_move(self, player_position):
        angle_to_player = math.atan2(
            player_position[0] - self.rect.centerx,
            player_position[1] - self.rect.centery
        )
        self.angle = math.degrees(angle_to_player) + 180
        laser = self.shoot_laser()
        if self.spawn_edge == "top" or self.spawn_edge == "bottom":
            self.rect.y += self.speed
        else:
            self.rect.x += self.speed

        return laser

    def shoot_laser(self):
        self.shoot_t_now = time()
        time_past = self.shoot_t_now - self.shoot_t_old
        laser = None
        if time_past >= self.shoot_d:
            laser = Laser(self.angle)
            laser.rect.centerx = self.rect.centerx
            laser.rect.bottom = self.rect.centery
            self.shoot_t_old = time()

        return laser

    def update(self):
        if self.angle <= -360 or self.angle >= 360:
            self.angle = 0

        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif WIDTH < self.rect.left:
            self.rect.right = 0
        elif self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif HEIGHT < self.rect.top:
            self.rect.bottom = 0

        self.angle += self.angle_increase
        self.image = pg.transform.rotate(self.orig, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


class Laser(pg.sprite.Sprite):
    def __init__(self, angle):
        super().__init__()
        
        sound_effect_channel = pg.mixer.Channel(1)
        sound_effect = pg.mixer.Sound("sounds/laser.mp3")
        sound_effect_channel.play(sound_effect)
        
        self.image = pg.transform.scale(
            pg.Surface((20, 20)), (WIDTH//100, WIDTH//100))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()

        # move attr
        self.angle = angle
        self.speed = WIDTH//80

    def update(self):
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
        elif self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

        if self.angle < 0:
            self.angle += 360

        self.rect.y -= int(self.speed*math.cos(math.radians(self.angle)))
        self.rect.x -= int(self.speed*math.sin(math.radians(self.angle)))

