from random import randint, choice
from time import sleep, time
import sqlite3
import math
from pygame import gfxdraw
import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, speed, angle_speed):
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

        if self.r == 1:
            self.rect.x = -self.rect.width
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif self.r == 2:
            self.speed = -self.speed
            self.rect.x = WIDTH
            self.rect.y = randint(0,HEIGHT-self.rect.height)
        elif self.r == 3:
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
    def __init__(self, texts, game_obj):
        self.texts = texts
        self.space = 100
        self.max_height = self.space*(len(texts))
        self.option = 0
        self.alt = True
        self.opacity = 100
        self.bg = BgMove()
        self.close_menu = False
        self.game_obj = game_obj

    def draw_menu(self):
        self.bg.run()
        rects = []
        style = pg.font.SysFont('Comic Sans MS', 100)
        center_text = lambda x: (
                (WIDTH - rects[x].width)//2,
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
        if self.alt:
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
                self.game_obj.close_game = True
                self.close_menu = True
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
            self.close_menu = True
        if self.texts[self.option] == self.texts[1]:
            self.game_obj.close_game = True
            self.close_menu = True

    def run(self):
        while not self.close_menu:
            self.control()
            self.draw_menu()
            pg.display.flip()
            clock.tick(FPS)


class BgMove:
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
        gfxdraw.filled_circle(
                circle_img, w, w, WIDTH//10, (255,255,255,150))
        # aacircle fixes collision bug
        gfxdraw.aacircle(circle_img, w, w, WIDTH//10, (0,0,0))
        self.image = circle_img
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.centerx = self.player.rect.centerx
        self.rect.centery = self.player.rect.centery

    def kill_shield(self):
        self.kill()


class Scoreboard:
    def __init__(self, score):
        self.name = ""
        self.score = score
        self.score_list = []
        self.bg = BgMove()
        self.close_insert_name = False
        self.close_scoreboard = False

    def control_name(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.close_insert_name = True
                elif event.key == pg.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) > 20:
                    pass
                else:
                    self.name += event.unicode

    def draw_name(self):
        self.bg.run()
        color = (255, 255, 255)

        # input request
        font = pg.font.Font(None, 100*HEIGHT//720)
        req_surface = font.render("YOUR NAME", True, color)
        w = req_surface.get_width()
        h = req_surface.get_height()
        disp.blit(req_surface, ((WIDTH - w)//2, (HEIGHT - h)//2 - int(h*0.8)))

        # input field
        font = pg.font.Font(None, 64*HEIGHT//720)
        name_surface = font.render(self.name, True, color)
        w = max(300, name_surface.get_width() + 10)
        h = max(64, name_surface.get_height() + 10)
        name_box = pg.Rect(
                (WIDTH - w)//2, (HEIGHT - h)//2 + int(h*0.8), 10, 10)
        name_box.w = w
        name_box.h = h
        disp.blit(
                name_surface,
                (name_box.x + 5*WIDTH//1280, name_box.y + 5*HEIGHT//720))
        pg.draw.rect(disp, color, name_box, 1)

    def edit_db_scores(self):
        def create_table():
            try:
                c.execute("""CREATE TABLE scores
                        (id INTEGER PRIMARY KEY, name, score)""")
            except sqlite3.OperationalError:
                pass

        def insert_name():
            c.execute("""INSERT INTO scores (name, score)
                      values('""" + self.name + """', """
                      + str(self.score) + """)""")


        def read_in_db():
            rows = c.execute("SELECT * FROM scores")
            self.score_list = []
            for row in enumerate(rows):
                if row[0] > 4:
                    c.execute("""DELETE FROM scores
                              WHERE id = (SELECT MIN(id) FROM scores
                              WHERE score = (SELECT MIN(score)
                              FROM scores))""")

            rows = c.execute("SELECT * FROM scores ORDER BY score DESC")
            for row in rows:
                name = row[1]
                score = row[2]
                self.score_list.append((name, score))



        db = sqlite3.connect("scores.db")
        c = db.cursor()
        create_table()
        insert_name()
        read_in_db()
        db.commit()
        c.close()

    def control_scoreboard(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.close_scoreboard = True

    def draw_board(self):
        self.bg.run()

        # headline
        head_style = pg.font.SysFont('Comic Sans MS', 120*HEIGHT//720)
        text = head_style.render("HIGHSCORES", False, (255, 255, 0))
        rect_h = text.get_rect()
        head_height = rect_h.height
        disp.blit(text, ((WIDTH - rect_h.width)//2, 50))

        # list
        space = 100*HEIGHT//720
        max_height = space*(len(self.score_list))
        rects = []
        style = pg.font.SysFont('Comic Sans MS', 100*HEIGHT//720)
        center_text = lambda x: (
                (WIDTH - rect_h.width)//2,
                x*space + head_height + (HEIGHT - max_height)//2)

        for i in range(len(self.score_list)):
            name = self.score_list[i][0]
            score = self.score_list[i][1]
            text = style.render(
                    str(i+1) + ". " + name + " "
                    + str(score) , False, (255,255,255))
            rect = text.get_rect()
            rects.append(rect)
            disp.blit(text, center_text(i))

    def run(self):
        while not self.close_insert_name:
            self.control_name()
            self.draw_name()
            pg.display.flip()
            clock.tick(FPS)

        self.edit_db_scores()

        while not self.close_scoreboard:
            self.control_scoreboard()
            self.draw_board()
            pg.display.flip()
            clock.tick(FPS)


class Game:
    def __init__(self):
        # timer attributes
        self.t_asteroid_was_spawned = 0
        self.time_speed2_col = 0
        self.time_shield_col = 0

        # some game objs
        self.player = Player(WIDTH//75, 5)
        self.bg = BgMove()

        # sprite groups
        self.astroids = pg.sprite.Group()
        self.sprites = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.powerups = pg.sprite.Group()

        self.shield = None
        self.score = 0
        self.old_score = 0
        self.asteroid_spawn_delay = 1
        self.sprites.add(self.player)
        self.close_game = False
        self.pu_list= [
                "pixelart/shield.png",
                "pixelart/health.png",
                "pixelart/speed2.png"
                ]

    def collisions(self):
        def damage_points(size):
            damage_dict = {
                7: 15,
                8: 10,
                9: 5
                }

            return damage_dict[size]

        def hits_ship():
            for elem in self.astroids:
                hits_ship = pg.sprite.collide_mask(
                        self.player, elem)

                if hits_ship is not None:
                    self.player.health -= damage_points(elem.size)
                    elem.kill()

        def hits_meteor():
            for elem in self.astroids:
                group = pg.sprite.Group()
                group.add(elem)
                hits_meteor = pg.sprite.groupcollide(
                        self.lasers, group, True, pg.sprite.collide_mask)

                if hits_meteor != {}:
                    self.score += damage_points(elem.size)
                    elem.kill()

            if self.shield is not None:
                for elem in self.astroids:
                    hits_shield = pg.sprite.collide_mask(
                        self.shield, elem)
                    if hits_shield is not None:
                        self.score += damage_points(elem.size)
                        elem.kill()

        def hits_powerup():
            for elem in self.powerups:
                group = pg.sprite.Group()
                group.add(elem)
                hit_powerup = pg.sprite.spritecollide(
                    self.player, group, False, pg.sprite.collide_mask)

                if hit_powerup != []:
                    string = elem.img
                    elem.kill()
                    if "shield" in string:
                        if self.time_shield_col == 0:
                            self.shield = Shield(self.player)
                            self.sprites.add(self.shield)
                            self.time_shield_col = time()

                    if "health" in string:
                        if self.player.health + 10 > 100:
                            self.player.health = 100
                        else:
                            self.player.health += 10

                    if "speed2" in string:
                        if self.time_speed2_col == 0:
                            self.player.shoot_d = self.player.shoot_d/2
                            self.time_speed2_col = time()


                if time() > time() - self.time_shield_col >= 10:
                    self.shield.kill_shield()
                    self.shield = None
                    self.time_shield_col = 0

                if time() > time() - self.time_speed2_col >= 3:
                    self.time_speed2_col = 0
                    self.player.shoot_d = self.player.shoot_d*2

        hits_ship()
        hits_meteor()
        hits_powerup()

    def spawn_powerups(self):
        if randint(0, PU_CHANCE) == 1:
            powerup = Powerup(choice(self.pu_list))
            self.sprites.add(powerup)
            self.powerups.add(powerup)

    def spawn_astroids(self, blob_size):
        angle_speed = list(range(-5,0)) + list(range(1,6))
        for _ in range(blob_size):
            asteroid = Asteroid(WIDTH//randint(100,150), choice(angle_speed))
            self.sprites.add(asteroid)
            self.astroids.add(asteroid)

    def draw_hud(self):
        disp.blit(pg.font.SysFont('Comic Sans MS', 30).render(
            'HEALTH', False, (255,255,255)),(30,30))

        if self.player.health > 0:
            pg.draw.rect(
                disp,
                (255,255,255),
                [30,55,(WIDTH//300)*self.player.health,40])

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
        self.asteroid_spawn_delay = 1
        self.player.health = 100
        self.player.angle = 0
        self.player.rect = self.player.orig.get_rect(
        center=self.player.disp_rect.center)
        for attr in ('astroids', 'lasers', 'powerups', 'sprites'):
            getattr(self, attr).empty()
        self.sprites.add(self.player)

        for i in range(250,0,-5):
            text = pg.font.SysFont('Comic Sans MS', 200).render(
                    'GAME OVER', False, (255,255,255))
            text.set_alpha(i)
            rect = text.get_rect()
            disp.blit(bg, (0, 0))
            disp.blit(
                    text,
                    ((WIDTH - rect.width)//2, (HEIGHT - rect.height)//2))

            pg.display.flip()
            sleep(0.03)

        Scoreboard(self.score).run()
        self.score = 0

    def run(self):
        start_menu = Menu(["start", "quit"], self)
        start_menu.run()
        while not self.close_game:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.close_game = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        Menu(["resume", "quit"], self).run()

            if self.player.health <= 0:
                self.game_over()
                start_menu.close_menu = False
                start_menu.run()

            if self.score > self.old_score + DIFFICULTY_SCORE_BARRIER:
                self.old_score = self.score
                fac = ASTEROID_SPAWN_FACTOR*ASTEROID_SPAWN_FACTOR
                self.asteroid_spawn_delay = self.asteroid_spawn_delay*fac

            past_time = time() - self.t_asteroid_was_spawned
            if past_time >= self.asteroid_spawn_delay:
                self.spawn_astroids(1)
                self.t_asteroid_was_spawned = time()

            laser = self.player.shoot_laser()
            if laser is not None:
                self.lasers.add(laser)
                self.sprites.add(laser)

            self.player.control()
            self.spawn_powerups()
            disp.fill((0,0,0))
            self.bg.run()
            self.collisions()
            self.sprites.update()
            self.sprites.draw(disp)
            self.draw_hud()
            pg.display.flip()
            clock.tick(FPS)


ASTEROID_SPAWN_FACTOR = 0.99
DIFFICULTY_SCORE_BARRIER = 100
PU_CHANCE = 300
FPS = 60
WIDTH = 1280
HEIGHT = 720
clock = pg.time.Clock()
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
Game().run()
pg.quit()
