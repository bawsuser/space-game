#sudo apt-get install python3-pygame
from main import *
from asteroid import Asteroid
from menu import Menu
from BgMove import BgMove
from scoreboard import Scoreboard
from items import Item, Shield, Shockwave
from player import Player
from enemy import Enemy


class Game:
    def __init__(self):
        # timer attributes
        self.t_asteroid_was_spawned = 0
        self.time_speed2_col = 0
        self.time_shield_col = 0

        # some game objs
        self.player = Player(WIDTH//75, 5, disp)
        self.bg = BgMove(disp)

        # sprite groups
        self.astroids = pg.sprite.Group()
        self.sprites = pg.sprite.Group()
        self.lasers = pg.sprite.Group()
        self.enemy_lasers = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.coins = pg.sprite.Group()

        self.shield = None
        self.score = 0
        self.old_score = 0
        self.asteroid_spawn_delay = 1
        self.sprites.add(self.player)
        self.close_game = False
        self.pu_list= [
                "pixelart/shield.png",
                "pixelart/health.png",
                "pixelart/speed2.png",
                "pixelart/shockwave.png"
                ]

        # enemy
        self.spawn_enemy = True

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
                    sound_effect = pg.mixer.Sound("sounds/explosion.mp3")
                    sound_effect_channel.play(sound_effect)
                    
                    elem.kill()

        def hits_meteor():
            def shields(shield):
                if shield is not None:
                    for elem in self.astroids:
                        hits_shield = pg.sprite.collide_mask(
                            shield, elem)
                        if hits_shield is not None:
                            sound_effect = pg.mixer.Sound("sounds/explosion.mp3")
                            sound_effect_channel.play(sound_effect)
                            
                            self.score += damage_points(elem.size)
                            elem.kill()
                            
            for elem in self.astroids:
                group = pg.sprite.Group()
                group.add(elem)
                hits_meteor = pg.sprite.groupcollide(
                        self.lasers, group, True, pg.sprite.collide_mask)

                if hits_meteor != {}:
                    sound_effect = pg.mixer.Sound("sounds/explosion.mp3")
                    sound_effect_channel.play(sound_effect)
                    
                    self.score += damage_points(elem.size)
                    elem.kill()
                    
            shields(self.shield)
            if hasattr(self, "shockshield"):
                shields(self.shockshield)



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
                        sound_effect = pg.mixer.Sound("sounds/shield.mp3")
                        sound_effect_channel.play(sound_effect)
                        
                        if self.time_shield_col == 0:
                        
                            self.shield = Shield(self.player)
                            self.sprites.add(self.shield)
                            self.time_shield_col = time()

                    if "health" in string:
                        sound_effect = pg.mixer.Sound("sounds/health.mp3")
                        sound_effect_channel.play(sound_effect)

                        if self.player.health + 10 > 100:
                            self.player.health = 100
                        else:
                            self.player.health += 10

                    if "speed2" in string:
                        sound_effect = pg.mixer.Sound("sounds/speed2.mp3")
                        sound_effect_channel.play(sound_effect)
                        
                        if self.time_speed2_col == 0:
                            self.player.shoot_d = self.player.shoot_d/2
                            self.time_speed2_col = time()

                    if "shockwave" in string:
                        setattr(self, "shockshield", Shockwave(self.player))
                        self.sprites.add(self.shockshield)
                        sound_effect = pg.mixer.Sound("sounds/shockwave.mp3")
                        sound_effect_channel.play(sound_effect)
                        pass

                if time() > time() - self.time_shield_col >= 10:
                    self.shield.kill_shield()
                    self.shield = None
                    self.time_shield_col = 0

                if time() > time() - self.time_speed2_col >= 3:
                    self.time_speed2_col = 0
                    self.player.shoot_d = self.player.shoot_d*2

        def hits_coin():
            for elem in self.coins:
                group = pg.sprite.Group()
                group.add(elem)
                hits_coin = pg.sprite.spritecollide(
                    self.player, group, False, pg.sprite.collide_mask)

                if hits_coin != []:
                    sound_effect = pg.mixer.Sound("sounds/coin.mp3")
                    sound_effect_channel.play(sound_effect)
                    
                    self.score += 1500
                    elem.kill()

        def shield_hits_enemy_laser():
            if self.shield is not None:
                for elem in self.enemy_lasers:
                    hits_shield = pg.sprite.collide_mask(
                        self.shield, elem)
                    if hits_shield is not None:
                        elem.kill()
                        
            if hasattr(self, "shockshield"):
                for elem in self.enemy_lasers:
                    hits_shield = pg.sprite.collide_mask(
                        self.shockshield, elem)
                    if hits_shield is not None:
                        elem.kill()
                        
        
        def enemy_laser_hits_ship():
            for elem in self.enemy_lasers:
                hits_ship = pg.sprite.collide_mask(
                        self.player, elem)

                if hits_ship is not None:
                    self.player.health -= 10
                    elem.kill()

        def remove_expired_shockwave():
            if hasattr(self, "shockshield") and time() - self.shockshield.start_time >= self.shockshield.max_lifetime:
                self.shockshield.kill()
                delattr(self, "shockshield")
            
        sound_effect_channel = pg.mixer.Channel(2)
        hits_ship()
        hits_meteor()
        hits_powerup()
        hits_coin()
        shield_hits_enemy_laser()
        enemy_laser_hits_ship() # enemy uncomment for damage
        remove_expired_shockwave()

    def spawn_powerups(self):
        if randint(0, PU_CHANCE) == 1:
            powerup = Item(choice(self.pu_list))
            self.sprites.add(powerup)
            self.powerups.add(powerup)

    def spawn_coins(self):
        if randint(0, COIN_CHANCE) == 1:
            coin = Item("pixelart/coin.png")
            self.sprites.add(coin)
            self.coins.add(coin)

    def spawn_astroids(self, blob_size):
        angle_speed = list(range(-5,0)) + list(range(1,6))
        for _ in range(blob_size):
            asteroid = Asteroid(WIDTH//randint(100,150), choice(angle_speed))
            self.sprites.add(asteroid)
            self.astroids.add(asteroid)

    def draw_hud(self):
        disp.blit(pg.font.SysFont('Comic Sans MS', HEIGHT*30//720).render(
            'HEALTH', False, (255,255,255)),(WIDTH*30//1280,HEIGHT*30//720))

        if self.player.health > 0:
            pg.draw.rect(
                disp,
                (255,255,255),
                [WIDTH*30//1280,HEIGHT*55//720,(WIDTH//300)*self.player.health,HEIGHT*40//720])

        score = pg.font.SysFont(
            'Comic Sans MS', HEIGHT*114//720).render(
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
        for attr in ('coins', 'astroids', 'lasers', 'powerups', 'sprites'):
            getattr(self, attr).empty()
        self.sprites.add(self.player)

        for i in range(250,0,-5):
            text = pg.font.SysFont('Comic Sans MS', HEIGHT*200//720).render(
                    'GAME OVER', False, (255,255,255))
            text.set_alpha(i)
            rect = text.get_rect()
            disp.blit(bg, (0, 0))
            disp.blit(
                    text,
                    ((WIDTH - rect.width)//2, (HEIGHT - rect.height)//2))

            pg.display.flip()
            sleep(0.03)

        Scoreboard(self.score, disp).run()
        self.spawn_enemy = True
        self.score = 0

    def run(self):
        start_menu = Menu(["start", "quit"], self, disp)
        start_menu.run()
       
        music_file = "sounds/synth.mp3"
        pg.mixer.music.load(music_file)
        pg.mixer.music.play(-1, randint(1,7200), 2000)
        
        while not self.close_game:    
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.close_game = True
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        pg.mixer.music.pause()
                        Menu(["resume", "quit"], self, disp).run()
                        
            pg.mixer.music.unpause()
            if self.player.health <= 0:
                pg.mixer.music.stop()
                self.game_over()
                start_menu.close_menu = False
                start_menu.run()
                pg.mixer.music.play(-1, randint(1,7200), 2000)

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

            ###############
            # ENEMY SECTION
            ###############
                    
            if self.spawn_enemy:
                setattr(self, "enemy_spawned_time", time())
                setattr(self, "enemy", Enemy(WIDTH//400, 5, disp))
                self.sprites.add(self.enemy)
                self.spawn_enemy = False
                setattr(self, "enemy_alive", True)
            
            # if enemy shoot kill obj => self.spawn_enemy = True
            if self.enemy_alive:
                enemy_laser = self.enemy.shoot_at_player_and_move(self.player.rect.center)
                if enemy_laser:
                    self.enemy_lasers.add(enemy_laser)
                    # Add enemy laser to sprites, ensuring it's drawn beneath the enemy
                    self.sprites.remove(self.enemy)  # Remove enemy from sprites temporarily
                    self.sprites.add(enemy_laser)
                    self.sprites.add(self.enemy)  # Add enemy back to ensure correct order

                if pg.sprite.spritecollide(self.enemy, self.lasers, False, pg.sprite.collide_mask):
                    self.enemy_alive = False
                    self.enemy.kill()
                if hasattr(self, "shockshield") and pg.sprite.collide_mask(self.enemy, self.shockshield):
                    self.enemy_alive = False
                    self.enemy.kill()
                        
            if (28//randint(2,4)) <= (time() - self.enemy_spawned_time) and not self.enemy_alive:
                self.spawn_enemy = True
                del self.enemy_spawned_time

            ###############
            # ENEMY SECTION
            ###############
            
            # self.player.health = 100 # usefull dont forget comment out
            self.player.control()
            self.spawn_powerups()
            self.spawn_coins()
            disp.fill((0,0,0))
            self.bg.run()
            self.collisions()
            self.sprites.update()
            self.sprites.draw(disp)
            self.draw_hud()
            pg.display.flip()
            clock.tick(FPS)
        

disp = pg.display.set_mode([WIDTH, HEIGHT])   
Game().run()
pg.quit()
