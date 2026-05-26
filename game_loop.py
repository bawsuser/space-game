#sudo apt-get install python3-pygame
from main import *
from asteroid import Asteroid
from menu import Menu
from BgMove import BgMove
from scoreboard import Scoreboard
from items import Item, Shield, Shockwave
from player import Player, Laser
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
                "pixelart/shockwave.png",
                "pixelart/4dirshoot.png"
                ]

        # enemy
        self.spawn_enemy = True

        self.last_4dir_shot_time = time()

        # pre-rendered/cached HUD assets (HEALTH label is static, score font reused)
        self._hud_health_label = get_font('Comic Sans MS', HEIGHT*30//720).render(
            'HEALTH', False, (255, 255, 255))
        self._hud_score_font = get_font('Comic Sans MS', HEIGHT*114//720)

    def collisions(self):
        damage_dict = {7: 15, 8: 10, 9: 5}
        def damage_points(size):
            return damage_dict[size]

        sound_effect_channel = pg.mixer.Channel(2)
        snd_explosion = get_sound("sounds/explosion.mp3")

        def hits_ship():
            for elem in pg.sprite.spritecollide(
                    self.player, self.astroids, True, pg.sprite.collide_mask):
                self.player.health -= damage_points(elem.size)
                sound_effect_channel.play(snd_explosion)

        def hits_meteor():
            for laser, asteroids_hit in pg.sprite.groupcollide(
                    self.lasers, self.astroids, True, True).items():
                for elem in asteroids_hit:
                    sound_effect_channel.play(snd_explosion)
                    self.score += damage_points(elem.size)

            shockshield = getattr(self, "shockshield", None)
            for shield in (self.shield, shockshield):
                if shield is None:
                    continue
                for elem in pg.sprite.spritecollide(
                        shield, self.astroids, True, pg.sprite.collide_mask):
                    sound_effect_channel.play(snd_explosion)
                    self.score += damage_points(elem.size)

        def hits_powerup():
            for elem in pg.sprite.spritecollide(
                    self.player, self.powerups, True, pg.sprite.collide_mask):
                string = elem.img
                if "shield" in string:
                    sound_effect_channel.play(get_sound("sounds/shield.mp3"))
                    if self.time_shield_col == 0:
                        self.shield = Shield(self.player)
                        self.sprites.add(self.shield)
                        self.time_shield_col = time()

                if "health" in string:
                    sound_effect_channel.play(get_sound("sounds/health.mp3"))
                    if self.player.health + 10 > 100:
                        self.player.health = 100
                    else:
                        self.player.health += 10

                if "speed2" in string:
                    sound_effect_channel.play(get_sound("sounds/speed2.mp3"))
                    if self.time_speed2_col == 0:
                        self.player.shoot_d = self.player.shoot_d/2
                        self.time_speed2_col = time()

                if "shockwave" in string:
                    setattr(self, "shockshield", Shockwave(self.player))
                    self.sprites.add(self.shockshield)
                    sound_effect_channel.play(get_sound("sounds/shockwave.mp3"))

                if "4dirshoot" in string:
                    setattr(self, "fourdirshoot", True)
                    setattr(self, "starttime", time())

            # Timer expirys belong outside the powerup loop so the shield/speed
            # buff actually expires even when no powerup is on screen.
            if self.time_shield_col != 0 and time() - self.time_shield_col >= 10:
                if self.shield is not None:
                    self.shield.kill_shield()
                self.shield = None
                self.time_shield_col = 0

            if self.time_speed2_col != 0 and time() - self.time_speed2_col >= 3:
                self.time_speed2_col = 0
                self.player.shoot_d = self.player.shoot_d*2

        def hits_coin():
            for _ in pg.sprite.spritecollide(
                    self.player, self.coins, True, pg.sprite.collide_mask):
                sound_effect_channel.play(get_sound("sounds/coin.mp3"))
                self.score += 1500

        def shield_hits_enemy_laser():
            if self.shield is not None:
                pg.sprite.spritecollide(
                    self.shield, self.enemy_lasers, True, pg.sprite.collide_mask)
            if hasattr(self, "shockshield"):
                pg.sprite.spritecollide(
                    self.shockshield, self.enemy_lasers, True, pg.sprite.collide_mask)

        def enemy_laser_hits_ship():
            for _ in pg.sprite.spritecollide(
                    self.player, self.enemy_lasers, True, pg.sprite.collide_mask):
                self.player.health -= 10

        def remove_expired_shockwave():
            if hasattr(self, "shockshield") and time() - self.shockshield.start_time >= self.shockshield.max_lifetime:
                self.shockshield.kill()
                delattr(self, "shockshield")

        hits_ship()
        hits_meteor()
        hits_powerup()
        hits_coin()
        shield_hits_enemy_laser()
        enemy_laser_hits_ship() # enemy uncomment for damage
        remove_expired_shockwave()

        def lasers(angle): 
            laser = Laser(angle)
            laser.rect.centerx = self.player.rect.centerx
            laser.rect.bottom = self.player.rect.centery
            self.lasers.add(laser)
            self.sprites.add(laser)

        if hasattr(self, "starttime") and time()-self.starttime <= 5:
            current_time = time()
            time_past = current_time - self.last_4dir_shot_time
            if hasattr(self, "fourdirshoot") and self.fourdirshoot == True and time_past >= 0.2:
                lasers(self.player.angle)
                lasers(self.player.angle+90)
                lasers(self.player.angle+180)
                lasers(self.player.angle+270)
                self.last_4dir_shot_time = current_time 
                # spawn 4 shoot with player coordinates, angle

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
        disp.blit(self._hud_health_label, (WIDTH*30//1280, HEIGHT*30//720))

        if self.player.health > 0:
            pg.draw.rect(
                disp,
                (255,255,255),
                [WIDTH*30//1280,HEIGHT*55//720,(WIDTH//300)*self.player.health,HEIGHT*40//720])

        score = self._hud_score_font.render(
            "SCORE: " + str(self.score), False, (255, 255, 255))
        rect = score.get_rect()
        disp.blit(score, (WIDTH-rect.width-30, 30))

    def enemy_spawn_and_logic(self):
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

    def game_over(self):
        bg = pg.transform.scale(get_image("pixelart/space.png"), (WIDTH, HEIGHT*2))
        self.asteroid_spawn_delay = 1
        self.player.health = 100
        self.player.angle = 0
        self.player.rect = self.player.orig.get_rect(
        center=self.player.disp_rect.center)
        for attr in ('coins', 'astroids', 'lasers', 'powerups', 'sprites'):
            getattr(self, attr).empty()
        self.sprites.add(self.player)

        text = get_font('Comic Sans MS', HEIGHT*200//720).render(
            'GAME OVER', False, (255, 255, 255))
        rect = text.get_rect()
        text_pos = ((WIDTH - rect.width)//2, (HEIGHT - rect.height)//2)
        for i in range(250, 0, -5):
            text.set_alpha(i)
            disp.blit(bg, (0, 0))
            disp.blit(text, text_pos)
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

            self.enemy_spawn_and_logic()
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
