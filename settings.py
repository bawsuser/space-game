import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
RESOLUTIONS = [(1280, 720), (1920, 1080), (2560, 1440)]
_DEFAULTS = {'fullscreen': True, 'res_index': 0}


def load():
    try:
        with open(_PATH) as f:
            d = json.load(f)
        d.setdefault('fullscreen', _DEFAULTS['fullscreen'])
        d.setdefault('res_index', _DEFAULTS['res_index'])
        d['res_index'] = max(0, min(int(d['res_index']), len(RESOLUTIONS) - 1))
        d['fullscreen'] = bool(d['fullscreen'])
        return d
    except Exception:
        return dict(_DEFAULTS)


def save(data):
    with open(_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def make_display(pg):
    """Create (or recreate) the pygame display surface from saved settings."""
    d = load()
    w, h = RESOLUTIONS[d['res_index']]
    if d['fullscreen']:
        try:
            return pg.display.set_mode([1280, 720], pg.FULLSCREEN | pg.SCALED)
        except pg.error:
            pass  # fall through to windowed on headless / Wayland edge cases
    try:
        return pg.display.set_mode([w, h], pg.SCALED)
    except pg.error:
        return pg.display.set_mode([w, h])
