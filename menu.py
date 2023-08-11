from main import *
from BgMove import BgMove

class Menu:
    def __init__(self, texts, game_obj):
        self.texts = texts
        self.space = WIDTH//13
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
        style = pg.font.SysFont('Comic Sans MS', WIDTH//10)
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
