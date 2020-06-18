import pygame as pg
import time

FPS = 60
WIDTH = 2560
HEIGHT = 1440
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
img = pg.image.load("pixelart/space.png").convert_alpha()
bg = pg.transform.scale(img, (WIDTH, HEIGHT))
 
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
        self.shoot_d = 0.3
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
                    
        self.t_now = time.time()
        if self.shoot == True and self.t_now-self.t_old >= self.shoot_d:
            laser = Laser()
            laser.rect.centerx = player.rect.centerx
            laser.rect.bottom = player.rect.centery
            sprites.add(laser)
            self.t_old = time.time()
                    
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
        return False


class Laser(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface([20, 20])
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.angle = player.angle
        self.speed = 120
 
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


player = Player(20, 5)
sprites = pg.sprite.Group()
sprites.add(player)
done = False
clock = pg.time.Clock()
while not done:
    done = player.control()
    disp.fill((0,0,0))
    disp.blit(bg, (0, 0))
    sprites.update()
    sprites.draw(disp)
    pg.display.flip()
    clock.tick(FPS)
 
pg.quit()
