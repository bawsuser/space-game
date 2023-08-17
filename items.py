from main import *

class Item(pg.sprite.Sprite):
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


class Shockwave(pg.sprite.Sprite):
    def __init__(self, player_obj):
        super().__init__()
        self.player = player_obj
        self.start_time = time()  # Record the start time
        self.max_radius = WIDTH / 2  # Maximum radius reached within 3 seconds
        
        self.image = pg.Surface((WIDTH, WIDTH), pg.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        # Calculate the elapsed time
        elapsed_time = time() - self.start_time
        if elapsed_time >= 3:
            self.kill()
        else:
            # Calculate the exponential scale
            scale = math.log(elapsed_time + 1) / math.log(4)  # Exponential scale factor
            
            current_radius = scale * self.max_radius
            self.image.fill((0, 0, 0, 0))
            gfxdraw.filled_circle(
                self.image, self.rect.centerx - self.player.rect.centerx + WIDTH // 2,
                self.rect.centery - self.player.rect.centery + WIDTH // 2,
                int(current_radius), (255, 255, 255, 150))
            gfxdraw.aacircle(
                self.image, self.rect.centerx - self.player.rect.centerx + WIDTH // 2,
                self.rect.centery - self.player.rect.centery + WIDTH // 2,
                int(current_radius), (0, 0, 0))
            self.rect = self.image.get_rect(center=self.player.rect.center)

