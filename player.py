from main import *

class Player(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed, disp):
        super().__init__()
        ship_img = pg.transform.scale(
                pg.image.load(
                    "pixelart/space_ship.png"), (WIDTH//10, WIDTH//10))
        self.orig = ship_img
        self.image = self.orig
        self.disp_rect = disp.get_rect()
        self.rect = self.orig.get_rect(center=self.disp_rect.center)
        self.health = 100

        # axis move attr
        self.speed = speed
        self.x_increase = 0
        self.y_increase = 0

        # angle move attr
        self.angle_speed = angle_speed
        self.angle_increase = 0
        self.angle = 0

        # shoot attr
        self.shoot = False
        self.shoot_d = 0.2
        self.shoot_t_old = 0
        self.shoot_t_now = self.shoot_d

    def control(self):
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            self.angle_increase = self.angle_speed
        elif pressed[pg.K_RIGHT]:
            self.angle_increase = -self.angle_speed
        elif not pressed[pg.K_RIGHT] or not pressed[pg.K_LEFT]:
            self.angle_increase = 0

        if pressed[pg.K_a]:
            self.x_increase = -self.speed
        elif pressed[pg.K_d]:
            self.x_increase = self.speed
        else:
            self.x_increase = 0

        if pressed[pg.K_w]:
            self.y_increase = -self.speed
        elif pressed[pg.K_s]:
            self.y_increase = self.speed
        else:
            self.y_increase = 0

        if pressed[pg.K_SPACE]:
            self.shoot = True
        else:
            self.shoot = False

    def shoot_laser(self):
        self.shoot_t_now = time()
        time_past = self.shoot_t_now - self.shoot_t_old
        laser = None
        if self.shoot and time_past >= self.shoot_d:
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

        self.rect.centerx += self.x_increase
        self.rect.centery += self.y_increase
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
        self.speed = WIDTH//40

    def update(self):
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
        elif self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()

        if self.angle < 0:
            self.angle += 360

        self.rect.y -= int(self.speed*math.cos(math.radians(self.angle)))
        self.rect.x -= int(self.speed*math.sin(math.radians(self.angle)))

