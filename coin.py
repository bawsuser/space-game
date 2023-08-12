from main import *

class Coin(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.img = "pixelart/coin.png"
        self.image = pg.transform.scale(
            pg.image.load(self.img), (WIDTH//10, WIDTH//10)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = randint(0,WIDTH -self.rect.width)
        self.rect.y = -self.rect.height
        self.speed = WIDTH//100

    def update(self):
        self.rect.y += self.speed
        if self.rect.y < -self.rect.height or self.rect.y > HEIGHT:
            self.kill()



