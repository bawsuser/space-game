from main import *

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
