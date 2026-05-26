from main import *
from BgMove import BgMove

class Scoreboard:
    def __init__(self, score, disp):
        self.disp = disp
        self.name = ""
        self.score = score
        self.score_list = []
        self.bg = BgMove(self.disp)
        self.close_insert_name = False
        self.close_scoreboard = False

    def control_name(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.close_insert_name = True
                elif event.key == pg.K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) > 20:
                    pass
                else:
                    self.name += event.unicode

    def draw_name(self):
        self.bg.run()
        color = (255, 255, 255)

        # input request
        font = pg.font.Font(None, 100*HEIGHT//720)
        req_surface = font.render("YOUR NAME", True, color)
        w = req_surface.get_width()
        h = req_surface.get_height()
        self.disp.blit(req_surface, ((WIDTH - w)//2, (HEIGHT - h)//2 - int(h*0.8)))

        # input field
        font = pg.font.Font(None, 64*HEIGHT//720)
        name_surface = font.render(self.name, True, color)
        w = max(300, name_surface.get_width() + 10)
        h = max(64, name_surface.get_height() + 10)
        name_box = pg.Rect(
                (WIDTH - w)//2, (HEIGHT - h)//2 + int(h*0.8), 10, 10)
        name_box.w = w
        name_box.h = h
        self.disp.blit(
                name_surface,
                (name_box.x + 5*WIDTH//1280, name_box.y + 5*HEIGHT//720))
        pg.draw.rect(self.disp, color, name_box, 1)

    def edit_db_scores(self):
        def create_table():
            try:
                c.execute("""CREATE TABLE scores
                        (id INTEGER PRIMARY KEY, name, score)""")
            except sqlite3.OperationalError:
                pass

        def insert_name():
            c.execute("""INSERT INTO scores (name, score)
                      values('""" + self.name + """', """
                      + str(self.score) + """)""")


        def read_in_db():
            rows = c.execute("SELECT * FROM scores")
            self.score_list = []
            for row in enumerate(rows):
                if row[0] > 4:
                    c.execute("""DELETE FROM scores
                              WHERE id = (SELECT MIN(id) FROM scores
                              WHERE score = (SELECT MIN(score)
                              FROM scores))""")

            rows = c.execute("SELECT * FROM scores ORDER BY score DESC")
            for row in rows:
                name = row[1]
                score = row[2]
                self.score_list.append((name, score))



        db = sqlite3.connect("scores.db")
        c = db.cursor()
        create_table()
        insert_name()
        read_in_db()
        db.commit()
        c.close()

    def control_scoreboard(self):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    self.close_scoreboard = True

    def draw_board(self):
        self.bg.run()

        # headline
        head_style = pg.font.SysFont('Comic Sans MS', 120*HEIGHT//720)
        text = head_style.render("HIGHSCORES", False, (255, 255, 0))
        rect_h = text.get_rect()
        head_height = rect_h.height
        self.disp.blit(text, ((WIDTH - rect_h.width)//2, 50))

        # list
        space = 100*HEIGHT//720
        max_height = space*(len(self.score_list))
        rects = []
        style = pg.font.SysFont('Comic Sans MS', 100*HEIGHT//720)
        center_text = lambda x: (
                (WIDTH - rect_h.width)//2,
                x*space + head_height + (HEIGHT - max_height)//2)

        for i in range(len(self.score_list)):
            name = self.score_list[i][0]
            score = self.score_list[i][1]
            text = style.render(
                    str(i+1) + ". " + name + " "
                    + str(score) , False, (255,255,255))
            rect = text.get_rect()
            rects.append(rect)
            self.disp.blit(text, center_text(i))

    def run(self):
        while not self.close_insert_name:
            self.control_name()
            self.draw_name()
            pg.display.flip()
            clock.tick(FPS)

        self.edit_db_scores()

        while not self.close_scoreboard:
            self.control_scoreboard()
            self.draw_board()
            pg.display.flip()
            clock.tick(FPS)

