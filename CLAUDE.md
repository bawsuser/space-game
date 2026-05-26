# Space Game — CLAUDE.md

## Starten

```bash
/tmp/spacegame_venv/bin/python main.py
# oder nach pipenv install:
pipenv run python main.py
```

Einstiegspunkt ist immer `main.py` — **nicht** `game_loop.py` direkt aufrufen (funktioniert wegen des zirkulären Imports nicht).

---

## Projektstruktur

```
main.py          — Konstanten (WIDTH, HEIGHT, FPS), pg.init(), Asset-Cache-Helpers
game_loop.py     — Haupt-Game-Loop, class Game (Kollisionen, Spawning, HUD, Game-Over)
player.py        — class Player, class Laser
enemy.py         — class Enemy
asteroid.py      — class Asteroid
items.py         — class Item, class Shield, class Shockwave
BgMove.py        — scrollender Hintergrund
menu.py          — Start- und Pause-Menü
scoreboard.py    — Highscore-Eingabe und -Anzeige (SQLite)
scores.db        — SQLite-Datenbank für Highscores
pixelart/        — alle Sprite-Bilder
sounds/          — alle Soundeffekte + Musik
```

---

## Wichtige Eigenheit: Zirkulärer Import

Das Projekt nutzt einen absichtlichen zirkulären Import-Trick:

- `main.py` macht `from game_loop import *` (Zeile 9)
- `game_loop.py` macht `from main import *` (Zeile 1)
- Alle anderen Module machen ebenfalls `from main import *`

Das funktioniert **nur** wenn `python main.py` als Einstiegspunkt genutzt wird. Python lädt `main.py` dann zweimal: einmal als `__main__` und einmal als Modul `main`. Das Modul `main` wird vollständig geladen (inkl. Konstanten und Asset-Cache), bevor `game_loop.py` weitermacht. Klingt verrückt, funktioniert aber.

`disp` (das Display-Surface) wird am Ende von `game_loop.py` (Zeile 323) gesetzt, **bevor** `Game()` instanziiert wird.

---

## Asset-Cache (seit dieser Session)

In `main.py` gibt es drei Hilfsfunktionen die je Asset nur einmal laden:

```python
get_image(path)      # pg.image.load + convert_alpha, gecacht
get_sound(path)      # pg.mixer.Sound, gecacht
get_font(name, size) # pg.font.SysFont, gecacht
```

Alle Sprites und der Game-Loop nutzen diese — **niemals** direkt `pg.image.load()` / `pg.mixer.Sound()` / `pg.font.SysFont()` aufrufen, sonst kehrt das Ruckeln zurück.

---

## Bekannte technische Schulden / TODOs

### Architektur

- **Zirkulärer Import auflösen**: Konstanten (WIDTH, HEIGHT, FPS etc.) in eine eigene `config.py` auslagern. Dann braucht kein Modul mehr `from main import *`.
- **`disp` als Global**: Das Display-Surface wird in `game_loop.py` als Modul-Global gesetzt und von allen Klassen genutzt. Sauberer wäre es, es durchzureichen oder als Singleton zu kapseln.
- **`hasattr`/`setattr`/`delattr` ersetzen**: `shockshield`, `enemy`, `fourdirshoot`, `starttime`, `enemy_spawned_time`, `enemy_alive` werden mit `setattr` dynamisch gesetzt. Stattdessen saubere Klassen-Attribute mit Default `None` in `__init__` definieren.

### Bugs / Spiellogik

- **SQL-Injection in `scoreboard.py`**: `insert_name()` baut den SQL-String per String-Concatenation zusammen. Auf parameterisierte Queries umstellen: `c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (self.name, self.score))`.
- **Enemy-Laser-Kollision**: `spritecollide(self.enemy, self.lasers, False, ...)` — der Player-Laser wird bei Treffer nicht gekillt (`dokill=False`). Wahrscheinlich unbeabsichtigt.

### Performance (noch offen)

- **Asteroid-Rotation**: Asteroiden rotieren jeden Frame (`angle_speed` ist immer ≠ 0). Man könnte Rotationen auf feste Winkelschritte (z.B. 5°) einrasten, um gecachte `Surface`-Objekte wiederzuverwenden.
- **`pg.transform.scale` bei Asteroid-Spawn**: Jeder neue Asteroid skaliert das gecachte Bild neu. Die drei möglichen Größen (size 7/8/9) könnten vorab als fertige Surfaces gecacht werden.

### UX

- **Fenstergröße / Fullscreen**: Kein Menü für Auflösung oder Fullscreen (Kommentar in `main.py` Zeile 52 verweist darauf).
- **`Menu.behaviour()`**: Vergleicht Menü-Optionen über Index (`texts[option] == texts[0]`). Besser direkt den String prüfen (`"quit"`, `"start"` etc.) für Robustheit.

---

## Performance-Erkenntnisse dieser Session

Benchmark (headless, 500 Frames, kein FPS-Cap):
- **Vorher**: ~500 FPS-equivalent
- **Nachher**: ~850 FPS-equivalent (~70% schneller)

Hauptursachen des Ruckelns waren:
1. `pg.mixer.Sound("sounds/explosion.mp3")` bei **jeder** Kollision (Disk-I/O pro Frame)
2. `pg.font.SysFont(...)` 60× pro Sekunde im HUD
3. Pro Asteroid eine neue `pg.sprite.Group()` in der Kollisions-Schleife
4. `Shockwave`-Surface war 1280×1280px (jetzt 720×720)
5. `pg.transform.rotate` lief jedes Frame auch ohne Winkeländerung
