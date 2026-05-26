from main import *
from BgMove import BgMove
import settings as _sett


class Menu:
    def __init__(self, texts, game_obj, disp):
        self.disp = disp
        self.texts = texts
        self.space = WIDTH//13
        self.max_height = self.space*(len(texts))
        self.option = 0
        self.alt = True
        self.opacity = 100
        self.bg = BgMove(self.disp)
        self.close_menu = False
        self.game_obj = game_obj

    def draw_menu(self):
        self.bg.run()
        rects = []
        style = get_font('Comic Sans MS', WIDTH//10)
        center_text = lambda x: (
                (WIDTH - rects[x].width)//2,
                x*self.space + (HEIGHT - self.max_height)//2)

        for i in range(len(self.texts)):
            text = style.render(self.texts[i], False, (0,0,255))
            rects.append(text.get_rect())
            if self.option != i:
                self.disp.blit(text, center_text(i))

        text_bg = style.render(self.texts[self.option], False, (255,255,0))
        text = style.render(self.texts[self.option], False, (255,255,255))
        text.set_alpha(self.opacity)
        self.disp.blit(text_bg, center_text(self.option))
        self.disp.blit(text, center_text(self.option))
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
        selected = self.texts[self.option]
        if selected == 'start':
            self.close_menu = True
        elif selected == 'quit':
            self.game_obj.close_game = True
            self.close_menu = True
        elif selected == 'settings':
            def on_close(new_disp):
                self.disp = new_disp
                self.bg = BgMove(new_disp)
            SettingsMenu(self.disp, on_close).run()

    def run(self):
        while not self.close_menu:
            self.control()
            self.draw_menu()
            pg.display.flip()
            clock.tick(FPS)


class SettingsMenu:
    def __init__(self, disp, on_close):
        """on_close(new_disp) called with recreated display when user leaves."""
        self.disp = disp
        self.on_close = on_close
        self.data = _sett.load()
        self.bg = BgMove(disp)
        self.option = 0
        self.closed = False

    def _options(self):
        fs = 'ON' if self.data['fullscreen'] else 'OFF'
        if self.data['fullscreen']:
            res_str = '(fullscreen)'
        else:
            w, h = _sett.RESOLUTIONS[self.data['res_index']]
            res_str = f'{w}x{h}'
        return [f'FULLSCREEN: {fs}', f'RESOLUTION: {res_str}', 'BACK']

    def control(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._back()
            elif event.type == pg.KEYDOWN:
                opts = self._options()
                if event.key == pg.K_w:
                    self.option = (self.option - 1) % len(opts)
                elif event.key == pg.K_s:
                    self.option = (self.option + 1) % len(opts)
                elif event.key in (pg.K_RETURN, pg.K_SPACE):
                    self._select()
                elif event.key == pg.K_ESCAPE:
                    self._back()

    def _select(self):
        opts = self._options()
        selected = opts[self.option]
        if 'FULLSCREEN' in selected:
            self.data['fullscreen'] = not self.data['fullscreen']
        elif 'RESOLUTION' in selected and not self.data['fullscreen']:
            self.data['res_index'] = (self.data['res_index'] + 1) % len(_sett.RESOLUTIONS)
        elif selected == 'BACK':
            self._back()

    def _back(self):
        _sett.save(self.data)
        new_disp = _sett.make_display(pg)
        self.on_close(new_disp)
        self.closed = True

    def draw(self):
        self.bg.run()
        title_font = get_font('Comic Sans MS', HEIGHT * 80 // 720)
        opt_font = get_font('Comic Sans MS', WIDTH // 14)
        opts = self._options()

        title = title_font.render('SETTINGS', False, (255, 255, 0))
        self.disp.blit(title, ((WIDTH - title.get_width()) // 2, HEIGHT // 8))

        space = HEIGHT // 6
        total_h = space * len(opts)
        start_y = (HEIGHT - total_h) // 2

        for i, opt in enumerate(opts):
            color = (255, 255, 0) if i == self.option else (0, 0, 255)
            surf = opt_font.render(opt, False, color)
            self.disp.blit(surf, ((WIDTH - surf.get_width()) // 2, start_y + i * space))

    def run(self):
        while not self.closed:
            self.control()
            if not self.closed:
                self.draw()
                pg.display.flip()
                clock.tick(FPS)
