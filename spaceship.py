import pygame as pg

FPS = 60
WIDTH = 2560
HEIGHT = 1440
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])
img = pg.image.load("pixelart/space.png").convert_alpha()
bg = pg.transform.scale(img, (WIDTH, HEIGHT))
 
class Player(pg.sprite.Sprite):
    def __init__(self, speed, rot_speed):
        super().__init__()
        self.orig = pg.image.load("pixelart/space_ship.png")
        self.image = self.orig
        self.disp_rect = disp.get_rect()
        self.rect = self.orig.get_rect(center=self.disp_rect.center)
        self.speed = speed
        self.x_speed = 0
        self.y_speed = 0
        self.rot_speed = rot_speed
        self.angle_speed = 0
        self.angle = 0
        
    def control(self):
        for event in pg.event.get(): 
            if event.type == pg.QUIT: 
                return True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    self.angle_speed = self.rot_speed
                elif event.key == pg.K_d:
                    self.angle_speed = -self.rot_speed
                elif event.key == pg.K_LEFT:
                    self.x_speed = -self.speed
                elif event.key == pg.K_RIGHT:
                    self.x_speed = self.speed
                elif event.key == pg.K_UP:
                    self.y_speed = -self.speed
                elif event.key == pg.K_DOWN:
                    self.y_speed = self.speed
            elif event.type == pg.KEYUP:
                if (event.key == pg.K_LEFT or event.key == pg.K_RIGHT):
                    self.x_speed = 0
                elif (event.key == pg.K_UP or event.key == pg.K_DOWN):
                    self.y_speed = 0
                elif event.key == pg.K_a or event.key == pg.K_d:
                    self.angle_speed = 0
                    
        if self.angle <= -360 or self.angle >= 360:
            self.angle = 0

        if self.rect.right < 0:
            self.rect.left = WIDTH
        elif WIDTH < self.rect.left:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = HEIGHT
        elif HEIGHT < self.rect.top:
            self.rect.bottom = 0
            
        self.rect.centerx += self.x_speed
        self.rect.centery += self.y_speed
        self.angle += self.angle_speed
        self.image = pg.transform.rotate(self.orig, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        return False

 
player = Player(20, 5)
sprites = pg.sprite.Group()
sprites.add(player)
done = False
clock = pg.time.Clock()
while not done:
    done = player.control()
    disp.fill((0,0,0))
    disp.blit(bg, (0, 0))
    sprites.draw(disp)
    pg.display.flip()
    clock.tick(FPS)
 
pg.quit()
