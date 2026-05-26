from main import *

class Item(pg.sprite.Sprite):
    def __init__(self, img = "pixelart/speed2.png"):
        super().__init__()
        self.img = img
        self.image = pg.transform.scale(
            get_image(img), (WIDTH//10, WIDTH//10))
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
        self.start_time = time()
        self.max_radius = HEIGHT / 2
        self.max_lifetime = 1.0
        # HEIGHT × HEIGHT is enough — max_radius is HEIGHT/2 — the original used
        # WIDTH × WIDTH which allocated and filled ~3× more pixels per frame.
        size = HEIGHT
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        self._center = size // 2
        self._last_radius = -1
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def update(self):
        elapsed_time = time() - self.start_time
        if elapsed_time > self.max_lifetime:
            self.kill()
            return
        scale = (elapsed_time + 1) / 2
        current_radius = int(min(scale * self.max_radius, self.max_radius))

        # Only re-fill+redraw if the radius (in pixels) actually changed.
        if current_radius != self._last_radius:
            self.image.fill((0, 0, 0, 0))
            gfxdraw.filled_circle(
                self.image, self._center, self._center,
                current_radius, (255, 255, 255, 150))
            gfxdraw.aacircle(
                self.image, self._center, self._center,
                current_radius, (0, 0, 0))
            self._last_radius = current_radius
        self.rect = self.image.get_rect(center=self.player.rect.center)

