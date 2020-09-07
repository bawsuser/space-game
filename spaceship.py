from random import randint, choice
from time import sleep, time
import pygame as pg
import math
import pygame.gfxdraw
 
class Player(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        ship_img = pg.transform.scale(pg.image.load("pixelart/space_ship.png"), (WIDTH//10, WIDTH//10))
        self.orig = ship_img
        self.image = self.orig
        self.disp_rect = disp.get_rect()
        self.rect = self.orig.get_rect(center=self.disp_rect.center)
        self.health = 100

        # axis move attr
        self.speed = speed
        self.x_increase = 0
        self.y_increase = 0

        #angle move attr
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
        if ((self.shoot == True) and
            (self.shoot_t_now - self.shoot_t_old >= self.shoot_d)):
            laser = Laser(self.angle)
            laser.rect.centerx = self.rect.centerx
            laser.rect.bottom = self.rect.centery
            self.shoot_t_old = time()
            return laser
        else:
            return None

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
        self.image = pg.transform.scale(
            pg.Surface([20, 20]), (WIDTH//100, WIDTH//100))
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
            

class Asteroid(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
        super().__init__()
        self.size = randint(7,9)
        x = WIDTH//self.size
        self.orig = pg.transform.scale(
            pg.image.load("pixelart/meteor.png"), (x,x)).convert_alpha()
        self.image = self.orig
        self.rect = self.orig.get_rect()

        # move attr
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
        if ((self.rect.y < -self.rect.height) or
            (self.rect.y > HEIGHT+self.rect.height) or
            (self.rect.x < -self.rect.width) or
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


class Menu:
    def __init__(self, texts):
        self.texts = texts
        self.space = 100
        self.max_height = self.space*(len(texts))
        self.option = 0
        self.alt = True
        self.opacity = 100
        self.bg = Bg_move()
        self.finished = False
        self.close_game = False

    def draw_menu(self):
        self.bg.run()
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
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close_game = True
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
        if self.texts[self.option] == self.texts[0]:
            self.finished = True
        if self.texts[self.option] == self.texts[1]:
            self.close_game = True
            self.finished = True

    def run(self):
        while not self.finished:
            self.control()
            self.draw_menu()
            pg.display.flip()
            clock.tick(FPS)
            
        return self.close_game


class Bg_move:
    def __init__(self):
        self.bg_ctr = -HEIGHT
        img = pg.image.load("pixelart/space.png").convert_alpha()
        self.bg = pg.transform.scale(img, (WIDTH, HEIGHT*2))
        
    def run(self):
        self.bg_ctr += 7
        disp.blit(self.bg, (0, self.bg_ctr-2*HEIGHT))
        disp.blit(self.bg, (0, self.bg_ctr))
        if self.bg_ctr >= HEIGHT:
            self.bg_ctr = -HEIGHT


class Powerup(pg.sprite.Sprite):
    def __init__(self, img = "pixelart/speed2.png"):
        super().__init__()
        self.img = img
        self.image = pg.transform.scale(
            pg.image.load(img), (WIDTH//10, WIDTH//10)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = randint(0,WIDTH -self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = WIDTH//100

    def update(self):
        self.rect.y += self.speed
        if self.rect.y < -self.rect.height or self.rect.y > HEIGHT:
            self.kill()      



class Shield(pg.sprite.Sprite):
    def __init__(self, player_obj):
        super().__init__()       
        self.player = player_obj
        circle_img = pg.Surface((WIDTH//5,WIDTH//5), pg.SRCALPHA)
        w = (circle_img.get_width() // 2)
        # transparency under 190 raises no collision bug
        pg.gfxdraw.filled_circle(circle_img, w, w, WIDTH//10, (255,255,255,190))
        self.image = circle_img 
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.centerx = self.player.rect.centerx
        self.rect.centery = self.player.rect.centery

    def kill_shield(self):
        self.kill()


class Game:
    def __init__(self):
        # timer attributes
        self.t_asteroid_was_spawned = 0
        self.time_speed2_col = 0
        self.time_shield_col = 0
       
        # some game objs
        self.player = Player(WIDTH//75, 5)
        self.bg = Bg_move()

        # sprite groups
        self.astroids_s = pg.sprite.Group()
        self.astroids_m = pg.sprite.Group()
        self.astroids_l = pg.sprite.Group()
        self.sprites = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.health_pu = pg.sprite.Group()
        self.shield_pu = pg.sprite.Group()
        self.speed2_pu = pg.sprite.Group()        

        self.shield = None
        self.score = 0
        self.asteroid_spawn_delay = 1
        self.sprites.add(self.player)
        self.close_game = False
        self.pu_list= [
            "pixelart/shield.png",
            "pixelart/health.png",
            "pixelart/speed2.png"
            ]

    def collisions(self):
        def hits_ship(group, damage):
            hits_ship = pg.sprite.spritecollide(
                self.player, group, True, pg.sprite.collide_mask)
            for hit in hits_ship:
                self.player.health -= damage

        def hits_meteor(group, points):
            hits_meteor = pg.sprite.groupcollide(
                self.lasers, group, True, pg.sprite.collide_mask)

            if self.shield != None:
                hits_shield = pg.sprite.spritecollide(
                    self.shield, group, True, pg.sprite.collide_mask)
                for hit in hits_shield:
                    self.score += points

            for hit in hits_meteor:
                self.score += points
            
        def hit_health_pu():
            hit_powerup = pg.sprite.spritecollide(
                self.player, self.health_pu, True, pg.sprite.collide_mask)

            if hit_powerup:
                if self.player.health + 10 > 100:
                    self.player.health = 100
                else:
                    self.player.health += 10
 
        def hit_shield_pu(rt = 10):
            hit_powerup = pg.sprite.spritecollide(
                self.player, self.shield_pu, True, pg.sprite.collide_mask)
        
            if hit_powerup and self.time_shield_col == 0:
                self.shield = Shield(self.player)
                self.sprites.add(self.shield)
                self.time_shield_col = time()

            if time() > time() - self.time_shield_col >= rt:
                self.shield.kill_shield()
                self.shield = None
                self.time_shield_col = 0

        def hit_speed2_pu(rt = 3):
            hit_powerup = pg.sprite.spritecollide(
                self.player, self.speed2_pu, True, pg.sprite.collide_mask)
        
            if hit_powerup and self.time_speed2_col == 0:
                self.player.shoot_d = self.player.shoot_d/2
                self.time_speed2_col = time()

            if time() > time() - self.time_speed2_col >= rt:
                self.time_speed2_col = 0
                self.player.shoot_d = self.player.shoot_d*2 


        hits_ship(self.astroids_s,5)
        hits_ship(self.astroids_m,10)
        hits_ship(self.astroids_l,15)
        hits_meteor(self.astroids_s,5)
        hits_meteor(self.astroids_m,10)
        hits_meteor(self.astroids_l,15)
        hit_health_pu()
        hit_shield_pu()
        hit_speed2_pu()

    def spawn_powerups(self):
        if randint(0,100) == 1:
            powerup = Powerup(choice(self.pu_list))
            self.sprites.add(powerup)
            if("health" in powerup.img):
                self.health_pu.add(powerup)
            elif("shield" in powerup.img):
                self.shield_pu.add(powerup)
            else:
                self.speed2_pu.add(powerup)
 
    def draw_hud(self):
        disp.blit(pg.font.SysFont('Comic Sans MS', 30).render(
            'HEALTH', False, (255,255,255)),(30,30))
        
        if 0 < self.player.health:
            pg.draw.rect(
                disp, (255,255,255), [30,55,(WIDTH//300)*self.player.health,40])

        score = pg.font.SysFont(
            'Comic Sans MS', 114).render(
                ("SCORE: " + str(self.score)),
                False,
                (255,255,255))

        rect = score.get_rect()
        disp.blit(score,(WIDTH-rect.width-30, 30))

    def game_over(self):
        img = pg.image.load("pixelart/space.png").convert_alpha()
        bg = pg.transform.scale(img, (WIDTH, HEIGHT*2))
        self.player.health = 100
        self.score = 0
        self.player.angle = 0
        self.player.rect = self.player.orig.get_rect(
            center=self.player.disp_rect.center)
        
        for i in range(250,0,-5):
            text = pg.font.SysFont('Comic Sans MS', 200).render(
                'GAME OVER', False, (255,255,255))
            text.set_alpha(i) 
            rect = text.get_rect()
            disp.blit(bg, (0, 0))
            disp.blit(text, ((WIDTH - rect.width)//2, (HEIGHT - rect.height)//2))
            pg.display.flip()
            sleep(0.03)

    def spawn_astroids(self, blob_size):
        li = list(range(-5,0)) + list(range(1,6))
        for i in range(blob_size):
            asteroid = Asteroid(WIDTH//randint(100,150), choice(li))
            self.sprites.add(asteroid)
            if asteroid.size == 7:
                self.astroids_l.add(asteroid)
            elif asteroid.size == 8:
                self.astroids_m.add(asteroid)
            else:
                self.astroids_s.add(asteroid)

    def run(self):
        self.close_game = Menu(["start", "quit"]).run()
        while not self.close_game:
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                        self.close_game = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.close_game = Menu(["resume", "quit"]).run()
              
            if self.player.health <= 0:
                self.game_over()
            
            if time() - self.t_asteroid_was_spawned >= self.asteroid_spawn_delay:
                self.spawn_astroids(1)
                self.t_asteroid_was_spawned = time()

            laser = self.player.shoot_laser()
            if laser != None:
                self.lasers.add(laser)

            self.player.control()    
            self.spawn_powerups()
            disp.fill((0,0,0))
            self.bg.run()     
            self.collisions()        
            self.lasers.update()
            self.sprites.update()         
            self.lasers.draw(disp)
            self.sprites.draw(disp)
            self.draw_hud()
            pg.display.flip()
            clock.tick(FPS)


FPS = 60
WIDTH = 1280
HEIGHT = 720
clock = pg.time.Clock()
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
Game().run()
pg.quit() 
