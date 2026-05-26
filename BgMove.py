from main import *


class BgMove:
    def __init__(self, disp):
        self.disp = disp
        self.bg_ctr = -HEIGHT
        self.bg = pg.transform.scale(
            get_image("pixelart/space.png"), (WIDTH, HEIGHT*2))

    def run(self):
        self.bg_ctr += 7
        self.disp.blit(self.bg, (0, self.bg_ctr-2*HEIGHT))
        self.disp.blit(self.bg, (0, self.bg_ctr))
        if self.bg_ctr >= HEIGHT:
            self.bg_ctr = -HEIGHT
