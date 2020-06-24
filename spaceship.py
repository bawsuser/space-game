from random import randint
from random import choice
from time import time
import pygame as pg

FPS = 60
WIDTH = 2560
HEIGHT = 1440
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
img = pg.image.load("pixelart/space.png").convert_alpha()
bg = pg.transform.scale(img, (WIDTH, HEIGHT))
img_mir = pg.image.load("pixelart/space_mir.png").convert_alpha()
bg_mir = pg.transform.scale(img_mir, (WIDTH, HEIGHT))
 
class Player(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        self.orig = pg.image.load("pixelart/space_ship.png")
        self.image = self.orig
        self.disp_rect = disp.get_rect()
        self.rect = self.orig.get_rect(center=self.disp_rect.center)
        self.speed = speed
        self.x_increase = 0
        self.y_increase = 0
        self.angle_speed = angle_speed
        self.angle_increase = 0
        self.angle = 0
        self.shoot = False
        self.shoot_d = 0.2
        self.t_old = 0
        self.t_now = self.shoot_d
        
    def control(self):
        for event in pg.event.get(): 
            if event.type == pg.QUIT: 
                return True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    self.angle_increase = self.angle_speed
                elif event.key == pg.K_d:
                    self.angle_increase = -self.angle_speed
                elif event.key == pg.K_LEFT:
                    self.x_increase = -self.speed
                elif event.key == pg.K_RIGHT:
                    self.x_increase = self.speed
                elif event.key == pg.K_UP:
                    self.y_increase = -self.speed
                elif event.key == pg.K_DOWN:
                    self.y_increase = self.speed
                elif event.key == pg.K_SPACE:
                   self.shoot = True
            elif event.type == pg.KEYUP:
                if (event.key == pg.K_LEFT or event.key == pg.K_RIGHT):
                    self.x_increase = 0
                elif (event.key == pg.K_UP or event.key == pg.K_DOWN):
                    self.y_increase = 0
                elif event.key == pg.K_a or event.key == pg.K_d:
                    self.angle_increase = 0
                elif event.key == pg.K_SPACE:
                    self.shoot = False
        return False

    def update(self):            
        self.t_now = time()
        if self.shoot == True and self.t_now-self.t_old >= self.shoot_d:
            laser = Laser(self.angle)
            laser.rect.centerx = self.rect.centerx
            laser.rect.bottom = self.rect.centery
            sprites.add(laser)
            self.t_old = time()
                    
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
        self.image = pg.Surface([20, 20])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.angle = angle
        self.speed = 120
        lasers.add(self)
 
    def update(self):
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
        elif self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()
            
        if self.angle < 0:
            self.angle += 360
            
        if 0 <= self.angle <= 90:
            self.rect.y -= self.speed*(90-self.angle)/90 
            self.rect.x -= self.speed*self.angle/90
        elif 90 <= self.angle <= 180:
            self.rect.y += self.speed*(self.angle-90)/90 
            self.rect.x -= self.speed*(180-self.angle)/90
        elif 180 <= self.angle <= 270:
            self.rect.y += self.speed*(90-(self.angle-180))/90 
            self.rect.x += self.speed*(self.angle-180)/90
        elif 270 <= self.angle <= 360:
            self.rect.y -= self.speed*(self.angle-270)/90 
            self.rect.x += self.speed*(90-(self.angle-270))/90        


class Asteroid(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        self.orig = pg.image.load("pixelart/meteor.png").convert_alpha()
        self.image = self.orig
        self.rect = self.orig.get_rect()
        self.speed = speed
        self.angle_speed = angle_speed
        self.angle = 0
        self.r = randint(1,4)
        self.side_move = randint(-5,5)
        if 1 == self.r:
            self.rect.x = -self.rect.width
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif 2 == self.r:
            self.speed = -self.speed
            self.rect.x = WIDTH
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif 3 == self.r:
            self.speed = -self.speed
            self.rect.y = HEIGHT
            self.rect.x = randint(0,WIDTH-self.rect.width)
        else:
            self.rect.y = -self.rect.height
            self.rect.x = randint(0,WIDTH-self.rect.width)


    def update(self):
        if self.rect.y < -self.rect.height or self.rect.y > HEIGHT+self.rect.height:
            self.kill()
        elif self.rect.x < -self.rect.width or self.rect.x > WIDTH+self.rect.width:
            self.kill()
        
        if self.angle <= -360 or self.angle >= 360:
            self.angle = 0
            
        self.angle += self.angle_speed
        self.image = pg.transform.rotate(self.orig, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.r > 2:
            self.rect.y += self.speed
            self.rect.x += self.side_move
        else:
            self.rect.x += self.speed
            self.rect.y += self.side_move


def bg_move(bg_ctr):
    bg_ctr += 8
    disp.blit(bg, (0, bg_ctr))
    disp.blit(bg_mir, (0, bg_ctr-HEIGHT))
    disp.blit(bg, (0, bg_ctr-(HEIGHT)*2))
    if bg_ctr >= HEIGHT*2:
        bg_ctr = 0
    return bg_ctr


def spawn_astroids(spawn_delay):
    li = list(range(-5,0)) + list(range(1,6))
    for i in range(spawn_delay):
        asteroid = Asteroid(randint(5,10), choice(li))
        sprites.add(asteroid)
        astroids.add(asteroid)
        

player = Player(20, 5)
sprites = pg.sprite.Group()
astroids = pg.sprite.Group()
lasers = pg.sprite.Group()
sprites.add(player)
bg_ctr = 0
spawn_delay = 1
t_old = 0
t_now = 0
done = False
clock = pg.time.Clock()
while not done:
    done = player.control()
    disp.fill((0,0,0))
    bg_ctr = bg_move(bg_ctr)
    t_now = time()
    if t_now-t_old >= spawn_delay:
        spawn_astroids(1)
        t_old = time()
    pg.sprite.spritecollide(player, astroids, True, pg.sprite.collide_mask)
    pg.sprite.groupcollide(lasers, astroids, True, pg.sprite.collide_mask)
    sprites.update()
    sprites.draw(disp)
    pg.display.flip()
    clock.tick(FPS)
 
pg.quit()
