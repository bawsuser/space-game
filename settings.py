import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

# All common 16:9 resolutions up to 4K.
RESOLUTIONS = [
    (1280,  720),   # 0  HD
    (1600,  900),   # 1  HD+
    (1920, 1080),   # 2  Full HD
    (2560, 1440),   # 3  QHD
    (3840, 2160),   # 4  4K UHD
]
_MAX_RES = (3840, 2160)
_DEFAULTS = {'fullscreen': True, 'res_index': 0}


def _best_res_index(native_w, native_h):
    """Largest RESOLUTIONS entry that fits within (native_w, native_h), capped at 4K."""
    capped_w = min(native_w, _MAX_RES[0])
    capped_h = min(native_h, _MAX_RES[1])
    best = 0
    for i, (w, h) in enumerate(RESOLUTIONS):
        if w <= capped_w and h <= capped_h:
            best = i
    return best


def _detect_res_index(pg):
    """Detect native screen resolution and return the matching RESOLUTIONS index."""
    try:
        sizes = pg.display.get_desktop_sizes()
        if sizes:
            w, h = sizes[0]
            return _best_res_index(w, h)
    except Exception:
        pass
    return 0


def load(pg=None):
    """Load settings from disk.

    Pass pg (the pygame module) on first call so the native screen resolution
    can be auto-detected when no settings.json exists yet.
    """
    try:
        with open(_PATH) as f:
            d = json.load(f)
        d.setdefault('fullscreen', _DEFAULTS['fullscreen'])
        d.setdefault('res_index', _DEFAULTS['res_index'])
        d['res_index'] = max(0, min(int(d['res_index']), len(RESOLUTIONS) - 1))
        d['fullscreen'] = bool(d['fullscreen'])
        return d
    except Exception:
        # First run or corrupted file — detect native resolution if pg available
        d = dict(_DEFAULTS)
        if pg is not None:
            d['res_index'] = _detect_res_index(pg)
        return d


def save(data):
    with open(_PATH, 'w') as f:
        json.dump(data, f, indent=2)


def get_resolution(data=None):
    """Return (width, height) for the given settings dict (or load from disk)."""
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
