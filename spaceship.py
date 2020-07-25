from random import randint
from random import choice
from time import sleep
from time import time
import pygame as pg
import math



 
class Player(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        ship_img = pg.transform.scale(pg.image.load("pixelart/space_ship.png"), (WIDTH//10, WIDTH//10))
        self.orig = ship_img
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
        self.health = 100
        self.hits_ship = []
        self.hits_meteor = []
        self.score = 0
        
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

    def update(self):
        if self.health <= 0:
            game_over()
            self.health = 100
            self.score = 0
            self.angle = 0
            self.rect = self.orig.get_rect(center=self.disp_rect.center)
            
        
        self.hits_ship = pg.sprite.spritecollide(
            self, astroids, True, pg.sprite.collide_mask)
        self.hits_meteor = pg.sprite.groupcollide(
            lasers, astroids, True, pg.sprite.collide_mask)
        self.t_now = time()
        
        if self.shoot == True and self.t_now-self.t_old >= self.shoot_d:
            laser = Laser(self.angle)
            laser.rect.centerx = self.rect.centerx
            laser.rect.bottom = self.rect.centery
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

    def draw_hud(self):
        for hit in self.hits_ship:
            self.health -= 10

        if 0 < self.health:
            pg.draw.rect(
                disp, (255,255,255), [30,55,(WIDTH//300)*self.health,40])

        disp.blit(
            pg.font.SysFont('Comic Sans MS', 30).render(
                'HEALTH', False, (255,255,255)),(30,30))
        
        for hit in self.hits_meteor:
            self.score += 5

        text = pg.font.SysFont(
            'Comic Sans MS', 114).render(
                ("SCORE: " + str(self.score)),
                False,
                (255,255,255))

        rect = text.get_rect()

        disp.blit(text,(WIDTH-rect.width-30, 30))


class Laser(pg.sprite.Sprite):
    def __init__(self, angle):
        super().__init__()
        laser_img = pg.transform.scale(
            pg.Surface([20, 20]), (WIDTH//100, WIDTH//100))
        self.image = laser_img
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.angle = angle
        self.speed = WIDTH//40
        lasers.add(self)
 
    def update(self):
        if self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()
        elif self.rect.x < 0 or self.rect.x > WIDTH:
            self.kill()
            
        if self.angle < 0:
            self.angle += 360
            
        self.rect.y -= int(self.speed*math.cos(math.radians(self.angle)))
        self.rect.x -= int(self.speed*math.sin(math.radians(self.angle)))       


class Asteroid(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        x = WIDTH//randint(7,10)
        meteor_img = pg.transform.scale(
            pg.image.load("pixelart/meteor.png"), (x,x)).convert_alpha()
        self.orig = meteor_img
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
        if ((self.rect.y < -self.rect.height)
            or (self.rect.y > HEIGHT+self.rect.height)):
            self.kill()
        elif ((self.rect.x < -self.rect.width) or
              (self.rect.x > WIDTH+self.rect.width)):
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


class menu():
    def __init__(self, texts):
        self.texts = texts
        self.space = 100
        self.max_height = self.space*(len(texts))
        self.option = 0
        self.alt = True
        self.opacity = 100
        self.finished = False

    def draw_menu(self):
        bg_move()
        rects = []
        style = pg.font.SysFont('Comic Sans MS', 100)
        center_text = lambda x: ((WIDTH - rects[x].width)//2,
                                 x*self.space + (HEIGHT - self.max_height)//2)
    
        for i in range(len(self.texts)):
            text = style.render(self.texts[i], False, (0,0,255))
            rects.append(text.get_rect())
            if self.option != i:
                disp.blit(text, center_text(i))

        text_bg = style.render(self.texts[self.option], False, (255,255,0))
        text = style.render(self.texts[self.option], False, (255,255,255))
        text.set_alpha(self.opacity)       
        disp.blit(text_bg, center_text(self.option))
        disp.blit(text, center_text(self.option))
        blink_speed = 4
        if self.alt == True:
            self.opacity += blink_speed
            if self.opacity >= 250:
                self.alt = False
        else:
            self.opacity -= blink_speed        
            if self.opacity <= 100:
                self.alt = True

    def control(self):
        global done
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
                self.finished = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.option -= 1
                    if self.option < 0:
                        self.option = len(self.texts)-1
                elif event.key == pg.K_s:
                    self.option += 1
                    if self.option > len(self.texts)-1:
                        self.option = 0
                elif event.key == pg.K_RETURN:
                    self.behaviour()

    def behaviour(self):
        global done
        if self.texts[self.option] == self.texts[0]:
            self.finished = True
        if self.texts[self.option] == self.texts[1]:
            done = True
            self.finished = True

    def run(self):
        while not self.finished:
            self.control()
            self.draw_menu()
            pg.display.flip()
            clock.tick(FPS)


def bg_move():
    global bg_ctr
    bg_ctr += 7
    disp.blit(bg, (0, bg_ctr-2*HEIGHT))
    disp.blit(bg, (0, bg_ctr))
    if bg_ctr >= HEIGHT:
        bg_ctr = -HEIGHT


def game_over():
    for i in range(250,0,-5):
        text = pg.font.SysFont('Comic Sans MS', 200).render(
            'GAME OVER', False, (255,255,255))
        text.set_alpha(i) 
        rect = text.get_rect()
        disp.blit(bg, (0, 0))
        disp.blit(text, ((WIDTH - rect.width)//2, (HEIGHT - rect.height)//2))
        pg.display.flip()
        sleep(0.03)
    

def spawn_astroids(blob_size):
    li = list(range(-5,0)) + list(range(1,6))
    for i in range(blob_size):
        asteroid = Asteroid(WIDTH//randint(100,150), choice(li))
        sprites.add(asteroid)
        astroids.add(asteroid)


FPS = 60
WIDTH = 1280
HEIGHT = 720
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
img = pg.image.load("pixelart/space.png").convert_alpha()
bg = pg.transform.scale(img, (WIDTH, HEIGHT*2))
bg_ctr = -HEIGHT  
player = Player(WIDTH//75, 5)
sprites = pg.sprite.Group()
sprites.add(player)
astroids = pg.sprite.Group()
lasers = pg.sprite.Group()
spawn_delay = 1
t_old = 0
t_now = 0
done = False
clock = pg.time.Clock()

menu(["start", "quit"]).run()
while not done:
    for event in pg.event.get():
        if event.type == pg.QUIT: 
                done = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                menu(["resume", "quit"]).run()
               
    player.control()
    disp.fill((0,0,0))
    bg_move()
    t_now = time()
    
    if t_now-t_old >= spawn_delay:
        spawn_astroids(1)
        t_old = time()
        
    lasers.update()
    sprites.update()
    lasers.draw(disp)
    sprites.draw(disp)
    player.draw_hud()        
    pg.display.flip()
    clock.tick(FPS)
 
pg.quit()
