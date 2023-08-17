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

