import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# All common 16:9 resolutions up to 4K. Index 0 is the default (720p = fast).
RESOLUTIONS = [
    (1280,  720),   # 0  HD
    (1600,  900),   # 1  HD+
    (1920, 1080),   # 2  Full HD
    (2560, 1440),   # 3  QHD
    (3840, 2160),   # 4  4K UHD
]
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


def get_resolution(data=None):
    """Return (width, height) for the current (or given) settings dict."""
    if data is None:
        data = load()
    return RESOLUTIONS[data['res_index']]


def make_display(pg, data=None):
    """Create (or recreate) the pygame display surface from settings."""
    if data is None:
        data = load()
    w, h = get_resolution(data)
    if data['fullscreen']:
        try:
            return pg.display.set_mode([w, h], pg.FULLSCREEN | pg.SCALED)
        except pg.error:
            pass  # fall through on headless / Wayland edge cases
    try:
        return pg.display.set_mode([w, h], pg.SCALED)
    except pg.error:
        return pg.display.set_mode([w, h])
