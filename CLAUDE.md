# Space Game — CLAUDE.md

## Starten

```bash
# Nach install.sh (einmalig ausführen):
bash install.sh
source ~/.bashrc
spacegame        # von überall startbar

# Oder direkt:
.venv/bin/python main.py
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
menu.py          — class Menu, class SettingsMenu
scoreboard.py    — Highscore-Eingabe und -Anzeige (SQLite)
settings.py      — load/save settings.json, Display-Erstellung, Auto-Detection
install.sh       — idempotenter Installer (venv + spacegame-Alias)
settings.json    — gespeicherte Nutzereinstellungen (fullscreen, res_index)
scores.db        — SQLite-Datenbank für Highscores
pixelart/        — alle Sprite-Bilder
sounds/          — alle Soundeffekte + Musik
.venv/           — Python-Virtualenv (nicht im Repo, per .gitignore)
```

---

## Wichtige Eigenheit: Zirkulärer Import

Das Projekt nutzt einen absichtlichen zirkulären Import-Trick:

- `main.py` macht `from game_loop import *` (Zeile 9)
- `game_loop.py` macht `from main import *` (Zeile 1)
- Alle anderen Module machen ebenfalls `from main import *`

Das funktioniert **nur** wenn `python main.py` als Einstiegspunkt genutzt wird. Python lädt `main.py` dann zweimal: einmal als `__main__` und einmal als Modul `main`. Das Modul `main` wird vollständig geladen (inkl. Konstanten und Asset-Cache), bevor `game_loop.py` weitermacht.

`disp` (das Display-Surface) wird am Ende von `game_loop.py` gesetzt, **bevor** `Game()` instanziiert wird.

---

## Asset-Cache

In `main.py` gibt es drei Hilfsfunktionen die je Asset nur einmal laden:

```python
get_image(path)      # pg.image.load + convert_alpha, gecacht
get_sound(path)      # pg.mixer.Sound, gecacht
get_font(name, size) # pg.font.SysFont, gecacht
```

**Niemals** direkt `pg.image.load()` / `pg.mixer.Sound()` / `pg.font.SysFont()` aufrufen — sonst kehrt das Ruckeln zurück (Disk-I/O pro Frame).

---

## Display & Settings (`settings.py`)

Auflösung und Fullscreen werden in `settings.json` gespeichert.

```python
RESOLUTIONS = [
    (1280,  720),   # HD
    (1600,  900),   # HD+
    (1920, 1080),   # Full HD
    (2560, 1440),   # QHD
    (3840, 2160),   # 4K UHD
]
```

**Erster Start (kein `settings.json`)**: `pg.display.get_desktop_sizes()` erkennt die native Monitorauflösung automatisch und wählt den besten passenden Eintrag (max. 4K).

**Display-Erstellung** nutzt immer `pg.SCALED`:
- Fullscreen: `set_mode([w, h], FULLSCREEN | SCALED)` — rendert bei gewählter Auflösung, füllt den Bildschirm
- Windowed: `set_mode([w, h], SCALED)` — Fenster in gewählter Größe

`pg.SCALED` bedeutet: die Spiellogik arbeitet immer auf der gewählten Auflösung, die GPU skaliert transparent.

**Settings-Menü**: Im Startmenü → `settings` → Fullscreen-Toggle gilt sofort, Auflösungsänderung gilt beim nächsten Start (Hinweis wird eingeblendet).

---

## pygame-ce statt pygame

Das Projekt nutzt **pygame-ce** (Community Edition) statt dem Original-pygame:

```bash
pip install pygame-ce   # nicht: pip install pygame
```

pygame-ce ist ein Drop-in-Ersatz (`import pygame` bleibt gleich) mit GPU-beschleunigtem Blitting via SDL2 — wichtig für gute Performance bei höheren Auflösungen wie 4K. Kein Code musste für den Wechsel geändert werden.

---

## Bekannte technische Schulden / TODOs

### Architektur

- **Zirkulärer Import auflösen**: Konstanten (WIDTH, HEIGHT, FPS etc.) in eine eigene `config.py` auslagern. Dann braucht kein Modul mehr `from main import *`. Würde auch dynamische Auflösungsänderung ohne Neustart ermöglichen.
- **`disp` als Global**: Das Display-Surface wird in `game_loop.py` als Modul-Global gesetzt. Sauberer wäre es, es durchzureichen oder als Singleton zu kapseln.
- **`hasattr`/`setattr`/`delattr` ersetzen**: `shockshield`, `enemy`, `fourdirshoot`, `starttime`, `enemy_spawned_time`, `enemy_alive` werden dynamisch gesetzt. Stattdessen saubere Attribute mit Default `None` in `__init__`.
- **Auflösungsänderung ohne Neustart**: Aktuell gilt eine neue Auflösung erst nach Neustart, weil WIDTH/HEIGHT beim Import gesetzt werden. Lösbar durch `config.py`-Refactor.

### Bugs / Spiellogik

- **SQL-Injection in `scoreboard.py`**: `insert_name()` baut SQL per String-Concatenation. Fix: `c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (self.name, self.score))`.
- **Enemy-Laser-Kollision**: `spritecollide(self.enemy, self.lasers, False, ...)` — Player-Laser wird bei Treffer nicht gekillt (`dokill=False`). Wahrscheinlich unbeabsichtigt.

### Performance (noch offen)

- **Asteroid-Rotation**: Asteroiden rotieren jeden Frame (angle_speed ist immer ≠ 0). Rotationen auf feste Winkelschritte (z.B. 5°) einrasten → gecachte Surfaces wiederverwenden.
- **Asteroid-Skalierung beim Spawn**: Jeder neue Asteroid skaliert das gecachte Bild neu. Die drei Größen (size 7/8/9) könnten vorab als fertige Surfaces gecacht werden.
- **BgMove feste Scrollgeschwindigkeit**: `bg_ctr += 7` ist pixelbasiert, nicht auflösungsrelativ. Bei 4K scrollt der Hintergrund langsamer als bei 720p.

---

## Performance-Erkenntnisse

Benchmark (headless, 500 Frames, kein FPS-Cap):
- **Vorher** (original): ~500 FPS-equivalent
- **Nachher** (optimiert): ~850 FPS-equivalent (~70% schneller)

Hauptursachen des Ruckelns waren:
1. `pg.mixer.Sound(...)` bei **jeder** Kollision (Disk-I/O pro Frame) → jetzt gecacht
2. `pg.font.SysFont(...)` 60× pro Sekunde im HUD → jetzt gecacht
3. Pro Asteroid eine neue `pg.sprite.Group()` in der Kollisions-Schleife → `groupcollide` direkt
4. `Shockwave`-Surface war 1280×1280px → jetzt 720×720, nur Redraw bei Radiusänderung
5. `pg.transform.rotate` lief jedes Frame → jetzt nur bei Winkeländerung
6. `pg.mixer.music.unpause()` lief 60× pro Sekunde → jetzt nur nach ESC-Menü
